# Ingredient Recipes

## Desired roads

Resolve candidates with `route.plan_ingredient_options`. Present ambiguity only when the planner cannot choose a feasible pack; otherwise copy its `recommended_next_call.arguments` into one generation call. Report included, partial, substituted, and missed roads.

## Mandatory stops

For a brand-new route, do not create a baseline. For an area-only loop, pass the geocoded area center as the planner start. Call `route.plan_ingredient_options`, use its network-validated recommendation when the user delegated the choice, and copy its `recommended_next_call.arguments` verbatim into exactly one `route.generate_multi_point_route` call without adding fields. A null recommendation or zero external generation budget is a hard stop: never construct a call from candidate packs. Do not manually execute returned `fallback_packs` or retry a distance miss; the server owns bounded pack recovery and same-pack distance calibration. Report stop names, roles, co-satisfied roles, mile/km positions, spacing warnings, network-feasibility warnings, and generation compromises.

For an existing stored route, use `route.plan_water_stops` or `route.plan_poi_stops` to plan along the current geometry.

## Mixed constraints

Resolve roads, POIs, exclusions, and segment qualities into one ingredient plan before generation. Do not make unrelated searches and hope the final route joins them correctly.

## Target-distance climb chains

Follow `climb-route-intelligence`. Keep explicit ids/counts in exact mode. For a climb-only route whose count may flex to fit distance, send one ranked `climb_needs` entry with `climb_selection_mode: "distance_fill"`, bounded min/max counts, and a hard tolerance. Pass the one returned owner-bound plan reference into one `route.generate_multi_point_route` call. The server chooses/orders the CH chain; null planning, a failed distance band, or any unverified selected climb is a hard stop. Count returned CH legs separately from expensive generation jobs, which must remain zero for this mode.
