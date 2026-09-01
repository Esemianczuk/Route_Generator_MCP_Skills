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

- Use `climb_ids` for explicit selections and `climb_needs` for delegated selection in `route.plan_ingredient_options`. Mixed road, POI, water, and climb requirements belong in the same plan.
- Treat an unavailable climb or an explicit graph mismatch as infeasible. A historical ingredient whose graph identity is honestly `unverified` may proceed only with its immutable ordered arcs plus dense entry-to-summit controls, and the final answer must disclose that fallback rather than calling the binding exact. Do not reconstruct a missing ingredient from coordinates or silently substitute another climb.
- Call `route.generate_multi_point_route` once with only the returned `ingredient_plan_ref` arguments.
- Inclusion requires successful directed verification: entry precedes summit, the route covers the dense controls and enough of the climb distance, and net progress is uphill. Exact graph bindings must match; an unavailable historical fingerprint remains explicitly unverified and is never presented as exact. Report the dataset identity when it is useful for reproducibility.
