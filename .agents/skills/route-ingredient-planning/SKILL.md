---
name: route-ingredient-planning
description: Multi-ingredient planning for routes that must combine named roads, desired road classes, repeated water/fuel cadence, multiple POIs, exclusions, or several mandatory anchors. Use for "must ride", "avoid", repeated stops, fuel-stop tours, or complex ingredient ordering before generation; use route-poi-stops for a single parking/start-anchor search.
---

# Route Ingredient Planning

## Use when

Use before generation when the request combines named roads, mandatory POIs, stop cadence, multiple anchors, exclusions, or segment-specific qualities.

## Do not use when

Do not use for a simple single-anchor loop, a single parking/start-anchor search, or an ordinary point-to-point request with no mandatory ingredients.

Prefer an explicit ingredient plan before trying a large generation.

## Workflow

1. Resolve named start/end anchors with `route.geocode_locations`. For an area-only loop such as "around Madison," pass the geocoded area and use its center as the planning start; the backend also infers this anchor when only `area.center` is supplied.
2. For a brand-new route with any mandatory support stop, cadence, named road, or mixed ingredient constraint, call `route.plan_ingredient_options` before generation.
   For an area route with a stop count but no user-specified cadence, use `route_mode: "loop"`, the target distance, and a count-only need such as `{"class":"water","target_count":3}`. Do not invent `spacing_m` or `min_spacing_m`; the planner distributes repeated stops across even interior route slots. Supply spacing only when the user actually requested an interval or minimum gap.
3. Use the planner's recommended pack when the user delegated the choice. The planner may rerank its sidecar packs with cached shortest-path feasibility checks before choosing it. An unresolved mandatory ingredient always makes the pack non-executable: a partial pack with one water stop is never a valid recommendation for a three-water-stop request, even when the user delegated stop choice. If the planner reports a meaningful compromise, network-feasibility risk, or no executable pack, explain it before generating.
4. Inspect `generation_contract` before generation. Continue only when `recommended_next_call` is present and `external_generation_call_budget` is `1`; copy its compact `{ingredient_plan_ref: ...}` arguments verbatim into exactly one `route.generate_multi_point_route` call. Do not expand the reference or add waypoints, distance, `generation_mode`, `variants`, or other fields. The server owns the canonical plan. If the call is null or the budget is `0`, do not copy candidates or option-pack waypoints by hand and do not call any generation tool. Correct a missing area/start input once or explain the reported shortfall.
5. Treat bounded fallback and distance calibration behind the plan reference as transparent server-side recovery; they must not be called manually by the model. The server may use up to two internal same-pack calibration passes when all ingredients were reached but distance alone missed tolerance. Never synthesize a second waypoint plan, generate a baseline route first, or add planned stops one at a time.
6. Use the returned default 3D profile artifact as the route visual. It should contain normal climb callouts and the verified support-stop POI markers; do not make an extra render call unless the user requests another view or the default artifact is missing.
7. Report the selected ingredients and the returned `ingredient_verification`, including partial, missed, substituted, and co-satisfied roles. If verification is `verified`, report the route as complete and do not offer a distance retry merely because the actual distance differs within the accepted tolerance. Keep route/workspace IDs as plain identifiers, never fabricated `sandbox:` or file links.

Use these exact tool paths; do not invent intermediate planner names:

- New loop or point-to-point route with water, fuel, cafes, restrooms, parks, parking, named roads, or mixed mandatory ingredients: `route.geocode_locations` when needed -> `route.plan_ingredient_options` -> exactly one `route.generate_multi_point_route`.
- Existing stored route that needs support stops planned along its current corridor: `route.plan_water_stops` or `route.plan_poi_stops`.
- Existing stored route that needs one confirmed stop inserted: search the local cache, then use `route.add_poi_stop`.
- Required named roads without other mandatory POIs may use `route.plan_ingredient_options` followed by the returned generation call. Use `route.generate_named_road_route` only when the planner explicitly recommends that specialized path.

`route.plan_water_stops` and `route.plan_poi_stops` require an existing stored route. They are follow-up tools, not pre-generation planners.

For requests such as "three water stops, one of them a park", encode the requirements together in `poi_needs`. One selected stop may co-satisfy multiple roles. Do not search water and parks independently and hope the results line up.

Do not use live Overpass before the ingredient planner. The planner owns cache-first candidate selection and reports whether a fallback is needed.

Use [references/agent-recipes.md](references/agent-recipes.md) for multi-stop and desired-road flows.

## Postconditions

- The plan reports resolved, partial, substituted, and missing ingredients.
- Mandatory anchors are ordered before route generation and have a stable ingredient pack id.
- Generation starts only when the returned plan is feasible or the user accepts a stated compromise.
- A new-route request performs one expensive route-generation call after planning.
- The MCP tool may make one bounded internal fallback attempt for a clearly infeasible primary pack, but the model still makes exactly one external generation call.
- The final response identifies any co-satisfied role, such as which water stop is also the park.
- Treat a verified stop within the returned waypoint tolerance (normally at most about 100 m) as part of the route. Describe that small access offset as on-route access, not as a reason to offer another full reroute. Offer a corrective edit only when verification marks the stop missed/partial or the offset is materially larger.
