# Route Tool Selection

- Use `route.generate_routes` for best-in-area, loop, or ordinary point-to-point generation.
- Use `route.plan_ingredient_options` before generation for any new route with ordered anchors, mandatory stops, named roads, or mixed ingredients.
- Use `route.generate_multi_point_route` once with the planner's exact recommended arguments. Never manually replay planner-provided fallback packs.
- Use `route.generate_named_road_route` only when a planner result explicitly recommends that specialized path.
- Use `route.summarize_route` for “tell me about this route”; never regenerate for a summary.
- Preserve route workspace identifiers returned by tools. Do not treat the MCP transport session as a route workspace.
- Mention an image only when the latest tool result returns an artifact.
