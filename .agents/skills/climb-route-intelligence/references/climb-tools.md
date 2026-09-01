# Climb Tool Selection

## Catalog queries

- `route.query_climbs` searches by area, radius, or bounding box and supports category/eligibility filters, exact counts, ordered results, and extrema. Its result separates `total` from the bounded `climbs` list and includes dataset `identity`.
- Unless the user asks otherwise, keep `bicycle_eligible`, `route_ready`, and `is_primary` enabled.
- Use `gain_m` for largest, `max_50m_percent` for steepest, and `fiets` for hardest. Use `distance_m` only when the user asks for the longest climb.
- The route-analysis climb tools analyze a stored route; they do not search the regional climb catalog.

## Selected climbs

- `route.get_climb` resolves one real `climb_id` to its detail and fixed directed ingredient. Use it for inspection, a prior-turn "that one," or explicit-id validation; do not call it for every search result.
- Preserve the catalog's entry/start and exit/summit controls. A fixed directed climb is locked, cannot be reversed, and requires ordered graph-arc traversal.

## Planning and verification

- Use `climb_ids` for explicit selections and `climb_needs` for delegated selection in `route.plan_ingredient_options`. Exact ids and exact requested counts keep `climb_selection_mode: "exact"` (the default). Mixed road, POI, water, and climb requirements also use exact mode in one shared plan.
- Use `climb_selection_mode: "distance_fill"` only for a climb-only target-distance route whose climb count may vary. Send exactly one ranked `climb_needs` entry with `target_count: 1`; the value names the ranking pool, not the final climb count. For a roughly 100-mile Driftless loop, send `min_climb_count: 3`, `max_climb_count: 6`, `climb_candidate_limit: 12`, and `distance_tolerance_ratio: 0.05`. The hard API maximum is 8 selected climbs.
- Distance fill first screens the bounded ranked pool with directed profile-CH entry-to-summit paths, then uses profile-CH connector distances to choose a count and ordering inside the hard distance band. It fails closed when it cannot find a compatible chain; do not substitute a baseline, mutation, straight-line order, or model-built pack.
- Treat an unavailable climb or an explicit graph mismatch as infeasible. A historical ingredient whose graph identity is honestly `unverified` may proceed only with its immutable ordered arcs plus dense entry-to-summit controls, and the final answer must disclose that fallback rather than calling the binding exact. Do not reconstruct a missing ingredient from coordinates or silently substitute another climb.
- Call `route.generate_multi_point_route` once with only the returned owner-bound `ingredient_plan_ref` arguments.
- A distance-fill chain reports cheap CH work as `ch_leg_request_count`/`route_engine_request_count` and reports `expensive_generation_request_count: 0`. Do not describe its internal CH screening, connectors, or stitched final legs as extra expensive generation jobs or extra MCP calls.
- Inclusion requires successful final verification for every selected climb plus the target-distance check: entry precedes summit, the route covers the dense controls and enough of the climb distance, and net progress is uphill. Exact graph bindings must match; an unavailable historical fingerprint remains explicitly unverified and is never presented as exact. A null plan, partial/unverified result, or failed hard distance band is terminal. Report the dataset identity when it is useful for reproducibility.
