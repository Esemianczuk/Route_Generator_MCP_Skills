# Route Generator MCP Skills

Versioned agent skills, recipes, and evals for using the Route Generator MCP and Route Analysis MCP servers reliably.

This repository is intentionally separate from the API/MCP app. The app can mount it with `ROUTE_MCP_SKILLS_DIR` and expose a compact default skill bundle to Chat Lab, while external agent clients can install or copy the skills directly.

## What Is Included

- `.agents/skills/` contains concise Codex/OpenAI-compatible skills.
- `references/tool-contracts/` captures stable tool-use expectations.
- `references/recipes/` contains concrete workflows for route generation, imports, weather, visuals, POIs, edits, and troubleshooting.
- `evals/cases/` contains mockable regression cases for tool selection and answer grounding.
- `scripts/` contains local smoke, packaging, catalog, and eval utilities.

## Local Smoke

```bash
python scripts/run_eval_suite.py --mode mock --skills none --out reports/baseline
python scripts/run_eval_suite.py --mode mock --skills default --out reports/default
python scripts/compare_skill_runs.py reports/baseline/results.json reports/default/results.json --out reports/skill_delta.md
python scripts/mcp_smoke.py --mock
python scripts/package_skills.py --version 0.1.0 --out dist
```

## App Integration

Point the API/MCP app at this checkout:

```bash
ROUTE_MCP_SKILLS_DIR=/home/eric/DocumentsFAST/Route_Generator_MCP_Skills
ROUTE_MCP_SKILLS_REPO_URL=https://github.com/Esemianczuk/Route_Generator_MCP_Skills
ROUTE_MCP_DEFAULT_SKILLS_ENABLED=1
```

No provider API keys belong in this repo.

