---
name: route-weather
description: Weather analysis and weather visualization workflow for route sessions. Use for rain, wind, headwind/tailwind, gusts, temperature, heat, UV, cloud cover, weather windows, start time assumptions, and weather maps/cards.
---

# Route Weather

## Use when

Use for weather analysis or visuals tied to route position and rider/runner/driver timing.

## Do not use when

Do not use for general climate questions or render a weather image when the user asked only for a textual forecast.

Analyze first, render second.

## Workflow

1. Call `route.analyze_weather` for any non-trivial weather question.
   For a combined weather-plus-cycling-ETA request, call it before `route.evaluate_cycling_performance`; the performance tool is not a substitute for route weather evidence.
2. Preserve activity type, start time, speed, and duration assumptions in the session.
3. Render the metric the analysis says matters most. Do not render rain when rain is negligible unless the user asks for rain.
4. Use whole-route visuals unless the user explicitly asks to zoom.
5. For "wind and heat", make separate wind/headwind and temperature visuals.

The only weather tools in this workflow are `route.analyze_weather` and, when the user requests an image, map, card, or visual, `route.render_weather_image`. Do not invent alternate weather-render tool names. For "worst headwind section on a satellite map", call `route.analyze_weather` first and then `route.render_weather_image` with the strongest-headwind selector and satellite map mode.

Use weather selectors such as strongest headwind, strongest tailwind, strongest crosswind, rainiest, hottest, or coldest only when needed.

## Postconditions

- Start time, activity, speed, duration, source, and inferred assumptions are explicit.
- The rendered metric matches the analyzed dominant issue or the user’s named metric.
- A zoomed result identifies its start/end distance span and preserves whole-route context where supported.
