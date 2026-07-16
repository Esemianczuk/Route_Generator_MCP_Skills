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

1. Resolve named start/end anchors with `route.geocode_locations`.
2. For a brand-new route with any mandatory support stop, cadence, named road, or mixed ingredient constraint, call `route.plan_ingredient_options` before generation.
3. Use the planner's recommended pack when the user delegated the choice. The planner may rerank its sidecar packs with cached shortest-path feasibility checks before choosing it. If the planner reports a meaningful compromise, network-feasibility risk, or no executable pack, explain it before generating.
4. Copy `recommended_next_call.arguments` into exactly one `route.generate_multi_point_route` call. Those arguments may contain bounded `fallback_packs`; they are for transparent server-side recovery and must not be called manually by the model. Do not synthesize a second waypoint plan, generate a baseline route first, or add the planned stops one at a time.
5. Report the selected ingredients and the returned `ingredient_verification`, including partial, missed, substituted, and co-satisfied roles.

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
