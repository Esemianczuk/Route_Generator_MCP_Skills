# Route Tool Selection

- Use `route.generate_routes` for best-in-area, loop, or ordinary point-to-point generation.
- Use `route.generate_multi_point_route` for ordered anchors, mandatory stops, or segment-specific criteria.
- Use `route.generate_named_road_route` only after named roads have been resolved and ordered.
- Use `route.summarize_route` for “tell me about this route”; never regenerate for a summary.
- Preserve route workspace identifiers returned by tools. Do not treat the MCP transport session as a route workspace.
- Mention an image only when the latest tool result returns an artifact.
