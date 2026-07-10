---
name: route-weather
description: Weather analysis and weather visualization workflow for route sessions. Use for rain, wind, headwind/tailwind, gusts, temperature, heat, UV, cloud cover, weather windows, start time assumptions, and weather maps/cards.
---

# Route Weather

Analyze first, render second.

## Workflow

1. Call `route.analyze_weather` for any non-trivial weather question.
2. Preserve activity type, start time, speed, and duration assumptions in the session.
3. Render the metric the analysis says matters most. Do not render rain when rain is negligible unless the user asks for rain.
4. Use whole-route visuals unless the user explicitly asks to zoom.
5. For "wind and heat", make separate wind/headwind and temperature visuals.

Use weather selectors such as strongest headwind, strongest tailwind, strongest crosswind, rainiest, hottest, or coldest only when needed.

