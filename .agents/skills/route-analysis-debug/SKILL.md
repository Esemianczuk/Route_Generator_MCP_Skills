---
name: route-analysis-debug
description: Route analysis and debugging skill for road names, surfaces, traffic, curviness, scenic scores, climbs, off-network spans, OSRM navigation, and route-quality diagnostics. Use when users ask why a route looks odd, what roads it uses, what sections are paved/unpaved, whether it includes a road, or why generation fell short.
---

# Route Analysis Debug

Analyze stored route data before guessing.

## Workflow

1. Call `route.summarize_route` for route identity and stored data availability.
2. Use section-specific analysis tools for surfaces, road/path split, climbs/rises, OSRM road names, scenic/traffic/curviness attributes, or off-network spans.
3. If the user asks to avoid or fix a section, isolate the span first, then use an edit/regeneration tool.
4. State confidence and missing data plainly.

Never claim scenic/traffic/surface data is unavailable until a summary/analysis tool confirms it.

