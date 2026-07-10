---
name: route-ingredient-planning
description: Ingredient planning for routes that must include named roads, desired road classes, water/fuel stop cadence, local POIs, or multiple anchors. Use when a user asks for specific roads, "must ride", "avoid", "water every N miles", fuel-stop tours, or complex route ingredients before generation.
---

# Route Ingredient Planning

Prefer an explicit ingredient plan before trying a large generation.

## Workflow

1. Resolve anchors and requested road/POI ingredients.
2. Call `route.plan_ingredient_options` when there are multiple ingredients, named roads, spacing constraints, or unclear ordering.
3. Use local cached POI planners before live Overpass.
4. Generate with `route.generate_named_road_route` or `route.generate_multi_point_route` once the skeleton is feasible.
5. Report included, partial, missed, and substituted ingredients.

Use the recipe file `../../../../references/recipes/agent-recipes.md` for multi-stop and desired-road flows.

