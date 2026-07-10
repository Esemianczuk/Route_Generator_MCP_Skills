# Agent Recipes

## New Scenic Route With Summary

1. Geocode if needed.
2. Call `route.generate_routes` with mode, distance, count, criteria, and session id.
3. Summarize each returned route by alias/name, distance, ascent, climbs, surfaces, and any warnings.
4. Mention images only when image artifacts were returned.

## Desired Roads Route

1. Call `route.plan_ingredient_options` or `route.generate_named_road_route` with the requested road names.
2. If roads are unresolved or confidence is low, ask one clarification or present candidates.
3. Use the returned ordered ingredient skeleton to generate the route.
4. Summarize which roads were included, partial, missed, or rerouted around.

## Stops Every N Miles

1. Generate or select a baseline route.
2. Use cached POI planning (`plan_water_stops`, `plan_poi_stops`, or `search_parking_anchors`) with spacing and route session.
3. Prefer multi-point route generation when stops are mandatory; use add-stop edits when stops are optional or close.
4. Return stop names, mile markers, warnings, and a map only if requested or if choices need review.

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

