#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import Any

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def _probe(label: str, url: str, token: str) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {token}", "User-Agent": "route-skill-remote-mcp-eval/0.3.0"}
    async with httpx.AsyncClient(headers=headers, timeout=30, follow_redirects=False) as client:
        async with streamable_http_client(url, http_client=client) as (read, write, _):
            async with ClientSession(read, write) as session:
                initialized = await session.initialize()
                tools = await session.list_tools()
                resources = await session.list_resources()
                prompts = await session.list_prompts()
                return {
                    "label": label,
                    "url": url,
                    "protocol_version": initialized.protocolVersion,
                    "server_name": initialized.serverInfo.name,
                    "tool_count": len(tools.tools),
                    "tools": sorted(tool.name for tool in tools.tools),
                    "resource_count": len(resources.resources),
                    "prompt_count": len(prompts.prompts),
                }


async def _run(base_url: str, token: str) -> list[dict[str, Any]]:
    base = base_url.rstrip("/")
    return [
        await _probe("route-generator", base + "/mcp/route-generator", token),
        await _probe("route-analysis", base + "/mcp/route-analysis", token),
    ]


def _load_cases(root: Path) -> dict[str, dict[str, Any]]:
    cases: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "evals" / "cases").glob("*.yaml")):
        case = json.loads(path.read_text(encoding="utf-8"))
        cases[str(case["id"])] = case
    if len(cases) != 21:
        raise SystemExit(f"Expected exactly 21 checked-in eval cases, found {len(cases)}.")
    return cases


def _bind_plans_to_remote_catalogs(
    *,
    root: Path,
    planning_report: Path,
    servers: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    cases = _load_cases(root)
    report = json.loads(planning_report.read_text(encoding="utf-8"))
    results = report.get("results") if isinstance(report, dict) else None
    if not isinstance(results, list):
        raise SystemExit(f"Planning report has no results array: {planning_report}")

    ownership: dict[str, str] = {}
    duplicates: set[str] = set()
    for server in servers:
        for tool in server["tools"]:
            if tool in ownership:
                duplicates.add(tool)
            ownership[tool] = str(server["label"])
    if duplicates:
        raise SystemExit(f"Remote MCP catalogs overlap: {sorted(duplicates)}")

    by_id = {str(item.get("id")): item for item in results if isinstance(item, dict)}
    bound: list[dict[str, Any]] = []
    for case_id, case in cases.items():
        planned = by_id.get(case_id)
        if planned is None:
            bound.append({"id": case_id, "ok": False, "error": "missing_planning_result"})
            continue
        tools = [str(tool) for tool in planned.get("planned_tools", [])]
        unknown = [tool for tool in tools if tool not in ownership]
        expected = [str(tool) for tool in case.get("must_call", [])]
        missing = [tool for tool in expected if tool not in tools]
        forbidden = [str(tool) for tool in case.get("must_not_call", []) if str(tool) in tools]
        bound.append(
            {
                "id": case_id,
                "prompt": case["prompt"],
                "selected_skill": planned.get("selected_skill"),
                "planned_tools": tools,
                "remote_ownership": {tool: ownership.get(tool) for tool in tools},
                "unknown_remote_tools": unknown,
                "missing_expected_tools": missing,
                "forbidden_tools": forbidden,
                "ok": bool(planned.get("ok")) and not unknown and not missing and not forbidden,
            }
        )
    return bound


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Bind all 21 native Codex skill/tool plans to the real non-overlapping catalogs exposed by both canonical "
            "MCP servers. This certifies remote executability of the plans; stateful behavior remains a separate API gate."
        )
    )
    parser.add_argument("--base-url", default="https://mcpapi.sherpa-map.com")
    parser.add_argument("--token-env", default="ROUTE_MCP_ACCESS_TOKEN")
    parser.add_argument("--planning-report", default="reports/codex-native-final/results.json")
    parser.add_argument("--out", default="reports/remote-mcp-plan-binding.json")
    args = parser.parse_args()
    token = os.getenv(args.token_env, "").strip()
    if not token:
        raise SystemExit(f"{args.token_env} is required for a live probe.")
    root = Path(__file__).resolve().parents[1]
    servers = asyncio.run(_run(args.base_url, token))
    cases = _bind_plans_to_remote_catalogs(
        root=root,
        planning_report=(root / args.planning_report).resolve(),
        servers=servers,
    )
    payload = {
        "mode": "native_plan_remote_catalog_binding",
        "base_url": args.base_url.rstrip("/"),
        "case_count": len(cases),
        "pass_count": sum(1 for case in cases if case["ok"]),
        "servers": servers,
        "cases": cases,
    }
    payload["ok"] = payload["case_count"] == 21 and payload["pass_count"] == 21
    output_path = (root / args.out).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not payload["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
