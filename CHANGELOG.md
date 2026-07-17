# Changelog

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
