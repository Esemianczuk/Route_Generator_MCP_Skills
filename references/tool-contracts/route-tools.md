# Route Tool Contracts

## Session Discipline

- Always pass the current session id for follow-up requests about "this route", "latest route", "route 2", weather, images, edits, imports, or comparisons.
- Use route aliases (`R1`, `R2`) or `route_selector: "active"` before asking users for raw route ids.
- After generation or import, summarize the active route before doing optional follow-ups.

## Generation Families

- `route.generate_routes`: best-in-area, loop, or point-to-point generation only when a new route has no mandatory POIs/stops/ingredients. Never use it after `route.plan_ingredient_options`.
- `route.generate_multi_point_route`: ordered anchors, tour legs, water/fuel stop every N miles, or multi-criteria point-to-point tours. For an ingredient plan, call it exactly once only when `recommended_next_call` is non-null and `external_generation_call_budget` is one. Copy the planner-provided arguments exactly; the server owns bounded fallback attempts and returns one final stored route.
- `route.generate_named_road_route`: desired road-name ingredients. Resolve and report road confidence first.
- `route.plan_ingredient_options`: pre-generation ingredient ordering and feasibility planning when many roads/POIs/stops are requested. Area-only loops use the geocoded area center as the planning start. A null recommendation or zero generation budget is a hard stop; candidates and option packs are diagnostic, not model-constructible generation arguments.

## Local Cached POIs First

Use cached/local Route Intelligence tools before live Overpass:

- `route.search_water_sources` / `route.plan_water_stops`
- `route.search_parking_anchors`
- `route.search_cached_pois` / `route.plan_poi_stops`

Only use `route.search_pois` when the local cached tool reports shortfall, unavailable category, or a specialized tag request.

## Visual Families

- `route.render_map_image`: top-down map/satellite/OSM/topo/relief images.
- `route.render_highlight_image`: graph plus highlight map or 3D hill-profile ribbon. Use `view_type: "profile_3d"` for elevation-ribbon profile views.
- `route.render_terrain_image`: terrain cutout / 3D landscape / route draped on ground.
- `route.render_weather_image`: weather cards, weather maps, or weather 3D profile views.

Ingredient-planned multi-point generation returns a default 3D profile image with regular climb callouts and verified POI markers. Do not issue a second render call unless the user requests a different view or that artifact is missing.

## Cycling Physics

Use `route.evaluate_cycling_performance` for cycling ETA, speed, FTP, bike/tire setup, hydration, sweat, sodium, calories, carbs, handling, and where-the-rider-will-be questions. Do not estimate these directly when a route is stored.
