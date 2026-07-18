---
name: route-poi-stops
description: Local cached POI, water, fuel, cafe, restroom, parking/start-anchor, and stop-insertion workflows for Route Generator MCP. Use when users ask to find, rank, add, compare, visualize, or plan a POI or parking start; this is the primary skill for a single non-private parking/start-anchor request.
---

# Route POI Stops

## Use when

Use to find, rank, plan, add, or visualize water, fuel, cafe, restroom, parking, repair, shelter, park, or other stop candidates.

## Do not use when

Do not use merely because a place name appears as a route endpoint. For a brand-new route that must pass through one or more support POIs, use route-ingredient-planning first.

Use offline/local cached POI tools first. Live Overpass is a fallback, not the default.

## Tool Priority

- Water/refill: `route.search_water_sources`, then `route.plan_water_stops`.
- Parking/start anchors: `route.search_parking_anchors`.
- Coffee, fuel, restrooms, parks, repairs, scenic, shelters: `route.search_cached_pois`, then `route.plan_poi_stops`. Use `route_portion`, `route_fraction`, `route_mile`, or `route_km` when the user specifies where along the route.
- Specialized raw OSM tags or cache shortfalls: `route.search_pois`.

The planning tools above are for existing stored routes. For a new route with required water, fuel, cafe, restroom, park, parking, or mixed POI ingredients, call `route.plan_ingredient_options`; then copy its `recommended_next_call.arguments` into one `route.generate_multi_point_route` call.

When a user says "choose for me" or "best", pick the best candidate and add it. Otherwise present numbered options.

For a requested loop that should start at ranked non-private parking, use `route.search_parking_anchors` and then call `route.generate_routes` with `generation_mode: "loop"` and the selected parking coordinates as `start`. There is no `route.generate_loop` tool; never invent a specialized loop tool name.

For an existing route and "your choice", "best", or "nearest", call `route.search_cached_pois` and then `route.add_poi_stop` for the selected candidate in the same turn. A search result is not an added stop. Use `route.search_parking_anchors` for ranked non-private starts, and `route.plan_water_stops` or `route.plan_poi_stops` for repeated stop cadence on the current route.

`route.add_poi_stop` normally inserts routable connector geometry. Call it exactly once per selected POI and treat its completion as terminal. If that POI was already inserted, `status: already_attached` with `changed: false` confirms the active route without another mutation; do not call it again. If a nearby POI cannot be connector-routed, it may return an `access_only` immutable revision with unchanged geometry, `geometry_detour_inserted: false`, and an explicit `access_offset_m`. Treat that as an added support marker with a short access offset, never as proof that the route passes through the POI.

## Postconditions

- Candidates include route-relative distance/position and ranking rationale.
- A POI is never described as added until the add/edit result confirms it.
- State whether an added POI is routed through, a connector detour, or an access-only support marker.
- Mandatory stop cadence on a new route uses one ingredient plan and one multi-point generation rather than disconnected searches.
