---
name: imported-course-analysis
description: Imported GPX/FIT/TCX/course matching, sparse turn-point matching, activity dense-track matching, off-network spans, confidence, and route-session analysis. Use when users drag/drop routes, ask about RideWithGPS/Garmin imports, or need imported course questions answered.
---

# Imported Course Analysis

## Use when

Use when a GPX, FIT, TCX, RideWithGPS, Garmin, activity track, or sparse course has been staged for import or needs matching analysis.

## Do not use when

Do not use for routes already generated and stored normally unless the question is specifically about their import/match quality.

Keep imported courses shape-faithful.

## Workflow

1. Call `route.import_route` with the opaque staged-upload handle supplied by the client and the current client session ID.
2. Read its returned match mode; the tool itself detects sparse route/course points versus dense activity tracks and performs the appropriate matching path.
3. Summarize its confidence, distance, surfaces, off-network spans, and any straight-line or unmatched cuts.
4. When the user asks about trail character, likely singletrack, bike choice, tires, handling, or race setup, call `route.analyze_surfaces` on the stored import. Its `likely_singletrack` result combines non-paved/unknown surface evidence with the calibrated turn-window signature without changing the imported shape.
5. For cycling speed/setup consequences, follow `cycling-performance`; for a requested visual or close-up, follow `route-visuals-3d` with `highlight_attribute: "singletrack"`.
6. Do not reroute imported geometry unless the user asks to edit it.

`route.import_route` is the complete remote MCP import boundary. Do not invent separate import-course, track-density, or course-matching tool calls.

If a map has straight-line cuts, inspect the matching result before presenting it as valid.

## Postconditions

- The imported shape remains authoritative unless the user asks to reroute it.
- Match mode, confidence, off-network spans, surfaces, and distance discrepancy are reported.
- Suspicious straight cuts are identified rather than silently accepted.
- Likely singletrack is reported as an inference alongside, not in place of, match and surface confidence.
