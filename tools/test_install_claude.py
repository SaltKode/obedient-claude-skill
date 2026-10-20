#!/usr/bin/env python3
"""Meaningful installer checks. All destinations live in temporary directories."""

from contextlib import redirect_stderr, redirect_stdout
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import install_claude as installer


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        # Some operating systems put the temporary directory behind a symlink.
        # Use the actual fixture path; installer inputs deliberately containing
        # symlinks are exercised separately below.
        self.root = Path(os.path.realpath(self.temporary.name))
        self.kit = self.root / "kit"
        self.config = self.root / "destination" / ".claude"
        (self.kit / "instructions").mkdir(parents=True)
        self.source_core = self.kit / "instructions" / "CLAUDE.md"
        self.source_core.write_bytes(b"# Work with me\nComplete authorized work.\n")
        self.source_skill = self.kit / "skills" / "work-with-me"
        (self.source_skill / "references").mkdir(parents=True)
        (self.source_skill / "SKILL.md").write_bytes(b"---\nname: work-with-me\ndescription: Work collaboratively.\n---\n# Work with me\n")
        (self.source_skill / "references" / "coding.md").write_bytes(b"Inspect existing code first.\n")

    def plan(self, update=False):
        return installer.build_plan(self.kit, self.config, update)

    def apply(self, update=False):
        return installer.apply_plan(self.plan(update))

    def snapshot(self, path):
        if not path.exists():
            return None
        return {item.relative_to(path).as_posix(): item.read_bytes() for item in path.rglob("*") if item.is_file()}

    def test_dry_run_creates_nothing(self):
        before = self.snapshot(self.root)
        output = io.StringIO()
        with redirect_stdout(output):
            result = installer.main(["--config-dir", str(self.config)], kit_dir=self.kit)
        self.assertEqual(result, 0)
        self.assertIn("DRY RUN", output.getvalue())
        self.assertFalse(self.config.parent.exists())
        self.assertEqual(self.snapshot(self.root), before)

    def test_fresh_install_and_repeat_are_idempotent(self):
        self.assertIsNone(self.apply())
        core = self.config / "CLAUDE.md"
        self.assertIn(installer.BEGIN, core.read_bytes())
        self.assertEqual((self.config / "skills" / "work-with-me" / installer.OWNER_FILE).read_bytes(), installer.OWNER_BYTES)
        before = self.snapshot(self.config)
        modified = core.stat().st_mtime_ns
        self.assertFalse(self.plan().changed)
        self.assertIsNone(self.apply())
        self.assertEqual(self.snapshot(self.config), before)
        self.assertEqual(core.stat().st_mtime_ns, modified)
        self.assertFalse((self.config / "work-with-me-backups").exists())

    def test_existing_utf8_bom_crlf_and_settings_are_preserved(self):
        self.config.mkdir(parents=True)
        original = installer.BOM + "# Mina regler\r\nBehåll räckvidden.\r\n".encode("utf-8")
        (self.config / "CLAUDE.md").write_bytes(original)
        settings = b'{"permissions":{"deny":["Bash(rm *)"]}}\n'
        (self.config / "settings.json").write_bytes(settings)
        backup = self.apply()
        installed = (self.config / "CLAUDE.md").read_bytes()
        self.assertTrue(installed.startswith(original))
        self.assertNotIn(b"\n", installed.replace(b"\r\n", b""))
        self.assertEqual(installed.count(installer.BOM), 1)
        self.assertEqual((backup / "CLAUDE.md").read_bytes(), original)
        self.assertEqual((self.config / "settings.json").read_bytes(), settings)

    def test_update_preserves_exact_bytes_outside_managed_block(self):
        self.apply()
        core = self.config / "CLAUDE.md"
        prefix = installer.BOM + b"# Existing\nKeep this  \n\n"
        suffix = b"\n\n# Following\r\nKeep trailing bytes\t"
        managed = core.read_bytes().rstrip(b"\n")
        original = prefix + managed + suffix
        core.write_bytes(original)
        self.source_core.write_bytes(b"# Work with me\nUpdated behavior.\n")
        with self.assertRaises(installer.InstallError):
            self.plan()
        backup = self.apply(update=True)
        updated = core.read_bytes()
        self.assertTrue(updated.startswith(prefix))
        self.assertTrue(updated.endswith(suffix))
        self.assertIn(b"Updated behavior.", updated)
        self.assertEqual((backup / "CLAUDE.md").read_bytes(), original)
        self.assertFalse(self.plan().changed)

    def test_unowned_skill_collision_refuses_even_update(self):
        target = self.config / "skills" / "work-with-me"
        target.mkdir(parents=True)
        (target / "SKILL.md").write_bytes((self.source_skill / "SKILL.md").read_bytes())
        before = self.snapshot(self.config)
        for update in (False, True):
            with self.assertRaisesRegex(installer.InstallError, "not owned"):
                self.plan(update)
        self.assertEqual(self.snapshot(self.config), before)
        self.assertFalse((self.config / "CLAUDE.md").exists())

    def test_owned_skill_update_backs_up_complete_previous_tree(self):
        self.apply()
        target = self.config / "skills" / "work-with-me"
        (target / "local-note.txt").write_bytes(b"Preserve in backup.\n")
        before = self.snapshot(target)
        (self.source_skill / "references" / "coding.md").write_bytes(b"New procedure.\n")
        with self.assertRaisesRegex(installer.InstallError, "installed skill differs"):
            self.plan()
        backup = self.apply(update=True)
        self.assertEqual(self.snapshot(backup / "skills" / "work-with-me"), before)
        self.assertEqual((target / "references" / "coding.md").read_bytes(), b"New procedure.\n")
        self.assertFalse((target / "local-note.txt").exists())
        self.assertFalse(self.plan().changed)

    def test_invalid_markers_or_encoding_fail_before_writes(self):
        self.config.mkdir(parents=True)
        cases = (
            installer.BEGIN + b"\nMissing end\n",
            installer.END + b"\n" + installer.BEGIN + b"\n",
            installer.BEGIN + b"\nA\n" + installer.END + b"\n" + installer.BEGIN + b"\nB\n" + installer.END,
            b"<!-- BEGIN WORK-WITH-ME v2 -->\nA\n<!-- END WORK-WITH-ME v2 -->\n",
            b"prefix " + installer.BEGIN + b"\nA\n" + installer.END,
            installer.BEGIN + b"\nA " + installer.END + b"\n",
            b"\xff\xfeU\x00T\x00F\x00",
            b"U\x00T\x00F\x00",
            b"Lone\rCR\r",
        )
        for content in cases:
            with self.subTest(content=content[:30]):
                (self.config / "CLAUDE.md").write_bytes(content)
                before = self.snapshot(self.config)
                with self.assertRaises(installer.InstallError):
                    self.plan(update=True)
                self.assertEqual(self.snapshot(self.config), before)

    def test_missing_source_fails_without_destination_creation(self):
        self.source_core.unlink()
        with self.assertRaises(OSError):
            self.plan()
        self.assertFalse(self.config.parent.exists())

    def test_source_and_destination_symlinks_are_refused(self):
        if not hasattr(os, "symlink"):
            self.skipTest("Symlinks unavailable")
        external = self.root / "external"
        external.mkdir()
        link = self.root / "linked"
        try:
            link.symlink_to(external, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation unavailable for this account")
        with self.assertRaisesRegex(installer.InstallError, "symlink"):
            installer.build_plan(self.kit, link / ".claude")
        source_link = self.source_skill / "linked-file"
        (external / "file").write_bytes(b"outside")
        source_link.symlink_to(external / "file")
        with self.assertRaisesRegex(installer.InstallError, "symlink"):
            self.plan()
        source_link.unlink()
        self.config.mkdir(parents=True)
        (self.config / "CLAUDE.md").symlink_to(external / "file")
        with self.assertRaisesRegex(installer.InstallError, "symlink"):
            self.plan()
        self.assertEqual((external / "file").read_bytes(), b"outside")

    def test_relative_destination_is_rejected(self):
        with self.assertRaisesRegex(installer.InstallError, "absolute"):
            installer.build_plan(self.kit, Path("relative/.claude"))

    def test_changed_destination_after_plan_is_rejected(self):
        self.apply()
        self.source_core.write_bytes(b"New instructions.\n")
        plan = self.plan(update=True)
        core = self.config / "CLAUDE.md"
        changed = core.read_bytes() + b"User edit after planning.\n"
        core.write_bytes(changed)
        with self.assertRaisesRegex(installer.InstallError, "changed after validation"):
            installer.apply_plan(plan)
        self.assertEqual(core.read_bytes(), changed)
        self.assertFalse((self.config / "work-with-me-backups").exists())

    def test_commit_failure_restores_existing_core_and_skill(self):
        self.apply()
        before = self.snapshot(self.config)
        self.source_core.write_bytes(b"New instructions.\n")
        (self.source_skill / "references" / "coding.md").write_bytes(b"New code process.\n")
        plan = self.plan(update=True)
        original_replace = os.replace

        def fail_new_skill(source, destination):
            if Path(source).name == "new-skill":
                raise OSError("Injected install failure")
            return original_replace(source, destination)

        with patch.object(installer.os, "replace", side_effect=fail_new_skill):
            with self.assertRaisesRegex(installer.InstallError, "contents restored"):
                installer.apply_plan(plan)
        self.assertEqual(self.snapshot(self.config), before)
        self.assertFalse(any(self.config.glob(".work-with-me-tmp-*")))

    def test_fresh_install_failure_removes_new_destination(self):
        plan = self.plan()
        original_replace = os.replace

        def fail_new_skill(source, destination):
            if Path(source).name == "new-skill":
                raise OSError("Injected install failure")
            return original_replace(source, destination)

        with patch.object(installer.os, "replace", side_effect=fail_new_skill):
            with self.assertRaises(installer.InstallError):
                installer.apply_plan(plan)
        self.assertFalse(self.config.parent.exists())

    def test_backup_failure_leaves_both_existing_targets_unchanged(self):
        self.apply()
        before = self.snapshot(self.config)
        self.source_core.write_bytes(b"New instructions.\n")
        plan = self.plan(update=True)
        original_write = installer._write_file

        def fail_backup(path, record):
            if "work-with-me-backups" in path.parts:
                raise OSError("Injected backup failure")
            return original_write(path, record)

        with patch.object(installer, "_write_file", side_effect=fail_backup):
            with self.assertRaisesRegex(installer.InstallError, "contents restored"):
                installer.apply_plan(plan)
        self.assertEqual(self.snapshot(self.config), before)
        self.assertFalse((self.config / "work-with-me-backups").exists())

    def test_cli_errors_are_nonzero_and_do_not_echo_file_content(self):
        self.config.mkdir(parents=True)
        secret = b"unrelated private text " + installer.BEGIN
        (self.config / "CLAUDE.md").write_bytes(secret)
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            result = installer.main(["--config-dir", str(self.config), "--apply"], kit_dir=self.kit)
        self.assertEqual(result, 1)
        self.assertNotIn("private text", stdout.getvalue() + stderr.getvalue())
        self.assertEqual((self.config / "CLAUDE.md").read_bytes(), secret)


if __name__ == "__main__":
    unittest.main(verbosity=2)
