#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from skill_catalog import catalog, repo_root
from validate_skills import validate_all

TOOL_RE = re.compile(r"\broute\.[a-z][a-z0-9_]*\b")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _commit(root: Path) -> str | None:
    try:
        return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def _skill_entry(skill_dir: Path) -> dict[str, Any]:
    files = [path for path in sorted(skill_dir.rglob("*")) if path.is_file()]
    file_hashes = {str(path.relative_to(skill_dir)): _sha256(path) for path in files}
    encoded = json.dumps(file_hashes, sort_keys=True, separators=(",", ":")).encode("utf-8")
    text = "\n".join(path.read_text(encoding="utf-8") for path in files if path.suffix in {".md", ".yaml", ".yml"})
    return {
        "name": skill_dir.name,
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "files": file_hashes,
        "tool_dependencies": sorted(set(TOOL_RE.findall(text))),
    }


def build_lock(root: Path, version: str) -> dict[str, Any]:
    validation = validate_all(root)
    if not validation["ok"]:
        raise ValueError("Skill validation failed: " + "; ".join(validation["errors"]))
    entries = [_skill_entry(path) for path in sorted((root / ".agents" / "skills").iterdir()) if path.is_dir()]
    skill_catalog = catalog(root)
    compact_catalog = {
        "repo": skill_catalog["repo"],
        "commit": skill_catalog["commit"],
        "skill_count": skill_catalog["skill_count"],
        "skills": [
            {
                "name": item["name"],
                "description": item["description"],
                "display_name": item["display_name"],
                "short_description": item["short_description"],
                "path": item["path"],
            }
            for item in skill_catalog["skills"]
        ],
    }
    payload: dict[str, Any] = {
        "lock_version": 1,
        "bundle_version": version,
        "repo": "Route_Generator_MCP_Skills",
        "repo_commit": _commit(root),
        "formats": ["agentskills.io", "codex-local-skills", "openai-hosted-skills"],
        "runtime_policy": {
            "prompt_injection_allowed": False,
            "native_runtime_required_for_execution_claim": True,
            "required_mcp_servers": ["route-generator", "route-analysis"],
        },
        "skills": entries,
        "catalog": compact_catalog,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload["bundle_sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Create the deterministic route-skill lock file.")
    parser.add_argument("--version", default="0.2.5")
    parser.add_argument("--out", type=Path, default=Path("dist/skills.lock.json"))
    args = parser.parse_args()
    root = repo_root()
    output = args.out if args.out.is_absolute() else root / args.out
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(build_lock(root, args.version), indent=2) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
