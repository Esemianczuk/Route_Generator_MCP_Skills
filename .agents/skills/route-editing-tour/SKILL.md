---
name: route-editing-tour
description: Tour editing, add/remove/replace legs, split/merge routes, undo/redo, avoid roads, exclusion zones, reroute around sections, and preserving analysis state across edited route versions. Use for any route manipulation after generation or import.
---

# Route Editing Tour

## Use when

Use after generation/import to add, remove, split, merge, reverse, avoid, reroute, extend, undo, or redo route/tour content.

## Do not use when

Do not use for a new independent route with no relationship to an existing route workspace.

Prefer the smallest edit that satisfies the request.

## Workflow

1. Identify the active route/tour and target span.
2. For add-stop/road-avoid edits, isolate the span before changing it.
3. Use CH-less edits for short local reroutes and multi-point generation for long or ingredient-heavy edits.
4. After edits, summarize new route alias/id, distance delta, changed span, and available undo.
5. Use `route.undo_tour` and `route.redo_tour` only for explicit undo/redo requests.

Use these exact mutation paths:

- Avoid a named road or distance span: `route.analyze_osrm_segments` -> `route.plan_avoidance_edit` -> `route.apply_avoidance_edit`.
- Add a generated conversational leg: `route.geocode_locations` when the destination is text, then `route.extend_tour`.
- Merge, split, keep/remove a window, append, or prepend stored routes: `route.edit_tour`.
- Reverse a route legally: `route.reverse_route`. A successful reverse is a new lineage revision and must remain within the server's distance-drift safety envelope; if it fails that invariant, report the failure and keep the source route active.
- Undo/redo: `route.undo_tour` or `route.redo_tour`.

Do not regenerate the entire route with `route.generate_routes` when a local revision tool can preserve the current route and lineage.

Keep generated tours as new versions with lineage rather than overwriting hidden state.

## Postconditions

- The new route version preserves lineage and reports changed spans and distance delta.
- The active route alias/id is explicit.
- Undo availability is reported without performing undo unless requested.
- A reverse never silently activates a route whose distance drifted beyond the legal-reverse safety envelope.
