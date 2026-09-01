---
name: climb-route-intelligence
description: Search a regional climb catalog, compare climb extrema, inspect a selected climb, or use one or more directed climbs as mandatory route ingredients. Use for Cat/Fiets questions, largest/steepest/hardest climb selection, "add that climb", and climb-chaining route requests; do not use for climbs detected only after a route already exists.
---

# Climb Route Intelligence

## Use when

Use for regional climb counts and rankings, a climb-id detail lookup, or a new route that must traverse selected climbs.

## Do not use when

Do not use catalog search to analyze climbs already present on a stored route; use the route-analysis climb tools for that. Do not turn a general preference for a hilly route into mandatory catalog ingredients unless the user asks for particular, ranked, or chained climbs.

## Workflow

1. Resolve a named area with `route.geocode_locations` unless the request already supplies a radius, bounding box, coordinates, or usable area context. Query the catalog with `route.query_climbs`. Its default routing set is bicycle-eligible, route-ready, primary climbs; widen those filters only when the user asks.
2. Preserve the metric the user named. "Largest" means `gain_m`, "steepest" means `max_50m_percent`, and "hardest" means `fiets`. Fiets is a cycling-oriented climb-difficulty score, not a synonym for elevation gain or maximum grade. For category questions, filter the requested category and report the returned exact `total`; never infer a count from the length of a top-results page.
3. Keep the returned `climb_id` with every selection. Use `route.get_climb` when the user asks for full detail, when a selected id needs its directed route ingredient, or when resolving a conversational reference such as "that one." Do not repeat an area search when the prior result already identifies the climb, and never invent an id.
4. For a new route, pass explicitly selected ids through `climb_ids` on `route.plan_ingredient_options`; use `climb_needs` when the user delegates which qualifying climbs to choose. The planner owns network-feasible ordering with the other route ingredients. Do not sort anchors by straight-line distance, reverse a climb, reduce it to one summit waypoint, generate a baseline first, or mutate a generic route in hopes that it reaches the climbs.
5. For a many-climb distance target, query a bounded eligible shortlist in the requested order metric and let the planner choose/order a feasible ingredient pack. A request such as a roughly 100-mile Driftless loop should still make one external generation call, not one route call per climb.
6. Continue only when the planner returns a non-null `recommended_next_call` and `external_generation_call_budget: 1`. Copy its compact `{ingredient_plan_ref: ...}` arguments verbatim into exactly one `route.generate_multi_point_route` call. A null recommendation or zero budget is a hard stop.
7. Report a climb as incorporated only when returned directed-climb verification passes. Check canonical entry-before-summit order, dense control/distance coverage, and uphill progress. When an exact graph identity is available it must also match; when the historical climb release has no comparable graph identity, disclose the returned unverified-binding warning and rely on the dense directed controls instead. An explicit graph mismatch is a hard failure. Stored-route climb detection alone does not prove that the requested catalog climb was traversed in its required direction.

Read [references/climb-tools.md](references/climb-tools.md) when choosing query metrics, carrying a prior selection, or interpreting directed verification.

## Postconditions

- Informational answers distinguish exact counts from returned top results and name the metric used for each extremum.
- A selected climb keeps its real catalog id and canonical start-to-summit direction.
- Planned routes use a server-owned ingredient plan and exactly one external generation call.
- Final inclusion claims are grounded in directed-climb verification, including direction, dense control/distance coverage, uphill progress, and the strongest graph-binding check available.
