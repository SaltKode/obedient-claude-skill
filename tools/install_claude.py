#!/usr/bin/env python3
"""Install this kit into Claude Code. Dry-run by default; Python stdlib only.

Only CLAUDE.md's marked block and skills/work-with-me are managed. Existing
UTF-8 instructions (including a BOM, LF, or CRLF) are preserved outside that
block. Other encodings and lone-CR line endings are rejected before writes.
Do not run this installer concurrently with another writer to those paths.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import stat
import sys
import uuid


BEGIN = b"<!-- BEGIN WORK-WITH-ME v1 -->"
END = b"<!-- END WORK-WITH-ME v1 -->"
OWNER_FILE = ".work-with-me-owned"
OWNER_BYTES = b"work-with-me installer ownership v1\n"
BOM = b"\xef\xbb\xbf"


class InstallError(Exception):
    """A configuration or validation problem with a safe, actionable message."""


@dataclass(frozen=True)
class FileRecord:
    data: bytes
    mode: int


@dataclass
class Tree:
    files: dict[str, FileRecord]
    directories: dict[str, int]


@dataclass
class Plan:
    config: Path
    original_core: FileRecord | None
    original_skill: Tree | None
    desired_core: bytes
    desired_skill: Tree
    core_action: str
    skill_action: str

    @property
    def changed(self) -> bool:
        return self.core_action != "unchanged" or self.skill_action != "unchanged"


def _check_stat(path: Path, info: os.stat_result) -> None:
    reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & reparse:
        raise InstallError(f"Refusing symlink, junction, or reparse-point path: {path}")


def check_path(path: Path, kind: str | None = None) -> None:
    """Inspect each existing ancestor without resolving away links."""
    if not path.is_absolute() or ".." in path.parts:
        raise InstallError(f"Use an absolute path without '..': {path}")
    for candidate in (*reversed(path.parents), path):
        try:
            info = candidate.lstat()
        except FileNotFoundError:
            continue
        _check_stat(candidate, info)
        expected = "directory" if candidate != path else kind
        if expected == "directory" and not stat.S_ISDIR(info.st_mode):
            raise InstallError(f"Expected a directory: {candidate}")
        if expected == "file" and not stat.S_ISREG(info.st_mode):
            raise InstallError(f"Expected a regular file: {candidate}")


def read_file(path: Path) -> FileRecord:
    check_path(path, "file")
    info = path.lstat()
    return FileRecord(path.read_bytes(), stat.S_IMODE(info.st_mode))


def read_optional_file(path: Path) -> FileRecord | None:
    check_path(path, "file")
    return read_file(path) if path.exists() else None


def read_tree(root: Path) -> Tree:
    check_path(root, "directory")
    files: dict[str, FileRecord] = {}
    directories: dict[str, int] = {}

    def visit(directory: Path) -> None:
        directories[directory.relative_to(root).as_posix()] = stat.S_IMODE(directory.lstat().st_mode)
        for child in sorted(directory.iterdir()):
            info = child.lstat()
            _check_stat(child, info)
            if stat.S_ISDIR(info.st_mode):
                visit(child)
            elif stat.S_ISREG(info.st_mode):
                files[child.relative_to(root).as_posix()] = FileRecord(child.read_bytes(), stat.S_IMODE(info.st_mode))
            else:
                raise InstallError(f"Refusing non-regular file in skill: {child}")

    visit(root)
    return Tree(files, directories)


def same_content(left: Tree, right: Tree) -> bool:
    return (
        left.directories.keys() == right.directories.keys()
        and {key: value.data for key, value in left.files.items()}
        == {key: value.data for key, value in right.files.items()}
    )


def _validate_text(data: bytes, label: str) -> None:
    try:
        data.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise InstallError(f"{label} must be UTF-8 (a UTF-8 BOM is supported); no files changed.") from None
    if b"\x00" in data:
        raise InstallError(f"{label} contains NUL bytes; provide a UTF-8 Markdown text file first.")
    if b"\r" in data.replace(b"\r\n", b""):
        raise InstallError(f"{label} uses lone-CR line endings; convert to LF or CRLF first.")


def _managed_span(data: bytes) -> tuple[int, int] | None:
    begins = data.count(b"<!-- BEGIN WORK-WITH-ME")
    ends = data.count(b"<!-- END WORK-WITH-ME")
    if begins == ends == 0:
        return None
    if begins != 1 or ends != 1 or data.count(BEGIN) != 1 or data.count(END) != 1:
        raise InstallError("CLAUDE.md has conflicting, duplicate, or unsupported WORK-WITH-ME markers.")
    start = data.index(BEGIN)
    end_start = data.index(END)
    finish = end_start + len(END)
    prefix, suffix = data[:start], data[finish:]
    after_begin = data[start + len(BEGIN):]
    if (
        finish <= start
        or end_start == 0
        or data[end_start - 1:end_start] != b"\n"
        or (prefix and prefix != BOM and not prefix.endswith(b"\n"))
        or not after_begin.startswith((b"\n", b"\r\n"))
        or (suffix and not suffix.startswith((b"\n", b"\r\n")))
    ):
        raise InstallError("WORK-WITH-ME markers must be ordered, complete, and on their own lines.")
    return start, finish


def desired_core(existing: FileRecord | None, source: bytes, update: bool) -> tuple[bytes, str]:
    _validate_text(source, "The kit's instructions/CLAUDE.md")
    source = source.removeprefix(BOM).replace(b"\r\n", b"\n").rstrip(b"\n")
    if not source.strip() or b"<!-- BEGIN WORK-WITH-ME" in source or b"<!-- END WORK-WITH-ME" in source:
        raise InstallError("The kit's instruction source is empty or contains reserved managed markers.")
    original = existing.data if existing else b""
    _validate_text(original, "Existing CLAUDE.md")
    newline = b"\r\n" if b"\r\n" in original and original.count(b"\n") == original.count(b"\r\n") else b"\n"
    block = BEGIN + newline + source.replace(b"\n", newline) + newline + END
    span = _managed_span(original)
    if span is not None:
        start, finish = span
        replacement = original[:start] + block + original[finish:]
        if replacement == original:
            return original, "unchanged"
        if not update:
            raise InstallError("The managed CLAUDE.md block differs. Review the kit, then use --apply --update to back up and replace it.")
        return replacement, "update managed block"
    payload = original.removeprefix(BOM)
    separator = (newline if original.endswith(b"\n") else newline * 2) if payload else b""
    return original + separator + block + newline, "append managed block" if existing else "create"


def build_plan(kit: Path, config: Path, update: bool = False) -> Plan:
    check_path(kit, "directory")
    check_path(config, "directory")
    check_path(config / "skills", "directory")
    check_path(config / "work-with-me-backups", "directory")
    core = read_optional_file(config / "CLAUDE.md")
    wanted_core, core_action = desired_core(core, read_file(kit / "instructions" / "CLAUDE.md").data, update)
    source = read_tree(kit / "skills" / "work-with-me")
    if "SKILL.md" not in source.files or OWNER_FILE in source.files or OWNER_FILE in source.directories:
        raise InstallError("Skill source must contain SKILL.md and must not contain an installer ownership marker.")
    wanted_skill = Tree({**source.files, OWNER_FILE: FileRecord(OWNER_BYTES, 0o600)}, dict(source.directories))
    destination = config / "skills" / "work-with-me"
    check_path(destination, "directory")
    current = read_tree(destination) if destination.exists() else None
    skill_action = "create"
    if current is not None:
        owner = current.files.get(OWNER_FILE)
        if owner is None or owner.data != OWNER_BYTES:
            raise InstallError(f"Existing skill is not owned by this installer: {destination}. --update cannot replace it; choose another config directory or move it yourself.")
        skill_action = "unchanged" if same_content(current, wanted_skill) else "update owned skill"
        if skill_action != "unchanged" and not update:
            raise InstallError("The installed skill differs. Review the kit, then use --apply --update to back up and replace it.")
    return Plan(config, core, current, wanted_core, wanted_skill, core_action, skill_action)


def _ensure_directory(path: Path, created: list[Path]) -> None:
    check_path(path, "directory")
    if path.exists():
        return
    _ensure_directory(path.parent, created)
    path.mkdir(mode=0o700)
    created.append(path)


def _write_file(path: Path, record: FileRecord) -> None:
    with path.open("xb") as handle:
        handle.write(record.data)
    path.chmod(record.mode)


def _write_tree(root: Path, tree: Tree) -> None:
    root.mkdir(mode=0o700)
    for name in sorted(tree.directories, key=lambda value: (value.count("/"), value)):
        if name != ".":
            (root / name).mkdir(mode=0o700)
    for name, record in tree.files.items():
        _write_file(root / name, record)
    for name in sorted(tree.directories, key=lambda value: (value.count("/"), value), reverse=True):
        (root / name).chmod(tree.directories[name])


def _verify_unchanged(plan: Plan) -> None:
    check_path(plan.config, "directory")
    if read_optional_file(plan.config / "CLAUDE.md") != plan.original_core:
        raise InstallError("CLAUDE.md changed after validation. Run the installer again.")
    target = plan.config / "skills" / "work-with-me"
    check_path(target, "directory")
    current = read_tree(target) if target.exists() else None
    if current != plan.original_skill:
        raise InstallError("The skill changed after validation. Run the installer again.")


def apply_plan(plan: Plan) -> Path | None:
    """Stage and back up before replacements; restore both targets on failure."""
    if not plan.changed:
        return None
    _verify_unchanged(plan)
    created: list[Path] = []
    transaction: Path | None = None
    backup: Path | None = None
    core_replaced = old_skill_moved = skill_installed = False
    core_path = plan.config / "CLAUDE.md"
    skill_path = plan.config / "skills" / "work-with-me"
    change_core = plan.core_action != "unchanged"
    change_skill = plan.skill_action != "unchanged"
    try:
        _ensure_directory(plan.config, created)
        transaction = plan.config / (".work-with-me-tmp-" + uuid.uuid4().hex)
        transaction.mkdir(mode=0o700)
        if change_core:
            mode = plan.original_core.mode if plan.original_core else 0o600
            _write_file(transaction / "new-core", FileRecord(plan.desired_core, mode))
            if plan.original_core is not None:
                _write_file(transaction / "old-core", plan.original_core)
        if change_skill:
            _ensure_directory(skill_path.parent, created)
            _write_tree(transaction / "new-skill", plan.desired_skill)
        if (change_core and plan.original_core is not None) or (change_skill and plan.original_skill is not None):
            backup_root = plan.config / "work-with-me-backups"
            _ensure_directory(backup_root, created)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
            backup = backup_root / (stamp + "-" + uuid.uuid4().hex[:8])
            backup.mkdir(mode=0o700)
            if change_core and plan.original_core is not None:
                _write_file(backup / "CLAUDE.md", plan.original_core)
            if change_skill and plan.original_skill is not None:
                (backup / "skills").mkdir(mode=0o700)
                _write_tree(backup / "skills" / "work-with-me", plan.original_skill)
        _verify_unchanged(plan)
        if change_core:
            check_path(core_path, "file")
            os.replace(transaction / "new-core", core_path)
            core_replaced = True
        if change_skill:
            check_path(skill_path, "directory")
            if plan.original_skill is not None:
                os.replace(skill_path, transaction / "old-skill")
                old_skill_moved = True
            os.replace(transaction / "new-skill", skill_path)
            skill_installed = True
    except (OSError, InstallError) as exc:
        rollback_errors: list[str] = []
        if transaction is not None:
            try:
                if skill_installed:
                    check_path(skill_path, "directory")
                    os.replace(skill_path, transaction / "failed-skill")
                if old_skill_moved:
                    check_path(skill_path, "directory")
                    os.replace(transaction / "old-skill", skill_path)
            except OSError as rollback_error:
                rollback_errors.append(str(rollback_error))
            except InstallError as rollback_error:
                rollback_errors.append(str(rollback_error))
            try:
                if core_replaced:
                    check_path(core_path, "file")
                    if plan.original_core is not None:
                        os.replace(transaction / "old-core", core_path)
                    else:
                        core_path.unlink()
            except (OSError, InstallError) as rollback_error:
                rollback_errors.append(str(rollback_error))
        if rollback_errors:
            raise InstallError(f"Installation failed and rollback was incomplete. Recovery files: {transaction}; backup: {backup}. Cause: {exc}. Rollback: {'; '.join(rollback_errors)}") from exc
        cleanup_errors: list[str] = []
        for temporary_path in (transaction, backup):
            if temporary_path is not None and temporary_path.exists():
                try:
                    shutil.rmtree(temporary_path)
                except OSError as cleanup_error:
                    cleanup_errors.append(f"{temporary_path}: {cleanup_error}")
        for directory in reversed(created):
            try:
                directory.rmdir()
            except OSError:
                pass
        if cleanup_errors:
            raise InstallError(f"Installation failed; previous instruction and skill contents restored, but cleanup was incomplete: {'; '.join(cleanup_errors)}. Cause: {exc}") from exc
        raise InstallError(f"Installation failed; previous instruction and skill contents restored. Cause: {exc}") from exc
    if transaction is not None:
        try:
            shutil.rmtree(transaction)
        except OSError as exc:
            raise InstallError(f"Installation completed, but temporary files could not be removed: {transaction}. Installed files and backups remain in place. Cause: {exc}") from exc
    return backup


def main(argv: list[str] | None = None, *, kit_dir: Path | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config-dir", type=Path, default=Path.home() / ".claude", metavar="ABSOLUTE_PATH", help="Claude Code configuration directory (default: ~/.claude)")
    parser.add_argument("--apply", action="store_true", help="Apply the reviewed plan; otherwise perform a read-only dry-run")
    parser.add_argument("--update", action="store_true", help="Allow backup and replacement of this installer's existing block and owned skill")
    args = parser.parse_args(argv)
    kit = kit_dir if kit_dir is not None else Path(__file__).absolute().parent.parent
    try:
        plan = build_plan(kit, args.config_dir, args.update)
        print("APPLY" if args.apply else "DRY RUN — no files will be written")
        print(f"Configuration: {plan.config}")
        print(f"CLAUDE.md: {plan.core_action}")
        print(f"skills/work-with-me: {plan.skill_action}")
        if not plan.changed:
            print("Already matches this kit; nothing to do.")
        elif args.apply:
            backup = apply_plan(plan)
            print("Installed. Restart Claude Code, check /context, then invoke /work-with-me.")
            if backup is not None:
                print(f"Originals backed up to: {backup}")
        else:
            print("Review the instruction files, then repeat with --apply to install.")
        return 0
    except (OSError, InstallError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
