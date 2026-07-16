---
name: route-generator-core
description: Core Route Generator MCP operating procedure for generating, summarizing, and following up on stored routes. Use for any route generation, best-in-area, loop, point-to-point, multi-route comparison, route-session continuity, or "tell me about this route" request.
---

# Route Generator Core

## Use when

Use for creating a route, selecting the generation mode, comparing generated alternatives, or summarizing the active route after generation.

## Do not use when

Do not use it to answer weather, cycling-physics, visual-only, imported-file, or explicit failure-diagnosis requests when a narrower skill applies.

Start by preserving session state. Use the current session id for every route tool unless the user explicitly asks to start a new workspace.

## Workflow

1. Clarify only missing essentials: location/anchors, route mode, distance/units, activity profile, and count. Call `route.geocode_locations` when named anchors do not yet have coordinates.
2. If the request contains mandatory stops, stop cadence, named roads, exclusions tied to specific ingredients, or mixed route ingredients, hand off to route-ingredient-planning before generation. Do not generate a baseline route first.
3. For an ordinary route with no mandatory ingredients, generate with `route.generate_routes`. For a planned ingredient route, copy the planner's `recommended_next_call.arguments` into exactly one `route.generate_multi_point_route` call.
4. After generation, summarize the returned route names/aliases, distance, ascent, climbs, surfaces, ingredient verification, warnings, and artifacts.
5. For follow-ups like "tell me about it", call `route.summarize_route`; do not generate again.
6. Mention images only when the latest tool result returned image artifacts.

For a catalog/help request, use the compatibility tool `route.tool_index` without generating a route.

Read [references/route-tools.md](references/route-tools.md) when tool choice is unclear.

## Postconditions

- A generation result names the active route alias/id and route workspace identifiers.
- A follow-up summary never creates a replacement route.
- Claims about distance, warnings, or artifacts are grounded in the latest tool result.
