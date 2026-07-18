# Route Generator MCP Skills

Versioned agent skills, recipes, and evals for using the Route Generator MCP and Route Analysis MCP servers reliably.

This repository is intentionally separate from the API/MCP app. The app exposes its catalog and lock metadata, while compatible agent clients install the skills locally or upload versioned bundles to a hosted skill runtime. The public Chat Lab does not emulate skills by injecting their text into a prompt.

## What Is Included

- `.agents/skills/` contains concise Codex/OpenAI-compatible skills.
- `references/tool-contracts/` captures stable tool-use expectations.
- `references/recipes/` contains concrete workflows for route generation, imports, weather, visuals, POIs, edits, and troubleshooting.
- `evals/cases/` contains mockable regressions plus native Codex skill-selection and tool-planning cases.
- `scripts/` contains local smoke, packaging, catalog, native-runtime, and remote-MCP eval utilities.

## Local Smoke

```bash
python scripts/run_eval_suite.py --mode mock --skills none --out reports/baseline
python scripts/run_eval_suite.py --mode mock --skills default --out reports/default
python scripts/compare_skill_runs.py reports/baseline/results.json reports/default/results.json --out reports/skill_delta.md
python scripts/mcp_smoke.py --mock
python scripts/validate_skills.py
python scripts/generate_skills_lock.py --version 0.2.8
python scripts/build_installable_skills.py --version 0.2.8
python scripts/run_codex_evals.py --out reports/codex-native-final
ROUTE_MCP_ACCESS_TOKEN='<test-only-key>' python scripts/run_remote_mcp_evals.py \
  --base-url http://127.0.0.1:8002 \
  --planning-report reports/codex-native-final/results.json
OPENAI_API_KEY='<transient-provider-key>' \
ROUTE_MCP_ACCESS_TOKEN='<test-only-route-key>' \
python scripts/run_openai_remote_semantic_evals.py --execute \
  --base-url https://staging.example.com \
  --staged-upload-id '<owner-bound-staged-upload-id>' \
  --negative-probes \
  --out reports/openai-remote-semantic.json
```

`run_eval_suite.py` is a fast deterministic planner regression, not evidence of native skill execution. `run_codex_evals.py` invokes `codex exec` in an isolated, read-only session, verifies the selected `.agents/skills/<name>/SKILL.md` was actually opened through native progressive disclosure, and grades its ordered MCP tool plan. `run_remote_mcp_evals.py` is deliberately a **catalog-binding gate only**: it uses the official Python SDK, rejects overlapping catalogs, and proves that every planned tool belongs to exactly one live server.

`run_openai_remote_semantic_evals.py --execute` is the provider-semantic gate. It sends exactly two OpenAI Responses `type: "mcp"` tools, grades actual `mcp_list_tools`/`mcp_call` output items for all 20 scenarios, carries explicit route workspaces across stateful follow-ups, proves undo/redo through remote calls, requires an owner-bound staged upload for the import case, rejects route `function_call` output, and can verify bad-token/unavailable-endpoint failures do not fall back locally. It records non-secret response, server, catalog, skill, workspace, route, artifact, latency, and usage evidence. Omit `--execute` for a redacted plan.

For the combined hosted-Skills lane, pass `--skill-refs-json dist/openai.skills.json --require-native-skills`. A skill counts as read only when the provider response includes both a relevant Shell `SKILL.md` command and a successful Shell output. Do not enable a public model in the hosted-Skills allowlist until this combined gate passes against staging.

## App Integration

Point the API/MCP app at this checkout:

```bash
ROUTE_MCP_SKILLS_DIR=/home/eric/DocumentsFAST/Route_Generator_MCP_Skills
ROUTE_MCP_SKILLS_REPO_URL=https://github.com/Esemianczuk/Route_Generator_MCP_Skills
```

The API reads catalog and `dist/skills.lock.json` metadata only. Hosted OpenAI skills require separately uploaded provider skill IDs and a model that supports both MCP and Skills; until that lane is certified, the Chat Lab reports skills as disabled. No provider API keys or account-specific hosted skill IDs belong in this repo.

To create provider-ready, self-contained zip files, run `build_installable_skills.py`. `upload_openai_skills.py` is dry-run by default and writes account-specific upload results only under ignored `dist/` files when explicitly executed.
