# Route Tool Contracts

## Session Discipline

- Always pass the current session id for follow-up requests about "this route", "latest route", "route 2", weather, images, edits, imports, or comparisons.
- Use route aliases (`R1`, `R2`) or `route_selector: "active"` before asking users for raw route ids.
- After generation or import, summarize the active route before doing optional follow-ups.
- Present route/workspace IDs as plain identifiers. They are not files or provider-local assets, so never fabricate `sandbox:`, download, or file links for them.
- A route with `ingredient_verification.status: verified` and a satisfied distance check is complete. Report its actual distance without offering another tuning pass unless the user explicitly requested tighter precision.
- Provider-native ingredient-generation results use a compact completion envelope: route metrics, verification and stop offsets, visual artifact metadata, bounded-attempt metrics, and `completion.follow_up_policy`. When `completion.user_request_complete` is true and `retry_recommended` is false, summarize the delivered result without proposing an unsolicited regeneration, distance tune, or stop reroute. Full diagnostics remain available from the direct Route API.

## Generation Families

- `route.generate_routes`: best-in-area, loop, or point-to-point generation only when a new route has no mandatory POIs/stops/ingredients. Never use it after `route.plan_ingredient_options`.
- `route.generate_multi_point_route`: ordered anchors, tour legs, water/fuel stop every N miles, or multi-criteria point-to-point tours. For an ingredient plan, call it exactly once only when `recommended_next_call` is non-null and `external_generation_call_budget` is one. Provider-native MCP receives a compact, owner-bound `{ingredient_plan_ref: ...}`; pass that object alone and never reconstruct or add waypoints, distance, or fallback packs. The server hydrates the canonical plan, owns up to two same-pack distance calibrations within a three-attempt hard cap, and returns one final stored route. Ingredient plans default to a 5% target-distance tolerance. The MCP accepts string `generation_mode` and integer `variants` only as compatibility aliases for imperfect clients that are not using a plan reference.
- `route.generate_named_road_route`: desired road-name ingredients. Resolve and report road confidence first.
- `route.plan_ingredient_options`: pre-generation ingredient ordering and feasibility planning when many roads/POIs/stops are requested. It accepts a structured geocoded area or a named `area_query`/string compatibility input. Area-centered `loop` and `best_in_area` requests use the area center as the planning start, and repeated stops without an explicit target cadence default to evenly spaced interior loop slots; `min_spacing_m` remains a lower bound and does not disable that distribution. Hard-infeasible network packs and partial packs with any unresolved mandatory ingredient are never recommended. A null recommendation or zero generation budget is a hard stop; candidates and option packs are diagnostic, not model-constructible generation arguments.

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
