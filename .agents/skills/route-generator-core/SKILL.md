---
name: route-generator-core
description: Core Route Generator MCP operating procedure for generating, summarizing, and following up on stored routes. Use for any route generation, best-in-area, loop, point-to-point, multi-route comparison, route-session continuity, or "tell me about this route" request.
---

# Route Generator Core

Start by preserving session state. Use the current session id for every route tool unless the user explicitly asks to start a new workspace.

## Workflow

1. Clarify only missing essentials: location/anchors, route mode, distance/units, activity profile, and count.
2. Generate with `route.generate_routes`, `route.generate_multi_point_route`, or a specialized ingredient tool.
3. After generation, summarize the returned route names/aliases, distance, ascent, climbs, surfaces, warnings, and artifacts.
4. For follow-ups like "tell me about it", call `route.summarize_route`; do not generate again.
5. Mention images only when the latest tool result returned image artifacts.

Read `../../../../references/tool-contracts/route-tools.md` when tool choice is unclear.

