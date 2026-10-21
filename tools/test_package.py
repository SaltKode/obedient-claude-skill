#!/usr/bin/env python3
"""Package/checker tests in isolated temporary directories; no model calls."""
from __future__ import annotations

import copy
import io
from pathlib import Path
import tempfile
import unittest
import warnings
import zipfile

from build_skill import archive_bytes, check_archive, skill_entries
from check_repository import BUDGETS, check_budgets, check_cases, check_frontmatter, check_links

HEADER = '---\nname: work-with-me\ndescription: "A focused working routine."\n---\n# Work\n'


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.skill = self.root / "skills/work-with-me"
        self.skill.mkdir(parents=True)
        (self.skill / "SKILL.md").write_text(HEADER, encoding="utf-8")
        (self.skill / "references").mkdir()
        (self.skill / "references/test.md").write_text("# Reference\n", encoding="utf-8")
        self.archive = self.root / "work-with-me.zip"

    def build(self):
        entries = skill_entries(self.root)
        self.archive.write_bytes(archive_bytes(entries))
        return entries

    def test_roundtrip_is_stable_and_matches_source(self):
        entries = self.build()
        first = self.archive.read_bytes()
        self.assertEqual(first, archive_bytes(dict(reversed(list(entries.items())))))
        check_archive(self.archive, entries)

    def test_stale_entry_is_rejected(self):
        entries = self.build()
        entries["work-with-me/SKILL.md"] += b"Changed\n"
        with self.assertRaisesRegex(ValueError, "Stale"):
            check_archive(self.archive, entries)

    def test_extra_and_duplicate_entries_are_rejected(self):
        for name in ("../outside.txt", "work-with-me/SKILL.md"):
            with self.subTest(name=name):
                entries = self.build()
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    with zipfile.ZipFile(self.archive, "a") as archive:
                        archive.writestr(name, b"unexpected")
                with self.assertRaisesRegex(ValueError, "membership"):
                    check_archive(self.archive, entries)

    def test_missing_skill_is_rejected(self):
        (self.skill / "SKILL.md").unlink()
        with self.assertRaisesRegex(ValueError, "Missing"):
            skill_entries(self.root)

    def test_hidden_content_is_rejected(self):
        (self.skill / ".private").write_text("do not package", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "hidden"):
            skill_entries(self.root)

    def test_symlink_content_is_rejected(self):
        try:
            (self.skill / "linked.md").symlink_to(self.skill / "SKILL.md")
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unavailable for this account")
        with self.assertRaisesRegex(ValueError, "linked"):
            skill_entries(self.root)

    def test_frontmatter_accepts_portable_subset_and_rejects_duplicates(self):
        check_frontmatter(HEADER)
        for bad in (HEADER.replace('name: work-with-me', 'name: other'), HEADER.replace('description:', 'name: work-with-me\ndescription:'), HEADER.replace('---\n# Work', 'allowed-tools: Bash\n---\n# Work')):
            with self.subTest(header=bad[:60]), self.assertRaises(ValueError):
                check_frontmatter(bad)

    def test_long_description_is_rejected(self):
        with self.assertRaises(ValueError):
            check_frontmatter(HEADER.replace("A focused working routine.", "x" * 1025))
        check_frontmatter(HEADER.replace("A focused working routine.", "x" * 1024))
        with self.assertRaises(ValueError):
            check_frontmatter(HEADER.replace("A focused working routine.", "   "))

    def test_links_reject_missing_or_escaping_targets(self):
        readme = self.root / "README.md"
        readme.write_text("[skill](skills/work-with-me/SKILL.md) [web](https://example.com)\n", encoding="utf-8")
        check_links(self.root)
        for target in ("absent.md", "../outside.md"):
            readme.write_text(f"[bad]({target})\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Broken"):
                check_links(self.root)

    def test_case_ids_and_fixture_paths_are_checked(self):
        good = {"cases": [{"id": "C99", "prompt": "Fix it", "files": {"app.py": "x = 1\n"}}], "rubrics": {"C99": {"pass": ["works"], "critical_fail": ["fabrication"]}}}
        self.assertEqual(check_cases(good), {"C99"})
        for name in ("../outside.py", "/absolute.py", "C:\\outside.py"):
            bad = copy.deepcopy(good)
            bad["cases"][0]["files"] = {name: "x"}
            with self.assertRaises(ValueError):
                check_cases(bad)
        bad = copy.deepcopy(good)
        bad["cases"].append(copy.deepcopy(bad["cases"][0]))
        with self.assertRaises(ValueError):
            check_cases(bad)
        bad = copy.deepcopy(good)
        bad["rubrics"] = {}
        with self.assertRaises(ValueError):
            check_cases(bad)

    def test_instruction_budget_is_bytes_not_an_estimated_token_count(self):
        for name, limit in BUDGETS.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"x" * limit)
        sizes = check_budgets(self.root)
        self.assertEqual(sizes, BUDGETS)
        (self.root / "instructions/CLAUDE.md").write_bytes(b"x" * (BUDGETS["instructions/CLAUDE.md"] + 1))
        with self.assertRaisesRegex(ValueError, "size"):
            check_budgets(self.root)


if __name__ == "__main__":
    unittest.main(verbosity=2)
