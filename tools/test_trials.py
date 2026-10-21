"""Offline harness tests. Fake processes and traces, never a Claude/API call."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import run_trials as runner
from trial_evidence import changes, parse_trace, snapshot


class TrialTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.suite = self.root / "suite.json"
        self.case = {"id": "C99", "runner_compatible": True, "prompt": "Fix this", "files": {"app.py": "value = 1\n"}}
        self.suite.write_text(json.dumps({"mode": "behavior", "cases": [self.case], "rubrics": {"C99": {"pass": ["SECRET_GRADING_TARGET"], "critical_fail": ["fabrication"]}}}), encoding="utf-8")
        self.args = runner.parser().parse_args(["--suite", str(self.suite), "--cases", "C99", "--baseline-ref", "old", "--model", "test-exact-model", "--effort", "high", "--budget-usd", "0.50", "--max-total-usd", "1", "--max-turns", "8", "--timeout", "30"])
        self.instructions = {"CLAUDE.md": b"Working agreement\n", ".claude/skills/work-with-me/SKILL.md": b"Skill\n"}

    def run_fixture(self):
        with patch.object(runner, "resolve_ref", side_effect=lambda repo, ref: "a" * 40 if ref == "old" else "b" * 40), patch.object(runner, "instruction_snapshot", return_value=self.instructions):
            return runner.run(self.args, self.repo)

    def trace(self, events):
        path = self.root / "trace.jsonl"
        path.write_text("\n".join(json.dumps(event) for event in events) + "\n", encoding="utf-8")
        return path

    def test_default_plan_neither_writes_nor_runs_model(self):
        self.args.output = self.root / "new-output"
        with patch.object(runner, "capture") as capture:
            report = self.run_fixture()
        capture.assert_not_called()
        self.assertFalse(self.args.output.exists())
        self.assertEqual(len(report["plan"]), 2)
        self.assertEqual(report["nominal_budget_usd"], "1.00")

    def test_prepare_keeps_rubrics_out_and_fixtures_identical(self):
        self.args.prepare = True
        self.args.output = self.root / "prepared"
        self.run_fixture()
        left = self.args.output / "trial-001/workspace"
        right = self.args.output / "trial-002/workspace"
        self.assertEqual((left / "app.py").read_bytes(), (right / "app.py").read_bytes())
        self.assertEqual((left / "CLAUDE.md").read_text(), "Working agreement\n")
        for path in self.args.output.rglob("*"):
            if path.is_file():
                self.assertNotIn("SECRET_GRADING_TARGET", path.read_text())

    def test_output_collision_and_repo_location_refused(self):
        self.args.prepare = True
        for output in (self.repo / "runs", self.root):
            with self.subTest(output=output):
                self.args.output = output
                with self.assertRaises(ValueError):
                    self.run_fixture()

    def test_oversubscribed_plan_refused(self):
        self.args.repeats = 2
        with self.assertRaisesRegex(ValueError, "exceeding"):
            self.run_fixture()

    def test_execution_requires_isolation_acknowledgment(self):
        self.args.execute = True
        self.args.output = self.root / "execution"
        with patch.object(runner, "capture") as capture, self.assertRaisesRegex(ValueError, "acknowledge"):
            self.run_fixture()
        capture.assert_not_called()
        self.assertFalse(self.args.output.exists())

    def test_unsupported_interactive_case_is_not_flattened(self):
        for key in ("prior_messages", "interaction", "operator_only_files"):
            with self.subTest(key=key), self.assertRaises(ValueError):
                runner.fixture_files({**self.case, key: [{"content": "history"}]})

    def test_fixture_cannot_override_settings_or_subject_skill(self):
        for name in ("../outside.py", "CLAUDE.md", ".git/config", ".GIT/config", "claude.MD", ".claude/settings.json", ".claude/skills/work-with-me/SKILL.md"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                runner.fixture_files({**self.case, "files": {name: "bad"}})
        self.assertIn(".claude/skills/helper/SKILL.md", runner.fixture_files({**self.case, "files": {".claude/skills/helper/SKILL.md": "helper"}}))

    def test_plan_alternates_conditions(self):
        plan = runner.plan_trials([self.case], 2)
        self.assertEqual([run["condition"] for run in plan], ["baseline", "candidate", "candidate", "baseline"])

    def test_command_has_limits_and_no_permission_bypass(self):
        cmd = runner.command("claude", self.args, self.args.budget_usd)
        self.assertIn("--max-budget-usd", cmd)
        self.assertIn("--max-turns", cmd)
        self.assertIn("--no-session-persistence", cmd)
        for prohibited in ("--dangerously-skip-permissions", "--allowedTools", "--setting-sources", "--system-prompt", "--fallback-model"):
            self.assertNotIn(prohibited, cmd)

    def test_rejects_nonfinite_or_negative_budget(self):
        for amount in ("NaN", "Infinity", "-1", "0"):
            with self.subTest(amount=amount), self.assertRaises(argparse.ArgumentTypeError):
                runner.money(amount)

    def test_usage_uses_final_totals_without_double_counting(self):
        path = self.trace([
            {"type": "assistant", "message": {"id": "m1", "usage": {"output_tokens": 999}, "content": []}},
            {"type": "result", "is_error": False, "usage": {"output_tokens": 10}, "modelUsage": {"model": {"outputTokens": 10}}, "total_cost_usd": 0.1},
        ])
        data = parse_trace(path)
        self.assertEqual(data["usage"], {"output_tokens": 10})
        self.assertEqual(data["estimated_cost_usd"], 0.1)
        self.assertEqual(data["observed_assistant_messages"], 1)

    def test_activation_attempt_distinguished_from_success(self):
        event = {"type": "assistant", "message": {"id": "m1", "content": [{"type": "tool_use", "id": "t1", "name": "Skill", "input": {"skill": "work-with-me"}}]}}
        data = parse_trace(self.trace([event, event]))
        self.assertEqual(data["observed_tool_calls"], 1)
        self.assertIsNone(data["activation_observations"][0]["succeeded"])
        data = parse_trace(self.trace([event, {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "t1", "is_error": True}]}}]))
        self.assertIs(data["activation_observations"][0]["succeeded"], False)

    def test_malformed_and_missing_result_not_success(self):
        path = self.trace([{"type": "system", "subtype": "init", "model": "example"}])
        with path.open("a") as out:
            out.write("not JSON\n")
        data = parse_trace(path)
        self.assertFalse(data["final_received"])
        self.assertIsNone(data["estimated_cost_usd"])
        self.assertEqual(data["malformed_lines"], 1)

    def test_snapshot_and_diff_do_not_follow_symlinks(self):
        workspace = self.root / "workspace"
        workspace.mkdir()
        file = workspace / "app.py"
        file.write_text("before\n")
        before = snapshot(workspace)
        file.write_text("after\n")
        delta = changes(before, snapshot(workspace))
        self.assertEqual(delta["changed_paths"], ["app.py"])
        self.assertIn("-before", delta["diff"])
        try:
            (workspace / "link").symlink_to(self.suite)
        except (OSError, NotImplementedError):
            return
        self.assertEqual(snapshot(workspace)["link"]["kind"], "symlink")
        self.assertNotIn("text", snapshot(workspace)["link"])

    def test_capture_uses_local_fake_process(self):
        out = self.root / "capture"
        out.mkdir()
        result = runner.capture([sys.executable, "-c", "import sys; print(sys.stdin.read()); sys.exit(3)"], self.root, "hello", out, 10)
        self.assertEqual(result["exit_code"], 3)
        self.assertIn("hello", (out / "stdout.jsonl").read_text())

    def test_timeout_recorded(self):
        out = self.root / "timeout"
        out.mkdir()
        result = runner.capture([sys.executable, "-c", "import time; time.sleep(30)"], self.root, "", out, 1)
        self.assertTrue(result["timed_out"])
        self.assertNotEqual(result["exit_code"], 0)

    def test_failed_or_unpriced_run_stops_the_pair(self):
        self.args.execute = True
        self.args.acknowledge_isolation = True
        self.args.environment_note = "Disposable fake environment"
        self.args.output = self.root / "failed-pair"
        def fake_capture(argv, cwd, prompt, directory, timeout):
            (directory / "stdout.jsonl").write_text(json.dumps({"type": "result", "is_error": False, "result": "done"}) + "\n")
            return {"exit_code": 0, "timed_out": False, "interrupted": False}
        help_text = b"--model --effort --output-format --no-session-persistence --max-turns --max-budget-usd"
        with patch.object(runner.shutil, "which", return_value="fake-claude"), patch.object(runner.subprocess, "check_output", side_effect=[help_text, b"fake-version"]), patch.object(runner, "capture", side_effect=fake_capture) as capture:
            report = self.run_fixture()
        self.assertEqual(capture.call_count, 1)
        self.assertIn("stopped", report)
        self.assertEqual(report["behavioral_quality"], "unscored")

    def test_successful_pair_retains_evidence_and_sums_cost_once(self):
        self.args.execute = True
        self.args.acknowledge_isolation = True
        self.args.environment_note = "Fake isolated fixture"
        self.args.output = self.root / "successful-pair"
        def fake_capture(argv, cwd, prompt, directory, timeout):
            (cwd / "app.py").write_text("value = 2\n")
            event = {"type": "result", "is_error": False, "result": "Edited", "total_cost_usd": 0.1, "usage": {"output_tokens": 12}}
            (directory / "stdout.jsonl").write_text(json.dumps(event) + "\n")
            return {"exit_code": 0, "timed_out": False, "interrupted": False}
        help_text = b"--model --effort --output-format --no-session-persistence --max-turns --max-budget-usd"
        with patch.object(runner.shutil, "which", return_value="fake-claude"), patch.object(runner.subprocess, "check_output", side_effect=[help_text, b"fake-version"]), patch.object(runner, "capture", side_effect=fake_capture):
            report = self.run_fixture()
        self.assertEqual(len(report["runs"]), 2)
        self.assertEqual(report["reported_estimated_cost_usd"], "0.2")
        self.assertTrue(report["reported_cost_complete"])
        self.assertNotIn("stopped", report)
        self.assertEqual(report["runs"][0]["changed_paths"], ["app.py"])
        self.assertEqual(report["behavioral_quality"], "unscored")

    def test_casefold_collisions_and_model_option_injection_refused(self):
        with self.assertRaises(ValueError):
            runner.fixture_files({**self.case, "files": {"App.py": "one", "app.py": "two"}})
        for value in ("--dangerously-skip-permissions", "two model names", ""):
            self.args.model = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.run_fixture()


if __name__ == "__main__":
    unittest.main(verbosity=2)
