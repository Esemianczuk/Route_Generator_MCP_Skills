---
name: imported-course-analysis
description: Imported GPX/FIT/TCX/course matching, sparse turn-point matching, activity dense-track matching, off-network spans, confidence, and route-session analysis. Use when users drag/drop routes, ask about RideWithGPS/Garmin imports, or need imported course questions answered.
---

# Imported Course Analysis

Keep imported courses shape-faithful.

## Workflow

1. Import the file into the current route session.
2. Detect sparse route/course points versus dense activity tracks.
3. Use turn-point matching for sparse route files and dense matching for activity points.
4. Summarize confidence, distance, surfaces, off-network spans, and any straight-line or unmatched cuts.
5. Do not reroute imported geometry unless the user asks to edit it.

If a map has straight-line cuts, inspect the matching result before presenting it as valid.

