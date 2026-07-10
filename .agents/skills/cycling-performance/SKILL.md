---
name: cycling-performance
description: Cycling physics, setup, ETA, power, FTP, speed, hydration, sweat, sodium, calories, carbs, tire/bike choice, and rider handling analysis for stored routes. Use whenever a cycling user asks how long, how fast, how hard, what bike/tires, water/fuel needs, or where they will be when.
---

# Cycling Performance

Call `route.evaluate_cycling_performance` before answering cycling physics or nutrition questions.

## Inputs To Preserve

Pass explicit user values: FTP, rider weight, bike type, tire type, handling skill, bottle count/size, drink mix, departure time, and weather inclusion. Let the tool infer defaults only when the user does not specify them.

Request chart imagery for ETA/speed/hydration. Request map imagery only when the user asks where on the route, support locations, slow sections, or timing markers should be shown.

Compare setups with separate scenario inputs rather than answering from generic deltas.

