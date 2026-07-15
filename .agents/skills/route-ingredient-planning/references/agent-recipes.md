# Ingredient Recipes

## Desired roads

Resolve candidates, call `route.plan_ingredient_options`, present ambiguity when confidence is low, then call `route.generate_named_road_route`. Report included, partial, substituted, and missed roads.

## Mandatory stops

Create/select a baseline, use cached planners first, order feasible stops by route progress, then use `route.generate_multi_point_route`. Report stop names, mile/km positions, spacing warnings, and generation compromises.

## Mixed constraints

Resolve roads, POIs, exclusions, and segment qualities into one ingredient plan before generation. Do not make unrelated searches and hope the final route joins them correctly.
