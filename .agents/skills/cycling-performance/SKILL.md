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

Pass explicit user values: FTP, rider weight, bike type, tire type, handling skill, bottle count/size, drink mix, departure time, and weather inclusion. Let the tool infer defaults only when the user does not specify them.

Request chart imagery for ETA/speed/hydration. Request map imagery only when the user asks where on the route, support locations, slow sections, or timing markers should be shown.

Compare setups with separate scenario inputs rather than answering from generic deltas.

## Postconditions

- Results state explicit user inputs separately from inferred defaults.
- Compared setups use independent scenarios and explain meaningful deltas.
- Charts and maps are requested only when they answer the user’s actual question.
