# Changelog

## 0.3.11

- Adds fixed cycling-pace solving and explicit ambient temperature/humidity/wind inputs to route-aware hydration and performance analysis.
- Accepts the natural pace aliases models commonly use and aligns active/current route-selector schema values with the backend.
- Strengthens the cycling eval to require one physics call for a 15 mph, 82 F, two-bottle sufficiency question instead of hand estimates.

## 0.3.10

- Keeps provider-chain rollover notes out of visitor intent routing and stops rollover from requesting session polling.
- Routes highway-like/highest-traffic span requests through the localized analysis-and-avoidance edit workflow.
- Makes provider-managed follow-ups use tools' active-route inference before any explicit continuity lookup.

## 0.3.9

- Keeps persisted-route POI planning and local avoidance edits inside bounded tool lanes instead of session polling or accidental regeneration.
- Distinguishes an explicit undo command from edit instructions that merely require undo history to be preserved.
- Documents common generation surface aliases so `gravel`, `dirt`, `trail`, and `bike_path` can be sent directly without a schema-error retry.

## 0.3.8

- Treats compact `route.get_session` continuity results as a one-lookup terminal state instead of polling large revision payloads.
- Makes explicit undo/redo one-call operations and stops after either a successful change or a safe no-op.
- Makes each selected POI insertion terminal and idempotent when the same POI is already attached.
- Strengthens the nearby access-fallback eval to require exactly one POI mutation call.

## 0.3.7

- Routes plain explicit named anchors directly through one multi-point generation call; the POI/road ingredient planner remains required only for discoverable ingredients.
- Treats successful one-route results and their compact completion envelope as terminal for the response, preventing model-driven distance and soft-preference retry loops.
- Documents safe undo no-op behavior and the common multi-point `mode` alias.
- Adds the ordered-named-anchor semantic regression, bringing the mock suite to 25 cases.

## 0.3.2

- Documents bracketed server-side distance calibration so required-stop routes converge instead of oscillating around the requested distance.
- Treats an exhausted but usable verification-partial route as partial without inviting a second model-driven generation call.

## 0.3.1

- Keeps route/workspace IDs as plain identifiers instead of inventing provider-local `sandbox:` links.
- Treats a verified route inside the planner's target-distance tolerance as complete and avoids offering an unnecessary distance retry.

## 0.3.0

- Replaces large planner-argument copying in provider-native MCP with a compact, owner-bound `ingredient_plan_ref` that the server hydrates into the canonical waypoint plan.
- Allows up to two bounded same-pack distance calibrations (three internal attempts total) while preserving exactly one model-visible generation call and one final stored route.

## 0.2.9

- Tightens the default distance tolerance for ingredient-planned routes from 10% to 5% while keeping distance-only correction inside one external MCP generation call.
- Adds a regression case requiring a single model-visible generation call even when the server must calibrate a required-stop route's distance.

## 0.2.8

- Makes the finalized route-analysis arc pass the canonical ascent total while preserving raw profile ascent as a diagnostic when the values differ.
- Requires final chat summaries to copy canonical top-level route metrics and not offer a redundant render when the default profile image was returned.

## 0.2.7

- Makes area-centered `best_in_area` ingredient planning use the same distributed loop-slot semantics as `loop`.
- Treats every unresolved mandatory ingredient as a hard generation stop instead of permitting a partial pack to redefine the user's requested stop count.
- Exposes named-area input resolution in the compact planner result for clearer model and operator diagnostics.

## 0.2.6

- Keeps count-only repeated stops free of model-invented cadence so the planner can distribute them across the requested route distance.
- Treats area-centered `best_in_area` planning like a loop for repeated-stop placement and documents named-area compatibility inputs.
- Extends the Madison water-stop eval to forbid redundant water-source searches after ingredient planning.

## 0.2.5

- Keeps multi-point compatibility aliases simple enough for provider-native structured calls.
- Treats same-pack distance calibration as a bounded server-side recovery, never a second model tool call.
- Extends the Madison water-stop eval to forbid parking-search detours after planning.

## 0.2.4

- Defaults repeated mandatory stops on loops to even interior distance slots when the user did not specify cadence.
- Requires planner arguments to be copied verbatim, forbids ordinary-task `route.tool_index` discovery, and keeps hard-infeasible packs out of recommendations.
- Documents compatibility handling for common multi-point aliases without turning them into extra generation attempts.

## 0.2.3

- Treats a geocoded area center as the anchor for area-only ingredient loops so repeated stops can be distributed and network-checked before generation.
- Makes a null planner recommendation or zero generation budget an explicit hard stop instead of permission to synthesize waypoints or retry generation.
- Adds a semantic eval for a 100-mile Madison-area route with three water stops and exactly one multi-point generation call.

## 0.2.1

- Makes pre-generation ingredient planning mandatory for new routes with required POIs, stop cadence, named roads, or mixed ingredients.
- Adds exact tool-order and generation-count semantic grading for complex route requests.
- Documents network-feasibility reranking and bounded server-side fallback packs without exposing model-driven retry loops.
- Keeps existing-route water and POI planning separate from brand-new route ingredient planning.

## 0.1.0

- Initial Route Generator MCP skill bundle.
- Adds ten focused skills, mock eval harness, tool-catalog capture, packaging, and Chat Lab install helpers.
