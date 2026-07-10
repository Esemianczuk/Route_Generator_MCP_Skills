---
name: route-editing-tour
description: Tour editing, add/remove/replace legs, split/merge routes, undo/redo, avoid roads, exclusion zones, reroute around sections, and preserving analysis state across edited route versions. Use for any route manipulation after generation or import.
---

# Route Editing Tour

Prefer the smallest edit that satisfies the request.

## Workflow

1. Identify the active route/tour and target span.
2. For add-stop/road-avoid edits, isolate the span before changing it.
3. Use CH-less edits for short local reroutes and multi-point generation for long or ingredient-heavy edits.
4. After edits, summarize new route alias/id, distance delta, changed span, and available undo.
5. Use `route.undo_tour` and `route.redo_tour` only for explicit undo/redo requests.

Keep generated tours as new versions with lineage rather than overwriting hidden state.

