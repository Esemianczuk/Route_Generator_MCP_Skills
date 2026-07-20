---
name: route-visuals-3d
description: Visual rendering skill for 2D maps, 3D hill-profile ribbons, 3D terrain cutouts, satellite floors, zooming, highlighting route portions, and selecting the correct visual tool. Use for any map/image/visual/zoom/terrain/satellite/topo/hill-profile request.
---

# Route Visuals 3D

## Use when

Use only when the user requests an image, map, visual comparison, zoom, highlight, satellite/topo view, 3D profile ribbon, or actual 3D terrain.

## Do not use when

Do not render imagery for a text-only analysis request, and do not use terrain rendering for a profile-ribbon request or vice versa.

Choose the visual family by intent.

## Tool Choice

- Top-down map, satellite, streets, topo, relief: `route.render_map_image`.
- Highlighted graph plus map or 3D elevation ribbon: `route.render_highlight_image`.
- Actual ground/terrain cutout, Google Earth style, route draped on terrain: `route.render_terrain_image`.
- Weather visuals: `route.render_weather_image`.

Use `zoom_mode` or selection framing only when the user asks to zoom/crop/hug/focus. Whole-route requests should stay whole-route with selected spans highlighted.

For inferred trail-like portions, use `route.render_highlight_image` with `highlight_attribute: "singletrack"`. Use `highlight_selector: "all"` for route-wide context or `"longest"` plus `zoom_to_selection: true` only when the user asks to inspect/zoom the most likely section. Keep the label “likely singletrack”; do not present it as a confirmed trail grade.

For "3D terrain" do not use the hill-profile ribbon. For "hill profile" do not use the terrain cutout unless the user asks for terrain.

## Postconditions

- Exactly one visual family is used per requested image unless comparison is explicit.
- Framing matches whole-route versus zoomed selection intent.
- The returned artifact, route, selection, basemap, and highlight are identified from tool output.
