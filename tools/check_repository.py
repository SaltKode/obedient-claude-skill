#!/usr/bin/env python3
"""Offline artifact checks, not a Claude behavioral evaluation. Stdlib only."""
from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import unquote, urlsplit
import zipfile

from build_skill import check_archive, skill_entries

BUDGETS = {
    "instructions/CLAUDE.md": 6000,
    "instructions/CLAUDE-chat-preferences.txt": 5500,
    "skills/work-with-me/SKILL.md": 6000,
}


def check_frontmatter(text: str) -> None:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("SKILL.md needs opening frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise ValueError("SKILL.md needs closing frontmatter") from None
    fields = {}
    for line in lines[1:end]:
        key, separator, value = line.partition(": ")
        if not separator or key in fields:
            raise ValueError("Invalid or duplicate skill metadata")
        fields[key] = value
    if set(fields) != {"name", "description"} or fields["name"] != "work-with-me":
        raise ValueError("Portable metadata must contain only name and description")
    description = json.loads(fields["description"])
    if not isinstance(description, str) or not 1 <= len(description) <= 200:
        raise ValueError("Keep the description a quoted string of 1–200 characters")
    if not "\n".join(lines[end + 1:]).strip():
        raise ValueError("Missing skill body")


def safe_fixture_path(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and ".." not in path.parts and "\\" not in name and ":" not in name


def check_cases(data: dict) -> set[str]:
    cases, rubrics = data["cases"], data["rubrics"]
    ids = [case["id"] for case in cases]
    if len(ids) != len(set(ids)) or set(ids) != set(rubrics):
        raise ValueError("Case IDs must be unique and match the rubric IDs")
    for case in cases:
        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            raise ValueError(f"Missing prompt for {case['id']}")
        for key in ("files", "operator_only_files"):
            for name, content in case.get(key, {}).items():
                if not safe_fixture_path(name) or not isinstance(content, str):
                    raise ValueError(f"Unsafe or invalid fixture in {case['id']}: {name}")
        rubric = rubrics[case["id"]]
        if not rubric.get("pass") or not rubric.get("critical_fail"):
            raise ValueError(f"Incomplete rubric for {case['id']}")
    return set(ids)


def check_links(root: Path) -> None:
    root = root.resolve()
    for source in root.rglob("*.md"):
        if ".git" in source.relative_to(root).parts:
            continue
        text = source.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]\n]*\]\(([^\s)]+)\)", text):
            url = urlsplit(target)
            if url.scheme or url.netloc or not url.path:
                continue
            resolved = (source.parent / unquote(url.path)).resolve()
            if not resolved.is_relative_to(root) or not resolved.exists():
                raise ValueError(f"Broken local link in {source.relative_to(root)}: {target}")


def check_budgets(root: Path) -> dict[str, int]:
    sizes = {}
    for name, limit in BUDGETS.items():
        data = (root / name).read_bytes()
        data.decode("utf-8")
        if len(data) > limit:
            raise ValueError(f"Instruction size requires review: {name} ({len(data)} > {limit} bytes)")
        sizes[name] = len(data)
    return sizes


def validate(root: Path) -> None:
    check_frontmatter((root / "skills/work-with-me/SKILL.md").read_text(encoding="utf-8"))
    sizes = check_budgets(root)
    ids = set()
    for name in ("cases.json", "focus-cases.json"):
        found = check_cases(json.loads((root / "evaluation" / name).read_text(encoding="utf-8")))
        if ids.intersection(found):
            raise ValueError("Duplicate case IDs across evaluation suites")
        ids.update(found)
    check_links(root)
    entries = skill_entries(root)
    if entries.get("work-with-me/LICENSE") != (root / "LICENSE").read_bytes():
        raise ValueError("Skill distribution must include the repository license unchanged")
    check_archive(root / "work-with-me.zip", entries)
    print(f"PASS: metadata, local file links, {len(ids)} case/rubric pairs, license, and {len(entries)} ZIP entries.")
    for name, size in sizes.items():
        print(f"{name}: {size} UTF-8 bytes (not a token measurement)")


def main() -> int:
    try:
        validate(Path(__file__).resolve().parent.parent)
        return 0
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
