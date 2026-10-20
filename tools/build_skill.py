#!/usr/bin/env python3
"""Build or check the skill-only ZIP. Python 3.10+, standard library only."""
from __future__ import annotations

import argparse
import io
import os
from pathlib import Path
import stat
import tempfile
import zipfile

STAMP = (2020, 1, 1, 0, 0, 0)
MAX_BYTES = 2_000_000


def skill_entries(root: Path) -> dict[str, bytes]:
    source = root / "skills" / "work-with-me"
    if source.is_symlink() or not source.is_dir():
        raise ValueError("Expected a real skills/work-with-me directory")
    entries = {}
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        if path.is_symlink():
            raise ValueError(f"Refusing linked skill content: {relative}")
        if any(part.startswith(".") for part in relative.parts):
            raise ValueError(f"Unexpected hidden skill content: {relative}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError(f"Not a regular skill file: {relative}")
        entries["work-with-me/" + relative.as_posix()] = path.read_bytes()
    if "work-with-me/SKILL.md" not in entries:
        raise ValueError("Missing SKILL.md")
    if sum(map(len, entries.values())) > MAX_BYTES:
        raise ValueError("Skill exceeds the package size review limit")
    return entries


def archive_bytes(entries: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(entries.items()):
            info = zipfile.ZipInfo(name, date_time=STAMP)
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return output.getvalue()


def check_archive(path: Path, entries: dict[str, bytes]) -> None:
    if path.is_symlink():
        raise ValueError("Refusing a linked archive")
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != set(entries):
            raise ValueError("Archive membership differs from skill source")
        if sum(info.file_size for info in archive.infolist()) > MAX_BYTES:
            raise ValueError("Archive exceeds the uncompressed size review limit")
        for info in archive.infolist():
            if info.date_time != STAMP or info.is_dir():
                raise ValueError(f"Unexpected archive metadata: {info.filename}")
            if archive.read(info) != entries[info.filename]:
                raise ValueError(f"Stale archive entry: {info.filename}")
        if archive.testzip() is not None:
            raise ValueError("Archive CRC check failed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check without modifying the archive")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    destination = root / "work-with-me.zip"
    temporary = None
    try:
        entries = skill_entries(root)
        if not args.check:
            if destination.is_symlink():
                raise ValueError("Refusing to replace a linked archive")
            with tempfile.NamedTemporaryFile(dir=root, prefix=".skill-zip-", delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(archive_bytes(entries))
            os.replace(temporary, destination)
            temporary = None
        check_archive(destination, entries)
        print(f"Skill ZIP matches {len(entries)} source files; contents and integrity verified.")
        return 0
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}")
        return 1
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
