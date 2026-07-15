---
name: route-poi-stops
description: Local cached POI, water, fuel, cafe, restroom, parking/start-anchor, and stop-insertion workflows for Route Generator MCP. Use when users ask to find, rank, add, compare, visualize, or plan a POI or parking start; this is the primary skill for a single non-private parking/start-anchor request.
---

# Route POI Stops

## Use when

Use to find, rank, plan, add, or visualize water, fuel, cafe, restroom, parking, repair, shelter, park, or other stop candidates.

## Do not use when

Do not use merely because a place name appears as a route endpoint; use the core generation or ingredient-planning skill unless it is a requested stop/anchor search.

Use offline/local cached POI tools first. Live Overpass is a fallback, not the default.

## Tool Priority

- Water/refill: `route.search_water_sources`, then `route.plan_water_stops`.
- Parking/start anchors: `route.search_parking_anchors`.
- Coffee, fuel, restrooms, parks, repairs, scenic, shelters: `route.search_cached_pois`, then `route.plan_poi_stops`.
- Specialized raw OSM tags or cache shortfalls: `route.search_pois`.

When a user says "choose for me" or "best", pick the best candidate and add it. Otherwise present numbered options.

For a requested loop that should start at ranked non-private parking, use `route.search_parking_anchors` and then call `route.generate_routes` with `generation_mode: "loop"` and the selected parking coordinates as `start`. There is no `route.generate_loop` tool; never invent a specialized loop tool name.

For "your choice", "best", or "nearest", call `route.search_cached_pois` and then `route.add_poi_stop` for the selected candidate in the same turn. A search result is not an added stop. Use `route.search_parking_anchors` for ranked non-private starts, and `route.plan_water_stops` or `route.plan_poi_stops` for repeated stop cadence.

## Postconditions

- Candidates include route-relative distance/position and ranking rationale.
- A POI is never described as added until the add/edit result confirms it.
- Mandatory stop cadence uses an ingredient or multi-point plan rather than disconnected searches.
