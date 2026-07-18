#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


JsonDict = dict[str, Any]
SECRET_PATTERN = re.compile(r"\b(?:sk|rk|sess|token)-[A-Za-z0-9_-]{8,}\b", re.IGNORECASE)
WORKSPACE_KEYS = {"route_workspace_id", "workspace_id", "route_session_id", "session_id"}
ROUTE_KEYS = {"route_id", "active_route_id", "result_route_id", "source_route_id"}
ARTIFACT_KEYS = {"artifact_id"}
SINGLE_ARTIFACT_CASES = {
    "001-loop-generation",
    "008-weather-headwind",
    "010-3d-terrain",
    "011-3d-profile",
    "012-map-zoom",
}
DEFAULT_ORDER = [
    "001-loop-generation",
    "002-summary-followup",
    "023-regenerate-active-workspace",
    "007-coffee-stop",
    "018-undo-redo",
    "003-named-roads",
    "004-water-stops",
    "021-area-loop-water-stops",
    "022-server-distance-calibration",
    "005-fuel-stops",
    "006-parking-anchor",
    "008-weather-headwind",
    "009-weather-summary",
    "010-3d-terrain",
    "011-3d-profile",
    "012-map-zoom",
    "013-cycling-performance",
    "014-bike-setup",
    "015-import-gpx",
    "016-avoid-road-edit",
    "017-tour-leg",
    "019-tool-index",
    "020-troubleshoot-bridge",
]
PRIMARY_WORKSPACE_CASES = {
    "001-loop-generation",
    "002-summary-followup",
    "023-regenerate-active-workspace",
    "007-coffee-stop",
    "018-undo-redo",
    "008-weather-headwind",
    "009-weather-summary",
    "010-3d-terrain",
    "011-3d-profile",
    "012-map-zoom",
    "013-cycling-performance",
    "014-bike-setup",
    "016-avoid-road-edit",
    "017-tour-leg",
}
CONTINUATION_CASES = {"002-summary-followup", "023-regenerate-active-workspace", "007-coffee-stop", "018-undo-redo"}
HOST_INSTRUCTIONS = """You are executing the Route Generator remote-MCP semantic release suite.
Use the connected remote MCP servers to perform the request, not merely describe a plan. Trust remote tool
descriptions and returned identifiers. Never invent success, route state, skill reads, or artifacts. Never use a
local function or fallback. For follow-ups, reuse the explicit route workspace and active route instead of
generating a replacement. When hosted skills are mounted, read the relevant SKILL.md before complex route work."""


@dataclass
class RouteContext:
    workspace_id: str | None = None
    route_id: str | None = None
    provider_response_id: str | None = None


@dataclass
class Evidence:
    response_id: str | None = None
    model: str | None = None
    text: str = ""
    mcp_list_servers: set[str] = field(default_factory=set)
    mcp_calls: list[JsonDict] = field(default_factory=list)
    function_calls: list[str] = field(default_factory=list)
    skill_reads: set[str] = field(default_factory=set)
    workspace_ids: set[str] = field(default_factory=set)
    route_ids: set[str] = field(default_factory=set)
    active_route_ids: list[str] = field(default_factory=list)
    artifact_ids: list[str] = field(default_factory=list)
    usage: JsonDict = field(default_factory=dict)
    provider_error: str | None = None


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _safe_error(value: object, *secrets: str) -> str:
    text = str(value)
    for secret in secrets:
        if secret:
            text = text.replace(secret, "[REDACTED]")
    return SECRET_PATTERN.sub("[REDACTED]", text)[:3000]


def _json_maybe(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    stripped = value.strip()
    if not stripped or stripped[0] not in "[{":
        return value
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return value


def _collect_identifiers(value: Any, evidence: Evidence, depth: int = 0) -> None:
    if depth > 8:
        return
    value = _json_maybe(value)
    if isinstance(value, list):
        for item in value[:100]:
            _collect_identifiers(item, evidence, depth + 1)
        return
    if not isinstance(value, dict):
        return
    for index, (raw_key, item) in enumerate(value.items()):
        if index >= 180:
            break
        key = str(raw_key).lower()
        if isinstance(item, str) and item:
            if key in WORKSPACE_KEYS:
                evidence.workspace_ids.add(item)
            elif key in ROUTE_KEYS:
                evidence.route_ids.add(item)
                if key == "active_route_id":
                    evidence.active_route_ids.append(item)
            elif key in ARTIFACT_KEYS:
                evidence.artifact_ids.append(item)
        _collect_identifiers(item, evidence, depth + 1)


def _tool_name(item: JsonDict) -> str:
    for key in ("name", "tool_name", "tool"):
        value = item.get(key)
        if isinstance(value, str) and value:
            return value
    return "mcp.call"


def _mcp_output(item: JsonDict) -> Any:
    for key in ("output", "result", "structuredContent", "structured_content"):
        if key in item:
            return _json_maybe(item[key])
    return None


def _shell_commands(item: JsonDict) -> str:
    action = item.get("action")
    if not isinstance(action, dict):
        return ""
    commands = action.get("commands")
    if not isinstance(commands, list):
        return ""
    return "\n".join(str(command) for command in commands)


def _shell_output_succeeded(item: JsonDict) -> bool:
    outputs = item.get("output")
    if not isinstance(outputs, list) or not outputs:
        return False
    for output in outputs:
        if not isinstance(output, dict):
            return False
        outcome = output.get("outcome")
        if not isinstance(outcome, dict) or outcome.get("type") != "exit" or outcome.get("exit_code") != 0:
            return False
    return True


def extract_evidence(response: JsonDict, skill_names: list[str]) -> Evidence:
    evidence = Evidence(
        response_id=response.get("id") if isinstance(response.get("id"), str) else None,
        model=response.get("model") if isinstance(response.get("model"), str) else None,
        usage=response.get("usage") if isinstance(response.get("usage"), dict) else {},
    )
    text_parts: list[str] = []
    pending_skill_reads: dict[str, set[str]] = {}
    for item in response.get("output") or []:
        if not isinstance(item, dict):
            continue
        item_type = str(item.get("type") or "")
        if item_type == "mcp_list_tools":
            label = item.get("server_label")
            if isinstance(label, str) and label:
                evidence.mcp_list_servers.add(label)
        elif item_type == "mcp_call":
            output = _mcp_output(item)
            call_error = item.get("error")
            if not call_error and isinstance(output, dict):
                call_error = output.get("error")
            evidence.mcp_calls.append(
                {
                    "tool": _tool_name(item),
                    "server_label": str(item.get("server_label") or ""),
                    "arguments": _json_maybe(item.get("arguments")) if item.get("arguments") is not None else {},
                    "ok": not bool(call_error),
                    "error": _safe_error(call_error) if call_error else None,
                }
            )
            _collect_identifiers(output, evidence)
        elif item_type == "function_call":
            evidence.function_calls.append(str(item.get("name") or item.get("id") or "function_call"))
        elif item_type == "shell_call":
            commands = _shell_commands(item).lower()
            if "skill.md" in commands:
                call_id = str(item.get("call_id") or item.get("id") or "")
                reads = {name for name in skill_names if name.lower() in commands}
                if call_id and reads:
                    pending_skill_reads[call_id] = reads
        elif item_type == "shell_call_output":
            call_id = str(item.get("call_id") or "")
            reads = pending_skill_reads.pop(call_id, set())
            if reads and _shell_output_succeeded(item):
                evidence.skill_reads.update(reads)
        elif item_type == "message":
            for content in item.get("content") or []:
                if not isinstance(content, dict):
                    continue
                if content.get("type") in {"output_text", "text"} and isinstance(content.get("text"), str):
                    text_parts.append(content["text"])
    evidence.text = "\n".join(text_parts)
    return evidence


def build_remote_tools(
    generator_url: str,
    analysis_url: str,
    route_token: str,
    skill_refs: list[JsonDict] | None = None,
) -> list[JsonDict]:
    tools: list[JsonDict] = []
    if skill_refs:
        tools.append(
            {
                "type": "shell",
                "environment": {
                    "type": "container_auto",
                    "skills": [
                        {"type": "skill_reference", "skill_id": item["skill_id"], "version": str(item["version"])}
                        for item in skill_refs
                    ],
                },
            }
        )
    tools.extend(
        [
            {
                "type": "mcp",
                "server_label": "route_generator",
                "server_description": "Creates, imports, edits, and versions persisted route workspaces.",
                "server_url": generator_url,
                "authorization": route_token,
                "require_approval": "never",
            },
            {
                "type": "mcp",
                "server_label": "route_analysis",
                "server_description": "Analyzes and renders routes stored in persisted route workspaces.",
                "server_url": analysis_url,
                "authorization": route_token,
                "require_approval": "never",
            },
        ]
    )
    return tools


def build_response_body(
    *,
    model: str,
    prompt: str,
    generator_url: str,
    analysis_url: str,
    route_token: str,
    previous_response_id: str | None,
    skill_refs: list[JsonDict] | None,
    reasoning_effort: str | None,
) -> JsonDict:
    body: JsonDict = {
        "model": model,
        "store": True,
        "parallel_tool_calls": False,
        "instructions": HOST_INSTRUCTIONS,
        "input": [{"role": "user", "content": prompt}],
        "tools": build_remote_tools(generator_url, analysis_url, route_token, skill_refs),
    }
    if previous_response_id:
        body["previous_response_id"] = previous_response_id
    if reasoning_effort:
        body["reasoning"] = {"effort": reasoning_effort}
    return body


def _load_cases(root: Path) -> dict[str, JsonDict]:
    cases: dict[str, JsonDict] = {}
    for path in sorted((root / "evals" / "cases").glob("*.yaml")):
        case = json.loads(path.read_text(encoding="utf-8"))
        cases[str(case["id"])] = case
    if len(cases) != 23:
        raise SystemExit(f"Expected exactly 23 eval cases, found {len(cases)}.")
    if set(cases) != set(DEFAULT_ORDER):
        raise SystemExit("The checked-in cases do not match the certified semantic execution schedule.")
    return cases


def _load_skill_refs(path: Path | None) -> list[JsonDict]:
    if path is None:
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_items = payload.get("skills") if isinstance(payload, dict) else payload
    if not isinstance(raw_items, list):
        raise SystemExit("Skill reference JSON must be an array or contain a skills array.")
    refs: list[JsonDict] = []
    for raw in raw_items:
        if not isinstance(raw, dict):
            continue
        name = str(raw.get("name") or raw.get("skill_name") or "").strip()
        skill_id = str(raw.get("skill_id") or raw.get("id") or "").strip()
        version = raw.get("version")
        if not name or not skill_id or not isinstance(version, int) or version < 1:
            raise SystemExit("Every hosted skill reference requires name, skill_id, and a positive integer version.")
        refs.append({"name": name, "skill_id": skill_id, "version": version})
    names = [item["name"] for item in refs]
    if len(names) != len(set(names)):
        raise SystemExit("Hosted skill names must be unique.")
    return refs


async def _probe_server(label: str, url: str, token: str) -> JsonDict:
    headers = {"Authorization": f"Bearer {token}", "User-Agent": "route-openai-semantic-eval/0.2.0"}
    async with httpx.AsyncClient(headers=headers, timeout=30, follow_redirects=False) as client:
        async with streamable_http_client(url, http_client=client) as (read, write, _):
            async with ClientSession(read, write) as session:
                initialized = await session.initialize()
                tools = await session.list_tools()
                serialized = [tool.model_dump(mode="json", exclude_none=True) for tool in tools.tools]
                digest = hashlib.sha256(json.dumps(serialized, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
                return {
                    "label": label,
                    "url": url,
                    "protocol_version": initialized.protocolVersion,
                    "server_name": initialized.serverInfo.name,
                    "server_version": initialized.serverInfo.version,
                    "tool_count": len(serialized),
                    "catalog_hash": digest,
                    "tools": sorted(tool["name"] for tool in serialized),
                }


async def probe_servers(base_url: str, route_token: str) -> list[JsonDict]:
    base = base_url.rstrip("/")
    return [
        await _probe_server("route_generator", base + "/mcp/route-generator", route_token),
        await _probe_server("route_analysis", base + "/mcp/route-analysis", route_token),
    ]


def _request_response(client: httpx.Client, body: JsonDict, api_key: str) -> tuple[JsonDict, float]:
    started = time.perf_counter()
    response = client.post(
        "/responses",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=body,
    )
    elapsed = round((time.perf_counter() - started) * 1000, 1)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("OpenAI Responses API returned a non-object JSON payload.")
    return payload, elapsed


def _case_prompt(case: JsonDict, context: RouteContext, staged_upload_id: str | None) -> str:
    prompt = str(case["prompt"])
    context_lines = ["Perform this request with actual remote MCP calls and ground the response in their results."]
    if case["id"] in PRIMARY_WORKSPACE_CASES and context.workspace_id:
        context_lines.append(f"The explicit route_workspace_id is {context.workspace_id}.")
    if case["id"] in PRIMARY_WORKSPACE_CASES and context.route_id:
        context_lines.append(f"The active route_id is {context.route_id}.")
    if case["id"] == "015-import-gpx":
        if not staged_upload_id:
            raise ValueError("Case 015 requires --staged-upload-id so the model can import through remote MCP.")
        context_lines.append(f"The already staged upload_id is {staged_upload_id}; do not use a direct import endpoint.")
    return prompt + "\n\nEvaluation context:\n- " + "\n- ".join(context_lines)


def grade_case(case: JsonDict, evidence: Evidence, expected_skill_read: bool) -> JsonDict:
    called = [str(item["tool"]) for item in evidence.mcp_calls]
    expected = [str(item) for item in case.get("must_call", [])]
    forbidden_expected = [str(item) for item in case.get("must_not_call", [])]
    missing = [tool for tool in expected if tool not in called]
    forbidden = [tool for tool in forbidden_expected if tool in called]
    ordered_expected = [str(item) for item in case.get("must_call_in_order", [])]
    ordered_positions: list[int] = []
    next_index = 0
    for tool in ordered_expected:
        try:
            position = called.index(tool, next_index)
        except ValueError:
            ordered_positions = []
            break
        ordered_positions.append(position)
        next_index = position + 1
    order_invalid = bool(ordered_expected) and len(ordered_positions) != len(ordered_expected)
    raw_exact_counts = case.get("exact_call_counts")
    exact_counts = raw_exact_counts if isinstance(raw_exact_counts, dict) else {}
    exact_call_count_mismatches = {
        str(tool): {"expected": int(expected_count), "actual": called.count(str(tool))}
        for tool, expected_count in exact_counts.items()
        if called.count(str(tool)) != int(expected_count)
    }
    failed_calls = [item["tool"] for item in evidence.mcp_calls if not item["ok"]]
    expected_skill = str(case.get("expected_skill") or "")
    skill_missing = expected_skill_read and expected_skill not in evidence.skill_reads
    unique_artifacts = sorted(set(evidence.artifact_ids))
    requires_single_artifact = str(case["id"]) in SINGLE_ARTIFACT_CASES
    artifact_count_invalid = requires_single_artifact and len(unique_artifacts) != 1
    ok = (
        not evidence.provider_error
        and not missing
        and not forbidden
        and not order_invalid
        and not exact_call_count_mismatches
        and not failed_calls
        and not evidence.function_calls
        and not skill_missing
        and not artifact_count_invalid
    )
    return {
        "id": case["id"],
        "prompt": case["prompt"],
        "expected_skill": expected_skill,
        "skills_observed_read": sorted(evidence.skill_reads),
        "mcp_list_servers": sorted(evidence.mcp_list_servers),
        "mcp_calls": evidence.mcp_calls,
        "missing_expected_tools": missing,
        "forbidden_tools": forbidden,
        "ordered_expected_tools": ordered_expected,
        "tool_order_invalid": order_invalid,
        "exact_call_count_mismatches": exact_call_count_mismatches,
        "failed_mcp_calls": failed_calls,
        "function_calls": evidence.function_calls,
        "skill_read_missing": skill_missing,
        "response_id": evidence.response_id,
        "workspace_ids": sorted(evidence.workspace_ids),
        "route_ids": sorted(evidence.route_ids),
        "artifact_ids": unique_artifacts,
        "duplicate_artifact_count": max(0, len(evidence.artifact_ids) - len(unique_artifacts)),
        "requires_single_artifact": requires_single_artifact,
        "artifact_count_invalid": artifact_count_invalid,
        "usage": evidence.usage,
        "provider_error": evidence.provider_error,
        "ok": ok,
    }


def _git_commit(root: Path) -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _negative_probe(
    *,
    client: httpx.Client,
    api_key: str,
    model: str,
    generator_url: str,
    analysis_url: str,
    route_token: str,
    skill_refs: list[JsonDict],
    reasoning_effort: str | None,
    name: str,
) -> JsonDict:
    body = build_response_body(
        model=model,
        prompt="Call route.tool_index now and report the remote result. Do not answer from memory.",
        generator_url=generator_url,
        analysis_url=analysis_url,
        route_token=route_token,
        previous_response_id=None,
        skill_refs=skill_refs,
        reasoning_effort=reasoning_effort,
    )
    try:
        response, latency = _request_response(client, body, api_key)
        evidence = extract_evidence(response, [item["name"] for item in skill_refs])
        remote_failure = any(not item["ok"] for item in evidence.mcp_calls) or bool(response.get("error"))
        return {
            "name": name,
            "response_id": evidence.response_id,
            "latency_ms": latency,
            "function_calls": evidence.function_calls,
            "remote_failure_visible": remote_failure,
            "provider_error": None,
            "ok": remote_failure and not evidence.function_calls,
        }
    except Exception as exc:
        return {
            "name": name,
            "response_id": None,
            "latency_ms": None,
            "function_calls": [],
            "remote_failure_visible": True,
            "provider_error": _safe_error(exc, api_key, route_token),
            "ok": True,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute the 23 semantic cases through OpenAI provider-native remote MCP.")
    parser.add_argument("--execute", action="store_true", help="Make provider and remote MCP calls. Omit for a redacted plan.")
    parser.add_argument("--base-url", default="https://mcpapi.sherpa-map.com")
    parser.add_argument("--openai-base-url", default="https://api.openai.com/v1")
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--reasoning-effort", default="medium")
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    parser.add_argument("--route-token-env", default="ROUTE_MCP_ACCESS_TOKEN")
    parser.add_argument("--skill-refs-json", type=Path)
    parser.add_argument("--require-native-skills", action="store_true")
    parser.add_argument("--staged-upload-id")
    parser.add_argument("--workspace-id")
    parser.add_argument("--route-id")
    parser.add_argument("--case", action="append", default=[])
    parser.add_argument("--negative-probes", action="store_true")
    parser.add_argument("--out", type=Path, default=Path("reports/openai-remote-semantic.json"))
    args = parser.parse_args()

    root = _repo_root()
    cases = _load_cases(root)
    selected = args.case or DEFAULT_ORDER
    unknown = sorted(set(selected) - set(cases))
    if unknown:
        raise SystemExit(f"Unknown case IDs: {unknown}")
    skill_refs = _load_skill_refs(args.skill_refs_json)
    if args.require_native_skills and not skill_refs:
        raise SystemExit("--require-native-skills requires --skill-refs-json with immutable provider versions.")

    plan = {
        "mode": "openai_provider_native_remote_mcp_semantic",
        "execute": args.execute,
        "model": args.model,
        "base_url": args.base_url.rstrip("/"),
        "case_ids": selected,
        "case_count": len(selected),
        "native_skills": bool(skill_refs),
        "skill_names": [item["name"] for item in skill_refs],
        "negative_probes": args.negative_probes,
    }
    if not args.execute:
        print(json.dumps(plan, indent=2))
        return

    api_key = os.getenv(args.api_key_env, "").strip()
    route_token = os.getenv(args.route_token_env, "").strip()
    if not api_key:
        raise SystemExit(f"{args.api_key_env} is required with --execute.")
    if not route_token:
        raise SystemExit(f"{args.route_token_env} is required with --execute.")
    if "015-import-gpx" in selected and not args.staged_upload_id:
        raise SystemExit("The import case requires --staged-upload-id.")

    servers = asyncio.run(probe_servers(args.base_url, route_token))
    overlaps = set(servers[0]["tools"]) & set(servers[1]["tools"])
    if overlaps:
        raise SystemExit(f"Remote MCP catalogs overlap: {sorted(overlaps)}")
    generator_url = args.base_url.rstrip("/") + "/mcp/route-generator"
    analysis_url = args.base_url.rstrip("/") + "/mcp/route-analysis"
    ownership = {tool: server["label"] for server in servers for tool in server["tools"]}
    context = RouteContext(workspace_id=args.workspace_id, route_id=args.route_id)
    coffee_route_before_edit: str | None = None
    coffee_route_after_edit: str | None = None
    results: list[JsonDict] = []
    setup_results: list[JsonDict] = []

    with httpx.Client(base_url=args.openai_base_url.rstrip("/"), timeout=900, follow_redirects=False) as client:
        for case_id in selected:
            case = cases[case_id]
            if case_id == "018-undo-redo":
                setup_prompt = "Undo the coffee-stop edit in the current explicit route workspace using remote MCP."
                if context.workspace_id:
                    setup_prompt += f" The route_workspace_id is {context.workspace_id}."
                body = build_response_body(
                    model=args.model,
                    prompt=setup_prompt,
                    generator_url=generator_url,
                    analysis_url=analysis_url,
                    route_token=route_token,
                    previous_response_id=context.provider_response_id,
                    skill_refs=skill_refs,
                    reasoning_effort=args.reasoning_effort,
                )
                try:
                    setup_response, setup_latency = _request_response(client, body, api_key)
                    setup_evidence = extract_evidence(setup_response, [item["name"] for item in skill_refs])
                    setup_active_route = setup_evidence.active_route_ids[-1] if setup_evidence.active_route_ids else None
                    setup_ok = (
                        "route.undo_tour" in [item["tool"] for item in setup_evidence.mcp_calls]
                        and not setup_evidence.function_calls
                        and (coffee_route_after_edit is None or setup_active_route != coffee_route_after_edit)
                    )
                    context.provider_response_id = setup_evidence.response_id
                    if setup_active_route:
                        context.route_id = setup_active_route
                    setup_results.append(
                        {
                            "name": "prepare-redo-with-remote-undo",
                            "mcp_calls": setup_evidence.mcp_calls,
                            "response_id": setup_evidence.response_id,
                            "active_route_id": setup_active_route,
                            "expected_pre_edit_route_id": coffee_route_before_edit,
                            "latency_ms": setup_latency,
                            "ok": setup_ok and not setup_evidence.function_calls,
                        }
                    )
                except Exception as exc:
                    setup_results.append(
                        {
                            "name": "prepare-redo-with-remote-undo",
                            "mcp_calls": [],
                            "response_id": None,
                            "latency_ms": None,
                            "provider_error": _safe_error(exc, api_key, route_token),
                            "ok": False,
                        }
                    )

            previous_id = context.provider_response_id if case_id in CONTINUATION_CASES else None
            expected_workspace_id = context.workspace_id if case_id in PRIMARY_WORKSPACE_CASES else None
            route_before_case = context.route_id
            try:
                prompt = _case_prompt(case, context, args.staged_upload_id)
                body = build_response_body(
                    model=args.model,
                    prompt=prompt,
                    generator_url=generator_url,
                    analysis_url=analysis_url,
                    route_token=route_token,
                    previous_response_id=previous_id,
                    skill_refs=skill_refs,
                    reasoning_effort=args.reasoning_effort,
                )
                response, latency = _request_response(client, body, api_key)
                evidence = extract_evidence(response, [item["name"] for item in skill_refs])
            except Exception as exc:
                latency = None
                evidence = Evidence(provider_error=_safe_error(exc, api_key, route_token))
            graded = grade_case(case, evidence, bool(skill_refs))
            wrong_server_calls = [
                item["tool"]
                for item in evidence.mcp_calls
                if ownership.get(str(item["tool"])) != str(item["server_label"])
            ]
            workspace_reused = not expected_workspace_id or expected_workspace_id in evidence.workspace_ids
            graded["wrong_server_calls"] = wrong_server_calls
            graded["expected_workspace_id"] = expected_workspace_id
            graded["workspace_reused"] = workspace_reused
            graded["ok"] = bool(graded["ok"]) and not wrong_server_calls and workspace_reused
            graded["latency_ms"] = latency
            active_route = evidence.active_route_ids[-1] if evidence.active_route_ids else None
            graded["active_route_id"] = active_route
            if case_id == "007-coffee-stop":
                coffee_route_before_edit = route_before_case
                coffee_route_after_edit = active_route
                edit_created_revision = bool(active_route and active_route != route_before_case)
                graded["edit_created_new_active_route"] = edit_created_revision
                graded["ok"] = bool(graded["ok"]) and edit_created_revision
            if case_id == "018-undo-redo":
                redo_restored_edit = bool(active_route and coffee_route_after_edit and active_route == coffee_route_after_edit)
                graded["redo_restored_edited_route"] = redo_restored_edit
                graded["ok"] = bool(graded["ok"]) and redo_restored_edit
            results.append(graded)

            if case_id in PRIMARY_WORKSPACE_CASES:
                if evidence.workspace_ids:
                    context.workspace_id = sorted(evidence.workspace_ids)[-1]
                if active_route:
                    context.route_id = active_route
            if case_id in {"001-loop-generation", "002-summary-followup", "007-coffee-stop", "018-undo-redo"}:
                context.provider_response_id = evidence.response_id

        negative_results: list[JsonDict] = []
        if args.negative_probes:
            negative_results.append(
                _negative_probe(
                    client=client,
                    api_key=api_key,
                    model=args.model,
                    generator_url=generator_url,
                    analysis_url=analysis_url,
                    route_token="invalid-route-mcp-token",
                    skill_refs=skill_refs,
                    reasoning_effort=args.reasoning_effort,
                    name="invalid_route_token_no_fallback",
                )
            )
            negative_results.append(
                _negative_probe(
                    client=client,
                    api_key=api_key,
                    model=args.model,
                    generator_url="https://mcp-unavailable.invalid/mcp/route-generator",
                    analysis_url="https://mcp-unavailable.invalid/mcp/route-analysis",
                    route_token=route_token,
                    skill_refs=skill_refs,
                    reasoning_effort=args.reasoning_effort,
                    name="unavailable_remote_endpoint_no_fallback",
                )
            )

    catalog_labels = sorted({label for item in results for label in item["mcp_list_servers"]})
    payload = {
        **plan,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "skill_repo_commit": _git_commit(root),
        "mounted_skill_ids": [item["skill_id"] for item in skill_refs],
        "mounted_skill_versions": {item["name"]: item["version"] for item in skill_refs},
        "servers": servers,
        "catalog_labels_observed": catalog_labels,
        "setup_results": setup_results,
        "results": results,
        "negative_results": negative_results,
        "pass_count": sum(1 for item in results if item["ok"]),
        "total_latency_ms": round(sum(float(item["latency_ms"] or 0) for item in results), 1),
        "route_workspace_ids": sorted({value for item in results for value in item["workspace_ids"]}),
        "route_ids": sorted({value for item in results for value in item["route_ids"]}),
        "artifact_ids": sorted({value for item in results for value in item["artifact_ids"]}),
    }
    payload["ok"] = (
        payload["pass_count"] == len(results)
        and all(item["ok"] for item in setup_results)
        and all(item["ok"] for item in negative_results)
        and not any(item["function_calls"] for item in results)
        and (not skill_refs or all(not item["skill_read_missing"] for item in results))
        and catalog_labels == ["route_analysis", "route_generator"]
    )
    output = args.out if args.out.is_absolute() else root / args.out
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": payload["ok"], "pass_count": payload["pass_count"], "case_count": len(results), "output": str(output)}, indent=2))
    if not payload["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
