# MCP Skills Guide

The skill bundle is a thin, versioned instruction layer for agent clients. It does not replace MCP tools; it teaches the model which tool family to choose, how to preserve session state, and how to avoid repeated mistakes such as generating a new route for a summary question or rendering rain maps when wind is the actual weather issue.

## Recommended Client Behavior

- Load the pinned skill lock at startup.
- Mount only provider-native skill references or local skill folders supported by the host.
- Show skill selection/usage alongside tool calls.
- Keep route ids and artifacts in backend session state; do not require users to paste raw ids.
- Never present prompt injection as native skill execution.
- Treat `scripts/run_eval_suite.py` as deterministic planner coverage only. Use `scripts/run_codex_evals.py` for native Codex progressive-disclosure evidence and retain its per-case event logs.
- Run `scripts/run_remote_mcp_evals.py` only against actual Streamable HTTP endpoints with a test token and the completed 20-case Codex report. It rejects unknown tools, catalog overlap, incomplete plans, and the old synthetic mock-success path; stateful route output remains an API/runtime gate.

## Route Resources

Future clients can expose these resources:

- `route://guides/skills-and-external-recipes`
- `route://guides/ingredient-planning`
- `route://guides/local-poi-workflows`
- `route://guides/weather-and-performance`
