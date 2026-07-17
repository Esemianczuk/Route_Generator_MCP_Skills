# Ingredient Recipes

## Desired roads

Resolve candidates with `route.plan_ingredient_options`. Present ambiguity only when the planner cannot choose a feasible pack; otherwise copy its `recommended_next_call.arguments` into one generation call. Report included, partial, substituted, and missed roads.

## Mandatory stops

For a brand-new route, do not create a baseline. For an area-only loop, pass the geocoded area center as the planner start. Call `route.plan_ingredient_options`, use its network-validated recommendation when the user delegated the choice, and copy its `recommended_next_call.arguments` into exactly one `route.generate_multi_point_route` call. A null recommendation or zero external generation budget is a hard stop: never construct a call from candidate packs. Do not manually execute returned `fallback_packs`; the server owns that bounded recovery path. Report stop names, roles, co-satisfied roles, mile/km positions, spacing warnings, network-feasibility warnings, and generation compromises.

For an existing stored route, use `route.plan_water_stops` or `route.plan_poi_stops` to plan along the current geometry.

## Mixed constraints

Resolve roads, POIs, exclusions, and segment qualities into one ingredient plan before generation. Do not make unrelated searches and hope the final route joins them correctly.
