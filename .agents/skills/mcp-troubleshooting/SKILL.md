---
name: mcp-troubleshooting
description: Troubleshooting Route Generator MCP tool failures, missing route sessions, unavailable bridge errors, duplicate visuals, wrong visual family, failed POI additions, model tool confusion, and provider/client integration issues. Use when a route MCP call errors or the assistant/tool behavior contradicts expected state.
---

# MCP Troubleshooting

Trust backend state and tool results over model text.

## Workflow

1. Inspect the latest tool trace and route session.
2. Confirm whether the requested route/artifact/POI/edit actually exists.
3. Retry only with corrected arguments; do not repeat the same failing call.
4. If generation bridge is unavailable, report the bridge issue and keep the session ready for retry.
5. If the model produced duplicate or wrong visuals, use a single explicit render call with the correct visual family.

Redact provider keys and avoid echoing secret-bearing URLs.

