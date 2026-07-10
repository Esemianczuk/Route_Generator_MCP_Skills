from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, body.strip()


def parse_openai_yaml(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    in_interface = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() == "interface:":
            in_interface = True
            continue
        if line and not line.startswith(" ") and line.strip().endswith(":"):
            in_interface = False
        if not in_interface or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def git_commit(root: Path) -> str | None:
    try:
        return subprocess.check_output(["git", "-C", str(root), "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return None


def catalog(root: Path | None = None) -> dict[str, Any]:
    root = root or repo_root()
    skills_dir = root / ".agents" / "skills"
    skills: list[dict[str, Any]] = []
    for skill_dir in sorted(skills_dir.glob("*")):
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue
        meta, body = parse_frontmatter(skill_file.read_text(encoding="utf-8"))
        interface = parse_openai_yaml(skill_dir / "agents" / "openai.yaml")
        skills.append({
            "name": meta.get("name") or skill_dir.name,
            "description": meta.get("description") or "",
            "body": body,
            "display_name": interface.get("display_name") or meta.get("name") or skill_dir.name,
            "short_description": interface.get("short_description") or "",
            "default_prompt": interface.get("default_prompt") or "",
            "path": str(skill_dir.relative_to(root)),
        })
    return {
        "repo": "Route_Generator_MCP_Skills",
        "commit": git_commit(root),
        "skill_count": len(skills),
        "skills": skills,
    }

