"""Offline evidence collection. Tool observations are not quality scores."""
from __future__ import annotations

from collections import Counter
import difflib
import hashlib
import json
import math
import os
from pathlib import Path

MAX_FILE = 2_000_000
MAX_FILES = 2000


def snapshot(root: Path) -> dict:
    """Hash a small fixture without following agent-created symbolic links."""
    result = {}
    total = 0
    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in {".git", "__pycache__"})
        for name in sorted(list(dirs) + files):
            path = Path(directory) / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                result[relative] = {"kind": "symlink", "target": os.readlink(path)}
                if name in dirs:
                    dirs.remove(name)
            elif path.is_file():
                size = path.stat().st_size
                total += size
                if size > MAX_FILE or total > 20 * MAX_FILE:
                    raise ValueError("Fixture output exceeds the inspection size limit")
                content = path.read_bytes()
                record = {"kind": "file", "bytes": size, "sha256": hashlib.sha256(content).hexdigest()}
                if size <= 64_000:
                    try:
                        record["text"] = content.decode("utf-8")
                    except UnicodeDecodeError:
                        pass
                result[relative] = record
            elif not path.is_dir():
                result[relative] = {"kind": "special"}
            if len(result) > MAX_FILES:
                raise ValueError("Too many fixture outputs to inspect")
    return result


def changes(before: dict, after: dict) -> dict:
    changed = [name for name in sorted(before.keys() | after.keys()) if before.get(name) != after.get(name)]
    diff = []
    for name in changed:
        left, right = before.get(name, {}), after.get(name, {})
        if "text" in left or "text" in right:
            diff.extend(difflib.unified_diff(left.get("text", "").splitlines(True), right.get("text", "").splitlines(True), fromfile="before/" + name, tofile="after/" + name))
    return {"changed_paths": changed, "diff": "".join(diff)}


def parse_trace(path: Path) -> dict:
    """Use final usage once; never add message usage or thinking a second time."""
    calls = {}
    results = {}
    messages = set()
    final = None
    init = None
    malformed = 0
    with path.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            if not line.strip():
                continue
            try:
                event = json.loads(line)
                if not isinstance(event, dict):
                    raise ValueError("Expected an event object")
            except (ValueError, TypeError):
                malformed += 1
                continue
            if event.get("type") == "system" and event.get("subtype") == "init":
                init = {key: event[key] for key in ("model", "tools", "permissionMode", "claude_code_version", "session_id") if key in event}
            if event.get("type") == "result":
                final = event
            message = event.get("message")
            if not isinstance(message, dict):
                continue
            if event.get("type") == "assistant" and message.get("id"):
                messages.add(message["id"])
            content = message.get("content", [])
            for block in content if isinstance(content, list) else []:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_use" and block.get("id"):
                    calls[block["id"]] = {"name": block.get("name"), "input": block.get("input", {})}
                elif block.get("type") == "tool_result" and block.get("tool_use_id"):
                    results[block["tool_use_id"]] = not bool(block.get("is_error"))
    activation = []
    reads = Counter()
    for identifier, call in calls.items():
        data = call["input"] if isinstance(call["input"], dict) else {}
        name = call["name"]
        is_skill = name == "Skill" and str(data.get("skill", "")).split(":")[-1] == "work-with-me"
        file_path = str(data.get("file_path", "")).replace("\\", "/")
        is_read = name == "Read" and file_path.endswith("/work-with-me/SKILL.md")
        if is_skill or is_read:
            activation.append({"tool_id": identifier, "tool": name, "succeeded": results.get(identifier)})
        if name == "Read":
            reads[json.dumps(data, sort_keys=True)] += 1
    cost = final.get("total_cost_usd") if final else None
    if isinstance(cost, bool) or not isinstance(cost, (int, float)) or not math.isfinite(cost) or cost < 0:
        cost = None
    return {
        "final_received": final is not None,
        "malformed_lines": malformed,
        "client_error": final.get("is_error") if final else None,
        "result_subtype": final.get("subtype") if final else None,
        "result_text": final.get("result") if final else None,
        "estimated_cost_usd": cost,
        "usage": final.get("usage") if final else None,
        "model_usage": final.get("modelUsage") if final else None,
        "client_turns": final.get("num_turns") if final else None,
        "init": init,
        "observed_assistant_messages": len(messages),
        "observed_tool_calls": len(calls),
        "activation_observations": activation,
        "repeated_read_requests": sum(max(0, count - 1) for count in reads.values()),
        "notes": "No activation observation does not prove no loading. Repeated reads require validity review. Usage fields are raw client totals, not additive categories across model/message totals.",
    }
