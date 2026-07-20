---
name: route-analysis-debug
description: Route analysis and debugging skill for road names, surfaces, traffic, curviness, scenic scores, climbs, off-network spans, OSRM navigation, and route-quality diagnostics. Use when users ask why a route looks odd, what roads it uses, what sections are paved/unpaved, whether it includes a road, or why generation fell short.
---

# Route Analysis Debug

## Use when

Use to inspect stored roads, surfaces, paths, climbs, scenic/traffic/curviness scores, OSRM segments, off-network spans, or route-quality anomalies.

## Do not use when

Do not use as a substitute for weather, cycling performance, route creation, or explicit transport-error diagnosis.

Analyze stored route data before guessing.

## Workflow

1. Call `route.summarize_route` for route identity and stored data availability.
2. Use section-specific analysis tools for surfaces, road/path split, climbs/rises, OSRM road names, scenic/traffic/curviness attributes, or off-network spans. `route.analyze_surfaces` also returns calibrated `likely_singletrack` spans when unknown/unpaved/dirt geometry contains the required turn-window signature.
3. If the user asks to avoid or fix a section, isolate the span first, then use an edit/regeneration tool.
4. State confidence and missing data plainly.

Never claim scenic/traffic/surface data is unavailable until a summary/analysis tool confirms it.

Treat likely singletrack as route-shape evidence, not an authoritative trail difficulty tag. Report its distance range, original surface, evidence/confidence, and the MTB Blue physics classification. Use `cycling-performance` for bike/tire/skill consequences instead of estimating them here.

## Postconditions

- Findings identify the route and distance spans they apply to.
- Missing or low-confidence data is stated explicitly.
- Any proposed edit is based on an isolated offending span.
