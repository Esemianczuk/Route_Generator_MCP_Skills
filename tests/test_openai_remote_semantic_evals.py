from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_openai_remote_semantic_evals import _load_cases, build_remote_tools, build_response_body, extract_evidence, grade_case


def test_remote_payload_has_exactly_two_mcp_tools_and_no_function_tools() -> None:
    body = build_response_body(
        model="gpt-5.4-mini",
        prompt="Tell me about this route.",
        generator_url="https://example.test/mcp/route-generator",
        analysis_url="https://example.test/mcp/route-analysis",
        route_token="route-secret",
        previous_response_id="resp_123",
        skill_refs=None,
        reasoning_effort="medium",
    )

    assert [tool["type"] for tool in body["tools"]] == ["mcp", "mcp"]
    assert [tool["server_label"] for tool in body["tools"]] == ["route_generator", "route_analysis"]
    assert body["previous_response_id"] == "resp_123"
    assert all(tool["authorization"] == "route-secret" for tool in body["tools"])
    assert not any(tool["type"] == "function" for tool in body["tools"])


def test_native_payload_places_shell_before_exactly_two_mcp_tools() -> None:
    tools = build_remote_tools(
        "https://example.test/mcp/route-generator",
        "https://example.test/mcp/route-analysis",
        "route-secret",
        [{"name": "route-weather", "skill_id": "skill_123", "version": 7}],
    )

    assert [tool["type"] for tool in tools] == ["shell", "mcp", "mcp"]
    assert tools[0]["environment"]["skills"] == [
        {"type": "skill_reference", "skill_id": "skill_123", "version": "7"}
    ]


def test_evidence_uses_actual_mcp_items_and_rejects_function_calls() -> None:
    evidence = extract_evidence(
        {
            "id": "resp_123",
            "model": "gpt-5.4-mini",
            "output": [
                {"type": "mcp_list_tools", "server_label": "route_generator", "tools": []},
                {"type": "mcp_list_tools", "server_label": "route_analysis", "tools": []},
                {
                    "type": "mcp_call",
                    "server_label": "route_analysis",
                    "name": "route.summarize_route",
                    "arguments": '{"route_workspace_id":"RG-TEST"}',
                    "output": '{"workspace":{"route_workspace_id":"RG-TEST"},"route_id":"rt_test"}',
                },
                {"type": "function_call", "name": "route_generate_routes"},
                {
                    "type": "shell_call",
                    "call_id": "shell_1",
                    "action": {"commands": ["cat /skills/route-generator-core/SKILL.md"]},
                },
                {
                    "type": "shell_call_output",
                    "call_id": "shell_1",
                    "output": [{"outcome": {"type": "exit", "exit_code": 0}}],
                },
            ],
        },
        ["route-generator-core"],
    )

    assert evidence.mcp_list_servers == {"route_generator", "route_analysis"}
    assert [item["tool"] for item in evidence.mcp_calls] == ["route.summarize_route"]
    assert evidence.workspace_ids == {"RG-TEST"}
    assert evidence.route_ids == {"rt_test"}
    assert evidence.function_calls == ["route_generate_routes"]
    assert evidence.skill_reads == {"route-generator-core"}

    graded = grade_case(
        {
            "id": "002-summary-followup",
            "prompt": "Tell me about it.",
            "must_call": ["route.summarize_route"],
            "must_not_call": ["route.generate_routes"],
            "expected_skill": "route-generator-core",
        },
        evidence,
        expected_skill_read=True,
    )
    assert graded["ok"] is False
    assert graded["function_calls"] == ["route_generate_routes"]


def test_case_grading_requires_expected_remote_calls_and_skill_read() -> None:
    evidence = extract_evidence(
        {
            "id": "resp_456",
            "output": [
                {
                    "type": "mcp_call",
                    "server_label": "route_analysis",
                    "name": "route.analyze_weather",
                    "output": "{}",
                }
            ],
        },
        ["route-weather"],
    )
    graded = grade_case(
        {
            "id": "008-weather-headwind",
            "prompt": "Show wind.",
            "must_call": ["route.analyze_weather", "route.render_weather_image"],
            "must_not_call": [],
            "expected_skill": "route-weather",
        },
        evidence,
        expected_skill_read=True,
    )

    assert graded["ok"] is False
    assert graded["missing_expected_tools"] == ["route.render_weather_image"]
    assert graded["skill_read_missing"] is True


def test_case_grading_enforces_tool_order_and_exact_call_counts() -> None:
    evidence = extract_evidence(
        {
            "id": "resp_complex_route",
            "output": [
                {
                    "type": "mcp_call",
                    "server_label": "route_generator",
                    "name": "route.geocode_locations",
                    "output": "{}",
                },
                {
                    "type": "mcp_call",
                    "server_label": "route_generator",
                    "name": "route.plan_ingredient_options",
                    "output": "{}",
                },
                {
                    "type": "mcp_call",
                    "server_label": "route_generator",
                    "name": "route.generate_multi_point_route",
                    "output": "{}",
                },
            ],
        },
        [],
    )
    case = {
        "id": "complex-route",
        "prompt": "Build it.",
        "must_call": [
            "route.geocode_locations",
            "route.plan_ingredient_options",
            "route.generate_multi_point_route",
        ],
        "must_call_in_order": [
            "route.geocode_locations",
            "route.plan_ingredient_options",
            "route.generate_multi_point_route",
        ],
        "exact_call_counts": {
            "route.plan_ingredient_options": 1,
            "route.generate_multi_point_route": 1,
        },
        "must_not_call": ["route.generate_routes", "route.plan_water_stops"],
        "expected_skill": "route-ingredient-planning",
    }

    assert grade_case(case, evidence, expected_skill_read=False)["ok"] is True

    evidence.mcp_calls.append(
        {
            "tool": "route.generate_multi_point_route",
            "server_label": "route_generator",
            "arguments": {},
            "ok": True,
            "error": None,
        }
    )
    graded = grade_case(case, evidence, expected_skill_read=False)
    assert graded["ok"] is False
    assert graded["exact_call_count_mismatches"]["route.generate_multi_point_route"] == {
        "expected": 1,
        "actual": 2,
    }


def test_complex_route_cases_encode_preplan_and_existing_route_split() -> None:
    cases = _load_cases(ROOT)
    new_route = cases["004-water-stops"]
    assert "100 mi scenic cycling route" in new_route["prompt"]
    assert new_route["must_call_in_order"] == [
        "route.geocode_locations",
        "route.plan_ingredient_options",
        "route.generate_multi_point_route",
    ]
    assert new_route["exact_call_counts"]["route.generate_multi_point_route"] == 1
    assert "route.plan_water_stops" in new_route["must_not_call"]
    assert "route.generate_routes" in new_route["must_not_call"]

    skill_text = (ROOT / ".agents" / "skills" / "route-ingredient-planning" / "SKILL.md").read_text(encoding="utf-8")
    assert "`route.plan_water_stops` and `route.plan_poi_stops` require an existing stored route" in skill_text
    assert "exactly one `route.generate_multi_point_route` call" in skill_text
    assert "must not be called manually by the model" in skill_text


def test_single_image_cases_require_exactly_one_remote_artifact() -> None:
    evidence = extract_evidence(
        {
            "id": "resp_image",
            "output": [
                {
                    "type": "mcp_call",
                    "server_label": "route_analysis",
                    "name": "route.render_weather_image",
                    "output": '{"artifact_id":"art_1"}',
                },
                {
                    "type": "mcp_call",
                    "server_label": "route_analysis",
                    "name": "route.analyze_weather",
                    "output": "{}",
                },
            ],
        },
        [],
    )
    case = {
        "id": "008-weather-headwind",
        "prompt": "Show wind.",
        "must_call": ["route.analyze_weather", "route.render_weather_image"],
        "must_not_call": [],
        "expected_skill": "route-weather",
    }

    assert grade_case(case, evidence, expected_skill_read=False)["ok"] is True
    evidence.artifact_ids.append("art_2")
    graded = grade_case(case, evidence, expected_skill_read=False)
    assert graded["ok"] is False
    assert graded["artifact_count_invalid"] is True
