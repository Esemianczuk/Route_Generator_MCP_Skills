---
name: route-poi-stops
description: Local cached POI, water, fuel, cafe, restroom, parking, and stop-insertion workflows for Route Generator MCP. Use when users ask to find, add, compare, visualize, or plan stops along routes or tours.
---

# Route POI Stops

Use offline/local cached POI tools first. Live Overpass is a fallback, not the default.

## Tool Priority

- Water/refill: `route.search_water_sources`, then `route.plan_water_stops`.
- Parking/start anchors: `route.search_parking_anchors`.
- Coffee, fuel, restrooms, parks, repairs, scenic, shelters: `route.search_cached_pois`, then `route.plan_poi_stops`.
- Specialized raw OSM tags or cache shortfalls: `route.search_pois`.

When a user says "choose for me" or "best", pick the best candidate and add it. Otherwise present numbered options.

