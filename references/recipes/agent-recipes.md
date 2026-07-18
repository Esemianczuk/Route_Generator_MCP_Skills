# Agent Recipes

## New Scenic Route With Summary

1. Geocode if needed.
2. Call `route.generate_routes` with mode, distance, count, criteria, and session id. Use `count: 1` unless the user explicitly asks for multiple alternatives. Keep ordinary quiet/low-traffic requests at `criteria.traffic: avoid`; do not strengthen them into hard blockers. If the tool returns no route plus a retry recipe, copy its `set` values under `weights` for one corrective retry and preserve the requested distance/count.
3. Summarize each returned route by alias/name, distance, ascent, climbs, surfaces, and any warnings.
4. Mention images only when image artifacts were returned.

## Desired Roads Route

1. Call `route.plan_ingredient_options` or `route.generate_named_road_route` with the requested road names.
2. If roads are unresolved or confidence is low, ask one clarification or present candidates.
3. Use the returned ordered ingredient skeleton to generate the route.
4. Summarize which roads were included, partial, missed, or rerouted around.

## Stops Every N Miles

1. For a brand-new route with mandatory stops, geocode named anchors and call `route.plan_ingredient_options` before any generation. For an area-only loop, use the geocoded area center as the planning start.
2. Continue only when the planner returns `recommended_next_call` with an external generation budget of one, then copy its compact `{ingredient_plan_ref: ...}` arguments verbatim into exactly one `route.generate_multi_point_route` call. Do not expand the reference or add waypoints, distance, `generation_mode`, `variants`, or other fields. A null call or zero budget forbids generation; never build from candidate packs, generate a baseline first, or manually run bounded fallback packs or distance-correction retries. The server owns the canonical plan and both bounded behaviors.
3. For an already-stored route, use `route.plan_water_stops` or `route.plan_poi_stops`; use add-stop edits only after the user confirms or delegates a candidate.
4. Return verified stop names, mile markers, warnings, and the default 3D profile with climb callouts and POI markers. Render another view only when requested or when the default artifact is missing.

## Weather Decision

1. Call `route.analyze_weather` first.
2. Use the metric that the analysis says matters most. Avoid rain maps when precipitation is negligible.
3. Render a whole-route weather map unless the user asks for a zoom/close-up.
4. For "wind and heat", render separate wind and temperature images.

## Imported GPX Course

1. Import/match the course into the route session.
2. Summarize confidence, distance, matched ratio, surfaces, roads, and off-network segments.
3. Preserve the imported shape unless the user asks to reroute or edit.
4. For sparse route files, use turn-point matching and flag intentional off-road/farm/private segments as analyzable off-network spans.

## Troubleshooting

If the tool result conflicts with the text, trust tool artifacts and state. If route context is missing, call a session/list/summarize tool before asking the user to paste ids.
