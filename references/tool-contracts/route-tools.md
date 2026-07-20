# Route Tool Contracts

## Session Discipline

- Direct MCP clients should pass their current session id for follow-up requests about "this route", "latest route", "route 2", weather, images, edits, imports, or comparisons. Provider-managed anonymous chats deliberately keep that identifier in backend state: call the matching bounded workflow tool with omitted identifiers and let it infer the visitor's active route; do not list sessions.
- Use route aliases (`R1`, `R2`) or `route_selector: "active"` before asking users for raw route ids. The schema accepts the backend's active/current/selected/this-route aliases as well as first/latest/shortest/longest/hilliness selectors.
- Call `route.get_session` at most once per turn when continuity must be recovered. Its default response is deliberately compact and includes route lineage, headline metrics, `can_undo`, `undo_target_route_id`, and a terminal completion signal; use `include_raw: true` only for an explicit external-client need. Do not poll it.
- After generation or import, summarize the active route before doing optional follow-ups.
- Present route/workspace IDs as plain identifiers. They are not files or provider-local assets, so never fabricate `sandbox:`, download, or file links for them.
- A route with `ingredient_verification.status: verified` and a satisfied distance check is complete. Report its actual distance without offering another tuning pass unless the user explicitly requested tighter precision.
- Provider-native multi-point generation results use a compact completion envelope: route metrics, verification and stop offsets when present, visual artifact metadata, bounded-attempt metrics, and `completion.follow_up_policy`. When `completion.user_request_complete` is true and `retry_recommended` is false, summarize the delivered result without proposing or calling an unsolicited regeneration, distance tune, or stop reroute. A usable route with `ingredient_verification.status: partial` must remain `completion.status: partial`, `user_request_complete: false`, and `retry_recommended: false`: report the compromise, but do not start a second model-driven generation in the same response. Full diagnostics remain available from the direct Route API.

## Generation Families

- `route.generate_routes`: best-in-area, loop, or point-to-point generation only when a new route has no mandatory POIs/stops/ingredients. Pass `count: 1` for one/single/default and use 2-3 only when the user explicitly requests alternatives or comparison. A successful one-route result is terminal for that response even if a soft preference is imperfect. `criteria.traffic: avoid` is a soft scoring preference below the engine's hard-filter threshold; `strongly_avoid` and `strictly_avoid` are progressively hard constraints and must reflect explicit user wording. `criteria.surface` accepts `gravel`/`dirt` as aliases for `unpaved` and `trail`/`bike_path` as aliases for `path`; pass the user's common term directly rather than spending a retry translating it. The tool accepts advanced top-level `weights`; copy a failed result's `retry_suggestions[].set` there on at most one corrective retry without changing the original mode, distance, units, or count. Never use this tool after `route.plan_ingredient_options`.
- `route.regenerate_routes`: broad retries or changes to an existing route. Pass `based_on_route_id`/`route_id` when known, or pass `route_workspace_id`/`session_id` and the server infers that workspace's active route. Do not manufacture a route id or fail merely because `based_on_route_id` was omitted when active workspace context is present.
- `route.generate_multi_point_route`: ordered anchors, tour legs, water/fuel stop every N miles, or multi-criteria point-to-point tours. Explicit named/geocoded anchors can be passed directly as ordered waypoints without `route.plan_ingredient_options`; call the tool exactly once, and treat `mode` as an alias for `generation_mode`. For an ingredient plan, call it exactly once only when `recommended_next_call` is non-null and `external_generation_call_budget` is one. Provider-native MCP receives a compact, owner-bound `{ingredient_plan_ref: ...}`; pass that object alone and never reconstruct or add waypoints, distance, or fallback packs. The server hydrates the canonical plan, owns up to two same-pack distance calibrations within a three-attempt hard cap, and returns one final stored route. The first distance correction is proportional; when two observed results bracket the target, the final correction interpolates inside that bracket to avoid oscillating between over- and undershoot. Ingredient plans default to a 5% target-distance tolerance. Obey the returned completion envelope and never add a model-driven distance retry to a successful one-route response.
- `route.generate_named_road_route`: desired road-name ingredients. Resolve and report road confidence first.
- `route.plan_ingredient_options`: pre-generation ingredient ordering and feasibility planning when roads, POIs, stop cadence, or mixed discoverable ingredients are requested. Do not call it for plain explicit named/geocoded waypoint anchors. It accepts a structured geocoded area or a named `area_query`/string compatibility input. Area-centered `loop` and `best_in_area` requests use the area center as the planning start, and repeated stops without an explicit target cadence default to evenly spaced interior loop slots; `min_spacing_m` remains a lower bound and does not disable that distribution. Hard-infeasible network packs and partial packs with any unresolved mandatory ingredient are never recommended. A null recommendation or zero generation budget is a hard stop; candidates and option packs are diagnostic, not model-constructible generation arguments.

- `route.undo_tour`: call exactly once for an explicit undo. It returns the parent revision when available. If the active route has no parent revision, it returns a successful structured no-op (`status: no_op`, `changed: false`) together with the unchanged active route instead of surfacing an MCP execution error. Both outcomes are terminal for the turn.

## Local Cached POIs First

Use cached/local Route Intelligence tools before live Overpass:

- `route.search_water_sources` / `route.plan_water_stops`
- `route.search_parking_anchors`
- `route.search_cached_pois` / `route.plan_poi_stops`

`route.search_cached_pois` accepts route-position aliases (`route_portion`, `route_fraction`, `route_distance_m`, `route_mile`, `route_km`) and ranks or filters cached candidates against the active route before numbering them. Do not fall back to live Overpass merely because the user asked for the first half, middle, or a route mile.

Only use `route.search_pois` when the local cached tool reports shortfall, unavailable category, or a specialized tag request.

## Editing Invariants

- `route.reverse_route` resolves the selected route, or the persisted active/latest route when provider-managed context is omitted. Cached engine routes use the engine's legal directional reverse; locally composed or imported routes rebuild the reversed stored shape through Route Intelligence matching. Both paths preserve lineage and attached POIs at reversed route positions, and reject empty results or distance drift outside 0.80-1.20 of the source. On rejection the source remains active; surface the failure instead of describing a new route.
- `route.add_poi_stop` normally stores connector geometry and returns a compact terminal completion envelope. Call it once per selected POI. When that POI was already inserted, it returns `status: already_attached` and `changed: false`; never call it again. When the graph cannot route to a nearby candidate inside the bounded access threshold, it may instead return an immutable `access_only` revision with preserved geometry, a POI marker, `geometry_detour_inserted: false`, and `access_offset_m`. Describe it as a nearby support stop, not as a route-through or detour.

## Visual Families

- `route.render_map_image`: top-down map/satellite/OSM/topo/relief images.
- `route.render_highlight_image`: graph plus highlight map or 3D hill-profile ribbon. Use `view_type: "profile_3d"` for elevation-ribbon profile views.
- For likely singletrack, use `highlight_attribute: "singletrack"`; use `highlight_selector: "all"` for whole-route context and `"longest"` with `zoom_to_selection: true` only for a requested close-up.
- `route.render_terrain_image`: terrain cutout / 3D landscape / route draped on ground.
- `route.render_weather_image`: weather cards, weather maps, or weather 3D profile views.

Ingredient-planned multi-point generation returns a default 3D profile image with regular climb callouts and verified POI markers. Do not issue a second render call unless the user requests a different view or that artifact is missing.

## Cycling Physics

Use `route.evaluate_cycling_performance` for cycling ETA, speed, FTP, bike/tire setup, hydration, sweat, sodium, calories, carbs, handling, and where-the-rider-will-be questions. A user-prescribed pace can be passed as `average_speed_mph`/`average_speed_kph`; the route physics solves for required power and reports whether it reached that pace. Pass stated non-forecast conditions as `temperature_f`/`temperature_c`, optional humidity, and wind. For an arrival deadline, prefer `end_time`; `finish_time`, `arrival_time`, and `likely_end_time` are accepted aliases, just as `start_time` and `likely_start_time` alias `departure_time`. A combined forecast-plus-cycling-ETA request calls `route.analyze_weather` first and `route.evaluate_cycling_performance` second; neither tool substitutes for the other. Do not estimate these directly when a route is stored.

The cycling tool automatically applies the calibrated likely-singletrack detector to unknown/unpaved/dirt geometry and uses MTB Blue physics only on qualifying points. It returns the original `source_surface`, inferred spans, and setup-specific handling risks. `route.analyze_surfaces` exposes the same inference without mutating authoritative surface data. Describe it as likely/inferred rather than a confirmed trail grade, and use explicit `setups` entries for bike/tire/skill comparisons.
