#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from redaction import redact


def root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for path in sorted((root() / "evals" / "cases").glob("*.yaml")):
        cases.append(json.loads(path.read_text(encoding="utf-8")))
    return cases


def plan_tools(prompt: str, skills: str) -> list[str]:
    text = prompt.lower()
    skilled = skills != "none"
    tools: list[str] = []
    asks_summary = any(word in text for word in ["summarize", "tell me about", "describe"])
    asks_tool_index = "list" in text and "tool" in text
    asks_import = "import" in text or "gpx" in text or "ridewithgps" in text
    asks_regenerate = "regenerate" in text or "full retry" in text
    asks_troubleshooting = any(word in text for word in ["bridge returned", "non-json", "404", "failed", "error"])
    asks_reverse = "reverse" in text and any(word in text for word in ["route", "tour", "active", "current"])
    asks_edit_existing = asks_reverse or any(word in text for word in ["avoid", "don't end up", "do not end up", "reroute around", "add another", "leg to that tour"])
    asks_new_route = any(word in text for word in ["make", "generate", "create", "build"]) and "route" in text
    asks_ordered_anchors = any(
        phrase in text
        for phrase in ["in that order", "mandatory anchors", "explicit mandatory anchors", "passing through", "route through"]
    )
    asks_named_roads = any(word in text for word in ["specific road", "named road", "blue mound", "county road", "hwy", "highway"])
    asks_cycling_performance = any(
        word in text
        for word in ["ftp", "watts", "hydration", "sweat", "bike setup", "tires", "how fast", "how long"]
    ) or (
        any(word in text for word in ["bottle", "water supply", "cycling pace", "mph pace", "kph pace"])
        and any(word in text for word in ["enough", "sufficient", "pace", "evaluate"])
    )
    asks_water_stops = "water" in text and ("stop" in text or "refill" in text) and not asks_cycling_performance
    asks_fuel_stops = any(word in text for word in ["gas", "fuel"]) and any(word in text for word in ["stop", "every", "route"])
    if "list" in text and "tool" in text:
        tools.append("route.tool_index")
    if asks_import:
        tools.append("route.import_route")
    if any(word in text for word in ["geocode", "from ", " to ", "near ", "around ", "in "]):
        if any(place in text for place in ["madison", "port washington", "brookfield", "sturgis", "wisconsin"]):
            tools.append("route.geocode_locations")
    if asks_regenerate:
        tools.append("route.regenerate_routes")
    elif skilled and asks_new_route and asks_ordered_anchors:
        tools.append("route.generate_multi_point_route")
    elif skilled and asks_new_route and (asks_named_roads or asks_water_stops or asks_fuel_stops):
        tools.extend(["route.plan_ingredient_options", "route.generate_multi_point_route"])
    elif asks_named_roads:
        tools.append("route.plan_ingredient_options" if skilled else "route.generate_routes")
        tools.append("route.generate_multi_point_route" if skilled else "route.generate_named_road_route")
    elif asks_water_stops:
        tools.append("route.plan_water_stops" if skilled else "route.search_pois")
        if not skilled and ("route" in text or "from " in text):
            tools.append("route.generate_multi_point_route")
    elif any(word in text for word in ["coffee", "gas", "fuel", "parking", "cafe", "restroom"]) and not asks_cycling_performance:
        if "parking" in text:
            tools.append("route.search_parking_anchors" if skilled else "route.search_pois")
        else:
            tools.append("route.search_cached_pois" if skilled else "route.search_pois")
            if skilled and any(phrase in text for phrase in ["your choice", "choose for me", "best", "nearest"]):
                tools.append("route.add_poi_stop")
        if any(word in text for word in ["route", "to ", "from ", "every"]):
            if "fuel" in text or "gas" in text or "every" in text:
                tools.append("route.generate_multi_point_route")
    elif any(word in text for word in ["make", "generate", "create", "build", "route"]) and not (
        asks_summary or asks_tool_index or asks_import or asks_troubleshooting or asks_edit_existing
    ):
        if "point to point" in text or "leg" in text or "tour" in text:
            tools.append("route.generate_multi_point_route")
        else:
            tools.append("route.generate_routes")
    asks_avoidance = any(word in text for word in ["avoid", "don't end up", "do not end up", "reroute around"]) and (
        "road" in text or "section" in text or "capitol" in text
    )
    if asks_summary:
        tools.append("route.summarize_route" if skilled else "route.generate_routes")
    if asks_avoidance:
        if skilled:
            tools.extend(["route.analyze_osrm_segments", "route.plan_avoidance_edit", "route.apply_avoidance_edit"])
        else:
            tools.append("route.generate_routes")
    if "add another" in text and ("leg" in text or "tour" in text):
        tools.append("route.extend_tour" if skilled else "route.generate_multi_point_route")
    if "weather" in text or "headwind" in text or "rain" in text or "temperature" in text:
        tools.append("route.analyze_weather")
        if "image" in text or "map" in text or "card" in text or "visual" in text or "zoom" in text:
            tools.append("route.render_weather_image")
    if "3d terrain" in text or "terrain cutout" in text or "google earth" in text:
        tools.append("route.render_terrain_image" if skilled else "route.render_highlight_image")
    elif "3d" in text or "hill profile" in text or "biggest climb" in text:
        tools.append("route.render_highlight_image")
    if "2d map" in text or "satellite map" in text or "topo" in text:
        tools.append("route.render_map_image")
    if asks_cycling_performance:
        tools.append("route.evaluate_cycling_performance" if skilled else "route.summarize_route")
    if "undo" in text:
        tools.append("route.undo_tour")
    if "redo" in text:
        tools.append("route.redo_tour")
    if asks_reverse:
        tools.append("route.reverse_route")
    deduped: list[str] = []
    for tool in tools:
        if tool not in deduped:
            deduped.append(tool)
    return deduped


def grade_case(case: dict[str, Any], skills: str) -> dict[str, Any]:
    predicted = plan_tools(case["prompt"], skills)
    expected = case.get("must_call", [])
    forbidden = case.get("must_not_call", [])
    missing = [tool for tool in expected if tool not in predicted]
    forbidden_hit = [tool for tool in forbidden if tool in predicted]
    score = 1.0
    if missing:
        score -= min(0.7, 0.2 * len(missing))
    if forbidden_hit:
        score -= min(0.5, 0.25 * len(forbidden_hit))
    return {
        "id": case["id"],
        "prompt": case["prompt"],
        "expected": expected,
        "predicted_tools": predicted,
        "missing": missing,
        "forbidden_hit": forbidden_hit,
        "score": max(0.0, round(score, 2)),
        "ok": not missing and not forbidden_hit,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["mock", "real"], default="mock")
    parser.add_argument("--skills", choices=["none", "default"], default="default")
    parser.add_argument("--out", default="reports/default")
    args = parser.parse_args()
    if args.mode != "mock":
        raise SystemExit("Real provider evals are intentionally not run by this script yet. Use run_chat_lab_eval.py.")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    results = [grade_case(case, args.skills) for case in load_cases()]
    summary = {
        "mode": args.mode,
        "skills": args.skills,
        "case_count": len(results),
        "pass_count": sum(1 for result in results if result["ok"]),
        "average_score": round(sum(result["score"] for result in results) / max(1, len(results)), 3),
    }
    (out / "results.json").write_text(json.dumps(redact({"summary": summary, "results": results}), indent=2), encoding="utf-8")
    failures = [result for result in results if not result["ok"]]
    (out / "failure_examples.md").write_text(
        "\n".join(f"- {item['id']}: missing={item['missing']} forbidden={item['forbidden_hit']}" for item in failures) or "No failures.\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
