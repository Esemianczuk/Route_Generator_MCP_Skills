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

1. Clarify only missing essentials: location/anchors, route mode, distance/units, activity profile, and count. Treat count literally: one/single/default means exactly one result; generate alternatives only when the user requests them. Call `route.geocode_locations` when named anchors do not yet have coordinates.
2. If the request contains mandatory stops, stop cadence, named roads, exclusions tied to specific ingredients, or mixed route ingredients, hand off to route-ingredient-planning before generation. Do not generate a baseline route first.
3. For an ordinary route with no mandatory ingredients, generate with `route.generate_routes`; pass `count: 1` and one intent unless the user explicitly requested 2-3 alternatives. Treat "favor", "prefer", "quieter", "low traffic", and ordinary "avoid traffic" wording as soft preferences. A qualified request such as "climbing welcome but not extreme" is balanced elevation, not a hilly maximum. A successful one-route result ends generation for this response: do not regenerate merely because a measured soft-preference percentage or distance is imperfect; report the tradeoff. Only if the tool itself failed and provides `retry_suggestions[].set` may you put those keys under top-level `weights`, preserve the original mode, distance, units, and count, and make at most one corrective retry. Use `strongly_avoid` or `strictly_avoid` only when the user explicitly asks for a hard/strict exclusion. For a planned ingredient route, copy the planner's `recommended_next_call.arguments` into exactly one `route.generate_multi_point_route` call.
4. After generation, summarize the returned route names/aliases, distance, ascent, climbs, surfaces, ingredient verification, warnings, and artifacts. Copy distance, ascent, and climb count from the generated route's top-level `summary`; do not substitute a nested diagnostic or independently recalculate them. Print route/workspace IDs as plain identifiers (normally code-formatted); never invent `sandbox:`, file, download, or asset links for an ID. For ingredient-planned routes, the default 3D profile should already show climb callouts and support-stop POIs; do not add a redundant render call or offer to render the profile that was already returned. When ingredient verification is `verified`, treat a route inside its distance tolerance as complete; state the actual distance but do not offer another distance-tuning pass unless the user explicitly required greater precision.
5. For follow-ups like "tell me about it", call `route.summarize_route`; do not generate again.
6. For a requested full retry or broad distance/character change, call `route.regenerate_routes`. Pass the explicit route id when available; otherwise pass the current `route_workspace_id`/session and let the tool infer its active route. Do not invent a `based_on_route_id`, and do not require the user to repeat an id already represented by the active workspace.
7. Mention images only when the latest tool result returned image artifacts.

For a catalog/help request, use the compatibility tool `route.tool_index` without generating a route. Do not call it during an ordinary route task; the provider already supplied the live tool catalog.

Read [references/route-tools.md](references/route-tools.md) when tool choice is unclear.

## Postconditions

- A generation result names the active route alias/id and route workspace identifiers.
- A one-route request returns and summarizes exactly one route, not unsolicited alternatives.
- A follow-up summary never creates a replacement route.
- Claims about distance, warnings, or artifacts are grounded in the latest tool result.
