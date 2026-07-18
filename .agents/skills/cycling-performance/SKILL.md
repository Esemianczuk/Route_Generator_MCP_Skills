---
name: cycling-performance
description: Cycling physics, setup, ETA, power, FTP, speed, hydration, sweat, sodium, calories, carbs, tire/bike choice, and rider handling analysis for stored routes. Use whenever a cycling user asks how long, how fast, how hard, what bike/tires, water/fuel needs, or where they will be when.
---

# Cycling Performance

## Use when

Use for cycling ETA, speed, power, rider/bike/tire comparison, handling, hydration, sodium, calories, carbs, or rider-position-over-time questions on a stored route.

## Do not use when

Do not use for running/driving estimates or generic route summaries that do not ask about cyclist performance.

Call `route.evaluate_cycling_performance` before answering cycling physics or nutrition questions.

## Inputs To Preserve

Pass explicit user values: requested average pace, FTP, rider weight, bike type, tire type, handling skill, bottle count/size, drink mix, departure time, ambient temperature/humidity/wind, and weather inclusion. Use `average_speed_mph`/`average_speed_kph` for a user-prescribed pace and `temperature_f`/`temperature_c` for stated conditions that are not a forecast. Let the tool infer defaults only when the user does not specify them. Do not fall back to hand-estimated hydration or timing while a stored route is available.

For a forecast-aware ETA, first follow `route-weather` and call `route.analyze_weather`, then call `route.evaluate_cycling_performance` with `include_weather: true`, the prescribed pace, and the user's time constraint. Prefer `end_time` for an arrival deadline; `finish_time`, `arrival_time`, and `likely_end_time` are compatible aliases. Do not answer forecast risk from performance output alone.

Request chart imagery for ETA/speed/hydration. Request map imagery only when the user asks where on the route, support locations, slow sections, or timing markers should be shown.

Compare setups with separate scenario inputs rather than answering from generic deltas.

## Postconditions

- Results state explicit user inputs separately from inferred defaults.
- Compared setups use independent scenarios and explain meaningful deltas.
- Charts and maps are requested only when they answer the user’s actual question.
