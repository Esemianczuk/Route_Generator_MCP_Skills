#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any

from redaction import redact
from run_eval_suite import load_cases
from skill_catalog import repo_root
from validate_skills import validate_all

SKILL_READ_RE = re.compile(r"\.agents/skills/([^/'\" ]+)/SKILL\.md")

OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "selected_skill": {"type": "string"},
        "planned_tools": {"type": "array", "items": {"type": "string", "pattern": "^route\\.[a-z0-9_]+$"}},
        "excluded_skills": {"type": "array", "items": {"type": "string"}},
        "postconditions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["selected_skill", "planned_tools", "excluded_skills", "postconditions"],
    "additionalProperties": False,
}


def _events(stdout: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for line in stdout.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            result.append(value)
    return result


def _skills_read(events: list[dict[str, Any]]) -> list[str]:
    found: list[str] = []
    for event in events:
        item = event.get("item") if isinstance(event.get("item"), dict) else {}
        if item.get("type") != "command_execution":
            continue
        command = str(item.get("command") or "")
        for name in SKILL_READ_RE.findall(command):
            if name not in found:
                found.append(name)
    return found


def _usage(events: list[dict[str, Any]]) -> dict[str, int]:
    for event in reversed(events):
        if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
            return {str(key): int(value) for key, value in event["usage"].items() if isinstance(value, int)}
    return {}


def _locked_tools(root: Path) -> set[str]:
    lock_path = root / "dist" / "skills.lock.json"
    if not lock_path.exists():
        raise SystemExit("dist/skills.lock.json is required; run generate_skills_lock.py first.")
    value = json.loads(lock_path.read_text(encoding="utf-8"))
    tools: set[str] = set()
    for skill in value.get("skills", []):
        if not isinstance(skill, dict):
            continue
        tools.update(str(item) for item in skill.get("tool_dependencies", []) if str(item).startswith("route."))
    if not tools:
        raise SystemExit("The skills lock does not contain route tool dependencies.")
    return tools


def _grade(case: dict[str, Any], answer: dict[str, Any], skills_read: list[str], valid_tools: set[str]) -> dict[str, Any]:
    planned = [str(item) for item in answer.get("planned_tools", [])]
    expected = [str(item) for item in case.get("must_call", [])]
    forbidden = [str(item) for item in case.get("must_not_call", [])]
    missing = [tool for tool in expected if tool not in planned]
    forbidden_hit = [tool for tool in forbidden if tool in planned]
    selected_skill = str(answer.get("selected_skill") or "")
    expected_skill = str(case.get("expected_skill") or "")
    skill_mismatch = bool(expected_skill and selected_skill != expected_skill)
    selected_skill_not_read = selected_skill not in skills_read
    unknown_tools = [tool for tool in planned if tool not in valid_tools]
    return {
        "id": case["id"],
        "prompt": case["prompt"],
        "expected_skill": expected_skill,
        "selected_skill": selected_skill,
        "skills_read": skills_read,
        "planned_tools": planned,
        "expected_tools": expected,
        "missing": missing,
        "forbidden_hit": forbidden_hit,
        "unknown_tools": unknown_tools,
        "skill_mismatch": skill_mismatch,
        "selected_skill_not_read": selected_skill_not_read,
        "postconditions": answer.get("postconditions", []),
        "excluded_skills": answer.get("excluded_skills", []),
        "ok": not missing and not forbidden_hit and not unknown_tools and not skill_mismatch and not selected_skill_not_read,
    }


def _run_case(
    root: Path,
    case: dict[str, Any],
    model: str,
    schema_path: Path,
    output_dir: Path,
    timeout: int,
    valid_tools: set[str],
) -> dict[str, Any]:
    case_id = str(case["id"])
    last_message = output_dir / f"{case_id}.answer.json"
    prompt = (
        "Use the relevant installed Route Generator skill through the native Codex skill system. "
        "Read only the one primary SKILL.md needed for this request. Do not execute remote MCP calls; "
        "this lane certifies native progressive disclosure and tool planning. Return the primary selected skill, "
        "the ordered bare route.* tool identifiers that should be called now, skills deliberately excluded, and result postconditions. "
        "Do not put arguments, scenarios, annotations, or tools that are only being explained into planned_tools.\n\n"
        f"User request: {case['prompt']}"
    )
    command = [
        "codex",
        "exec",
        "-m",
        model,
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "--json",
        "--output-schema",
        str(schema_path),
        "--output-last-message",
        str(last_message),
        "-C",
        str(root),
        prompt,
    ]
    started = time.perf_counter()
    completed = subprocess.run(command, cwd=root, text=True, capture_output=True, timeout=timeout)
    duration_ms = round((time.perf_counter() - started) * 1000, 1)
    (output_dir / f"{case_id}.events.jsonl").write_text(completed.stdout, encoding="utf-8")
    (output_dir / f"{case_id}.stderr.log").write_text(completed.stderr, encoding="utf-8")
    events = _events(completed.stdout)
    answer: dict[str, Any] = {}
    if last_message.exists():
        try:
            value = json.loads(last_message.read_text(encoding="utf-8"))
            if isinstance(value, dict):
                answer = value
        except json.JSONDecodeError:
            pass
    result = _grade(case, answer, _skills_read(events), valid_tools)
    result.update(
        {
            "returncode": completed.returncode,
            "duration_ms": duration_ms,
            "usage": _usage(events),
            "runtime_error": completed.returncode != 0 or not answer,
        }
    )
    result["ok"] = bool(result["ok"] and not result["runtime_error"])
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run native Codex skill-selection and tool-planning certification.")
    parser.add_argument("--out", default="reports/codex-native")
    parser.add_argument("--model", default="gpt-5.4")
    parser.add_argument("--case", action="append", dest="case_ids", help="Run one case id; repeat to select multiple cases.")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = repo_root()
    validation = validate_all(root)
    if not validation["ok"]:
        print(json.dumps(validation, indent=2))
        raise SystemExit(1)
    cases = load_cases()
    if args.case_ids:
        selected = set(args.case_ids)
        cases = [case for case in cases if case["id"] in selected]
        missing_cases = sorted(selected - {case["id"] for case in cases})
        if missing_cases:
            raise SystemExit("Unknown case ids: " + ", ".join(missing_cases))
    if args.limit > 0:
        cases = cases[: args.limit]

    output_dir = root / args.out
    output_dir.mkdir(parents=True, exist_ok=True)
    schema_path = output_dir / "output-schema.json"
    schema_path.write_text(json.dumps(OUTPUT_SCHEMA, indent=2) + "\n", encoding="utf-8")
    if args.dry_run:
        print(json.dumps({"mode": "codex_native_planning", "model": args.model, "case_ids": [case["id"] for case in cases]}, indent=2))
        return

    valid_tools = _locked_tools(root)
    results = [_run_case(root, case, args.model, schema_path, output_dir, args.timeout, valid_tools) for case in cases]
    summary = {
        "mode": "codex_native_planning",
        "model": args.model,
        "case_count": len(results),
        "pass_count": sum(1 for result in results if result["ok"]),
        "native_skill_read_count": sum(1 for result in results if result["skills_read"]),
        "average_duration_ms": round(sum(result["duration_ms"] for result in results) / max(1, len(results)), 1),
        "planning_only": True,
    }
    report = redact({"summary": summary, "results": results})
    (output_dir / "results.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if summary["pass_count"] != summary["case_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
