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

1. Resolve anchors and requested road/POI ingredients.
2. Choose the narrow dedicated path before the generic planner. Repeated fuel cadence alone uses `route.geocode_locations` -> `route.search_cached_pois` (or `route.plan_poi_stops` when route progress already exists) -> `route.generate_multi_point_route`; repeated water cadence uses the dedicated water planner. Call `route.plan_ingredient_options` for named-road ingredients, mixed POI categories, exclusions combined with mandatory anchors, or genuinely unclear ordering. A paved-only constraint does not by itself turn a fuel-cadence request into the generic path.
3. Use local cached POI planners before live Overpass.
4. Generate with `route.generate_named_road_route` or `route.generate_multi_point_route` once the skeleton is feasible.
5. Report included, partial, missed, and substituted ingredients.

Use these exact tool paths; do not invent intermediate planner names:

- Water cadence between named endpoints: `route.geocode_locations` -> `route.plan_water_stops` -> `route.generate_multi_point_route`.
- Fuel cadence on a new point-to-point route: `route.geocode_locations` -> `route.search_cached_pois` -> `route.generate_multi_point_route`. Use `route.plan_poi_stops` instead only when an existing route already supplies route-progress positions. Do not replace this path with `route.plan_ingredient_options` merely because the route also has a paved/surface constraint.
- Required named roads: `route.plan_ingredient_options` -> `route.generate_named_road_route`.
- Mixed named roads, POIs, exclusions, and segment constraints: `route.plan_ingredient_options` first, then use the generation call returned by that plan.

`route.plan_ingredient_options` is not a substitute for `route.plan_water_stops` when the request explicitly asks for water at a cadence. The water planner supplies water-specific ranked anchors for multipoint generation.

Use [references/agent-recipes.md](references/agent-recipes.md) for multi-stop and desired-road flows.

## Postconditions

- The plan reports resolved, partial, substituted, and missing ingredients.
- Mandatory anchors are ordered before route generation.
- Generation starts only when the returned plan is feasible or the user accepts a stated compromise.
