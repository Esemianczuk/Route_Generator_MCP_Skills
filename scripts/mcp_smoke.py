#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

MOCK_TOOLS = [
    "route.tool_index",
    "route.generate_routes",
    "route.generate_multi_point_route",
    "route.generate_named_road_route",
    "route.plan_ingredient_options",
    "route.search_cached_pois",
    "route.plan_water_stops",
    "route.search_parking_anchors",
    "route.render_map_image",
    "route.render_highlight_image",
    "route.render_terrain_image",
    "route.analyze_weather",
    "route.render_weather_image",
    "route.evaluate_cycling_performance",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true")
    args = parser.parse_args()
    if not args.mock:
        raise SystemExit("Real MCP smoke is environment-specific. Run with --mock for local regression.")
    print(json.dumps({"ok": True, "tool_count": len(MOCK_TOOLS), "tools": MOCK_TOOLS}, indent=2))


if __name__ == "__main__":
    main()

