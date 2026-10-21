#!/usr/bin/env python3
"""Opt-in paired Claude Code trials. Default: read-only plan, no model calls.

Run only in an operator-provided disposable environment. Temporary workspaces
are NOT a sandbox. Existing settings, credentials, hooks, and permissions are
not changed or bypassed. Review evaluation/TRIALS.md before --execute.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time

from check_repository import check_cases, safe_fixture_path
from trial_evidence import changes, parse_trace, snapshot

ROOT = Path(__file__).resolve().parent.parent


def git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.PIPE)


def resolve_ref(repo: Path, ref: str) -> str:
    sha = git(repo, "rev-parse", "--verify", "--end-of-options", ref + "^{commit}").decode().strip()
    if not re.fullmatch(r"[0-9a-f]{40,64}", sha):
        raise ValueError("Cannot resolve an immutable commit")
    return sha


def instruction_snapshot(repo: Path, sha: str, mode: str) -> dict[str, bytes]:
    paths = ["skills/work-with-me"]
    if mode == "behavior":
        paths.append("instructions/CLAUDE.md")
    tree = git(repo, "ls-tree", "-rz", sha, "--", *paths)
    selected = {}
    for entry in tree.split(b"\0"):
        if not entry:
            continue
        meta, raw_path = entry.split(b"\t", 1)
        permissions, kind, blob = meta.decode().split()
        source = raw_path.decode("utf-8")
        if kind != "blob" or permissions not in {"100644", "100755"}:
            raise ValueError("Instruction snapshots must contain regular files only")
        target = "CLAUDE.md" if source == "instructions/CLAUDE.md" else ".claude/" + source
        selected[target] = git(repo, "cat-file", "blob", blob)
    if ".claude/skills/work-with-me/SKILL.md" not in selected or (mode == "behavior" and "CLAUDE.md" not in selected):
        raise ValueError("Revision lacks the required agreement or skill")
    if sum(map(len, selected.values())) > 2_000_000:
        raise ValueError("Instruction snapshot is unexpectedly large")
    return selected


def fixture_files(case: dict) -> dict[str, bytes]:
    if case.get("runner_compatible") is not True or any(case.get(key) for key in ("prior_messages", "interaction", "operator_only_files")):
        raise ValueError(f"{case['id']} needs the manual protocol or a supported interaction adapter")
    files = {}
    for name, content in case.get("files", {}).items():
        parts = Path(name).parts
        if not safe_fixture_path(name) or any(part.casefold() in {".git", ".gitmodules"} for part in parts):
            raise ValueError(f"Unsafe fixture path: {name}")
        if name.casefold() == "claude.md" or name.casefold().startswith(".claude/") and not name.startswith(".claude/skills/"):
            raise ValueError("Fixtures cannot override the agreement, settings, or hooks")
        if name.casefold().startswith(".claude/skills/work-with-me/"):
            raise ValueError("Fixture cannot replace the skill under test")
        if name.casefold() in {path.casefold() for path in files}:
            raise ValueError("Fixture paths collide on a case-insensitive filesystem")
        files[name] = content.encode("utf-8")
    return files


def money(value: str) -> Decimal:
    try:
        amount = Decimal(value)
    except InvalidOperation:
        raise argparse.ArgumentTypeError("Expected a positive decimal budget") from None
    if not amount.is_finite() or amount <= 0:
        raise argparse.ArgumentTypeError("Budget must be positive and finite")
    return amount


def positive(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("Expected a positive integer")
    return number


def plan_trials(cases: list[dict], repeats: int) -> list[dict]:
    plan = []
    for trial in range(repeats):
        for index, case in enumerate(cases):
            order = ["baseline", "candidate"] if (trial + index) % 2 == 0 else ["candidate", "baseline"]
            for condition in order:
                plan.append({"case_id": case["id"], "repeat": trial + 1, "condition": condition})
    return plan


def command(executable: str, args: argparse.Namespace, budget: Decimal) -> list[str]:
    return [executable, "-p", "--model", args.model, "--effort", args.effort,
            "--output-format", "stream-json", "--verbose", "--no-session-persistence",
            "--max-turns", str(args.max_turns), "--max-budget-usd", str(budget)]


def capture(argv: list[str], cwd: Path, prompt: str, directory: Path, timeout: int) -> dict:
    """Retain full output. No shell interpolation, automatic retry, or permission grants."""
    started = time.monotonic()
    timed_out = False
    interrupted = False
    with (directory / "stdout.jsonl").open("wb") as out, (directory / "stderr.log").open("wb") as err:
        options = {"start_new_session": True} if os.name == "posix" else {}
        process = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.PIPE, stdout=out, stderr=err, **options)
        try:
            process.communicate(prompt.encode("utf-8"), timeout=timeout)
        except (subprocess.TimeoutExpired, KeyboardInterrupt) as error:
            timed_out = isinstance(error, subprocess.TimeoutExpired)
            interrupted = not timed_out
            if os.name == "posix":
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            else:
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True, check=False)
                if process.poll() is None:
                    process.kill()
            process.communicate()
    return {"exit_code": process.returncode, "timed_out": timed_out, "interrupted": interrupted, "elapsed_seconds": round(time.monotonic() - started, 3)}


def write_json(path: Path, data: dict | list) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def materialize(directory: Path, files: dict[str, bytes], instructions: dict[str, bytes]) -> Path:
    workspace = directory / "workspace"
    workspace.mkdir(parents=True, exist_ok=False)
    for name, content in {**files, **instructions}.items():
        if not safe_fixture_path(name):
            raise ValueError("Invalid materialization path")
        target = workspace / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    return workspace


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    result.add_argument("--suite", type=Path, default=ROOT / "evaluation/comparison-cases.json")
    result.add_argument("--cases", required=True, help="Comma-separated explicit case IDs; no implicit full-suite run")
    result.add_argument("--baseline-ref", required=True)
    result.add_argument("--candidate-ref", default="HEAD", help="Committed source only; uncommitted edits are not included")
    result.add_argument("--model", required=True, help="Use an exact model ID for comparisons")
    result.add_argument("--effort", required=True, choices=["low", "medium", "high", "xhigh", "max", "ultracode"])
    result.add_argument("--budget-usd", required=True, type=money, help="Client-estimated limit per run, NOT a hard billing cap")
    result.add_argument("--max-total-usd", required=True, type=money, help="Maximum sum of planned client limits, with actual reported spend checked between runs")
    result.add_argument("--max-turns", required=True, type=positive)
    result.add_argument("--timeout", required=True, type=positive, help="Per-run wall-clock seconds")
    result.add_argument("--repeats", default=1, type=positive)
    result.add_argument("--claude", default="claude", help="Already-installed Claude Code executable")
    result.add_argument("--output", type=Path, help="New directory outside this source repository")
    mode = result.add_mutually_exclusive_group()
    mode.add_argument("--prepare", action="store_true", help="Write fixtures without running any model")
    mode.add_argument("--execute", action="store_true", help="Explicitly opt in to usage-consuming model calls")
    result.add_argument("--acknowledge-isolation", action="store_true", help="Confirm a disposable environment and comparable settings with no conflicting global skill")
    result.add_argument("--environment-note", help="Record isolation/settings/tool/cache conditions, without credentials")
    return result


def run(args: argparse.Namespace, repo: Path = ROOT) -> dict:
    if not args.model or args.model.startswith("-") or any(char.isspace() for char in args.model):
        raise ValueError("Use a nonempty model identifier, not CLI options or whitespace")
    suite_bytes = args.suite.read_bytes()
    suite = json.loads(suite_bytes)
    check_cases(suite)
    selected_ids = args.cases.split(",")
    if len(selected_ids) != len(set(selected_ids)):
        raise ValueError("Select each case only once; use --repeats for repetitions")
    by_id = {case["id"]: case for case in suite["cases"]}
    if any(name not in by_id for name in selected_ids):
        raise ValueError("Unknown case ID")
    cases = [by_id[name] for name in selected_ids]
    fixtures = {case["id"]: fixture_files(case) for case in cases}
    mode = suite.get("mode", "behavior")
    if mode not in {"behavior", "activation"}:
        raise ValueError("Unsupported suite mode")
    refs = {"baseline": resolve_ref(repo, args.baseline_ref), "candidate": resolve_ref(repo, args.candidate_ref)}
    instructions = {key: instruction_snapshot(repo, sha, mode) for key, sha in refs.items()}
    planned = plan_trials(cases, args.repeats)
    nominal = args.budget_usd * len(planned)
    if nominal > args.max_total_usd:
        raise ValueError(f"Planned client limits total {nominal}, exceeding --max-total-usd")
    report = {"schema_version": 1, "mode": mode, "refs": refs, "suite_sha256": hashlib.sha256(suite_bytes).hexdigest(),
              "requested_model": args.model, "effort": args.effort, "nominal_budget_usd": str(nominal),
              "budget_warning": "Client estimates can overshoot and differ from billing/subscription quota. Leave headroom.",
              "environment_note": args.environment_note, "isolation": "Operator supplied; this runner is not a sandbox",
              "plan": planned, "runs": [], "behavioral_quality": "unscored", "reported_cost_complete": True}
    if not (args.prepare or args.execute):
        return report
    if not args.output:
        raise ValueError("--output is required for preparation or execution")
    output = args.output.expanduser().resolve()
    if output.is_relative_to(repo.resolve()) or output.exists():
        raise ValueError("Output must be a new directory outside the source repository")
    executable = None
    if args.execute:
        if not args.acknowledge_isolation or not args.environment_note:
            raise ValueError("Execution requires --acknowledge-isolation and --environment-note")
        executable = shutil.which(args.claude)
        if not executable:
            raise ValueError("Claude Code is not installed; no model call made")
        help_text = subprocess.check_output([executable, "--help"], timeout=15).decode("utf-8", errors="replace")
        for flag in ("--model", "--effort", "--output-format", "--no-session-persistence", "--max-turns", "--max-budget-usd"):
            if flag not in help_text:
                raise ValueError(f"Installed CLI does not expose {flag}; do not bypass this check")
        report["client_version"] = subprocess.check_output([executable, "--version"], timeout=15).decode().strip()
    output.mkdir(parents=True, mode=0o700)
    write_json(output / "plan.json", report)
    spent = Decimal(0)
    for number, item in enumerate(planned, 1):
        case = by_id[item["case_id"]]
        directory = output / f"trial-{number:03d}"
        directory.mkdir(mode=0o700)
        workspace = materialize(directory, fixtures[case["id"]], instructions[item["condition"]])
        metadata = {**item, "revision": refs[item["condition"]], "prompt": case["prompt"],
                    "fixture_sha256": hashlib.sha256(json.dumps(case.get("files", {}), sort_keys=True).encode()).hexdigest(),
                    "quality_review": {"completion": None, "correctness": None, "scope": None, "evidence": None, "delivery": None, "unnecessary_permission_questions": None}}
        before = snapshot(workspace)
        write_json(directory / "before.json", before)
        write_json(directory / "review.json", metadata)
        (directory / "prompt.txt").write_text(case["prompt"], encoding="utf-8")
        if not args.execute:
            report["runs"].append({**item, "status": "prepared"})
            continue
        remaining = args.max_total_usd - spent
        if remaining <= 0:
            report["stopped"] = "Reported estimated total reached the run budget"
            break
        argv = command(executable, args, min(args.budget_usd, remaining))
        process = capture(argv, workspace, case["prompt"], directory, args.timeout)
        evidence = parse_trace(directory / "stdout.jsonl")
        after = snapshot(workspace)
        delta = changes(before, after)
        (directory / "changes.diff").write_text(delta.pop("diff"), encoding="utf-8")
        write_json(directory / "after.json", after)
        record = {**metadata, "command": argv, "process": process, "evidence": evidence, **delta}
        write_json(directory / "result.json", record)
        report["runs"].append(record)
        write_json(output / "summary.json", report)
        cost = evidence["estimated_cost_usd"]
        if cost is not None:
            spent += Decimal(str(cost))
        else:
            report["reported_cost_complete"] = False
        if process["exit_code"] != 0 or process["timed_out"] or process["interrupted"] or not evidence["final_received"] or evidence["malformed_lines"] or evidence["client_error"] is not False or cost is None:
            report["stopped"] = "Run failed, was incomplete, or lacked trustworthy usage; no automatic retry"
            break
    report["reported_estimated_cost_usd"] = str(spent)
    write_json(output / "summary.json", report)
    return report


def main(argv: list[str] | None = None) -> int:
    try:
        result = run(parser().parse_args(argv))
        print(json.dumps(result if not result["runs"] else {key: result[key] for key in ("refs", "mode", "reported_estimated_cost_usd", "behavioral_quality")} | ({"stopped": result["stopped"]} if "stopped" in result else {}), indent=2))
        return 1 if "stopped" in result else 0
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
