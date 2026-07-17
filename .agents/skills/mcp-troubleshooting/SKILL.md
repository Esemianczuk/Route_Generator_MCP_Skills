---
name: mcp-troubleshooting
description: Diagnose explicit Route Generator MCP failures, missing state, contradictory tool results, duplicate artifacts, or provider/transport errors. Use only after a call failed or observed state conflicts with a prior confirmed result; do not trigger for ordinary route analysis.
---

# MCP Troubleshooting

## Use when

Use after an explicit error, timeout, missing confirmed artifact, contradictory route state, or reproducible provider/transport failure.

## Do not use when

Do not use speculatively for an unusual-looking but successful route; use route analysis first.

Trust backend state and tool results over model text.

## Workflow

1. Inspect the latest tool trace and route session.
2. Confirm whether the requested route/artifact/POI/edit actually exists.
3. If a generation call followed an ingredient plan, compare it with `recommended_next_call.arguments` and `generation_contract` first. A null recommendation or zero external generation budget means the generation call was invalid; correct the planner input instead of guessing waypoints or retrying generation.
4. Retry only with an evidence-backed argument correction from the returned validation detail. Do not guess that a workspace id, session id, or waypoint caused an HTTP status-only error, and do not repeat the same failing call.
5. If generation bridge is unavailable, report the bridge issue and keep the session ready for retry.
6. If the model produced duplicate or wrong visuals, use a single explicit render call with the correct visual family.

Redact provider keys and avoid echoing secret-bearing URLs.

Do not invent diagnostic MCP tools. The client tool trace is the primary evidence. If backend route-state confirmation is required, use the real `route.list_sessions` or `route.summarize_route`. The only GPX import tool is `route.import_route`; retry it only after correcting its endpoint, arguments, staged-upload handle, or session binding. A user asking what to inspect does not by itself require an immediate retry, so do not include a conditional future retry in the current call plan.

## Postconditions

- The failing layer is identified as provider, MCP transport, tool validation, route engine, artifact delivery, or client rendering.
- A retry changes a justified argument or state condition instead of repeating blindly.
- Secrets and secret-bearing URLs are absent from the report.
