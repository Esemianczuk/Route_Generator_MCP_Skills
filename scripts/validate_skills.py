#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from redaction import redact
from skill_catalog import catalog, parse_frontmatter, parse_openai_yaml, repo_root

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
TOOL_RE = re.compile(r"\broute\.[a-z][a-z0-9_]*\b")
SECRET_RE = re.compile(r"(?:sk-(?:proj-|ant-)?[A-Za-z0-9_-]{12,}|AIza[0-9A-Za-z_-]{20,})")
REQUIRED_HEADINGS = ("## Use when", "## Do not use when", "## Postconditions")
REQUIRED_INTERFACE = ("display_name", "short_description", "default_prompt")


def _known_tools(path: Path | None) -> set[str] | None:
    if path is None or not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    values = payload.get("tools", []) if isinstance(payload, dict) else []
    return {
        str(item.get("name"))
        for item in values
        if isinstance(item, dict) and str(item.get("name") or "").startswith("route.")
    }


def validate_all(root: Path, tool_catalog: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    descriptions: dict[str, str] = {}
    known_tools = _known_tools(tool_catalog)
    skills_root = root / ".agents" / "skills"
    skill_dirs = sorted(item for item in skills_root.iterdir() if item.is_dir()) if skills_root.exists() else []

    for skill_dir in skill_dirs:
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            errors.append(f"{skill_dir.name}: missing SKILL.md")
            continue
        raw = skill_file.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(raw)
        name = str(meta.get("name") or "")
        description = str(meta.get("description") or "").strip()
        if name != skill_dir.name or not NAME_RE.fullmatch(name):
            errors.append(f"{skill_dir.name}: frontmatter name must exactly match its lowercase hyphenated directory")
        if not description:
            errors.append(f"{skill_dir.name}: missing frontmatter description")
        normalized_description = " ".join(description.lower().split())
        if normalized_description in descriptions:
            errors.append(f"{skill_dir.name}: duplicates description from {descriptions[normalized_description]}")
        descriptions[normalized_description] = skill_dir.name
        if len(raw.splitlines()) > 500:
            errors.append(f"{skill_dir.name}: SKILL.md exceeds 500 lines")
        for heading in REQUIRED_HEADINGS:
            if heading not in body:
                errors.append(f"{skill_dir.name}: missing {heading}")
        if SECRET_RE.search(raw):
            errors.append(f"{skill_dir.name}: contains a secret-like value")

        interface = parse_openai_yaml(skill_dir / "agents" / "openai.yaml")
        for field in REQUIRED_INTERFACE:
            if not str(interface.get(field) or "").strip():
                errors.append(f"{skill_dir.name}: agents/openai.yaml missing interface.{field}")

        for target in LINK_RE.findall(body):
            if "://" in target or target.startswith("#"):
                continue
            if ".." in Path(target).parts:
                errors.append(f"{skill_dir.name}: reference escapes the installable skill folder: {target}")
                continue
            if not (skill_dir / target).resolve().is_file():
                errors.append(f"{skill_dir.name}: unresolved reference: {target}")

        referenced_tools = set(TOOL_RE.findall(raw))
        if known_tools is not None:
            for tool in sorted(referenced_tools - known_tools):
                errors.append(f"{skill_dir.name}: references tool absent from catalog: {tool}")
        elif referenced_tools:
            warnings.append(f"{skill_dir.name}: tool dependencies were not checked against a captured catalog")

    if not skill_dirs:
        errors.append("no skills found under .agents/skills")
    if not errors and len(catalog(root).get("skills", [])) != len(skill_dirs):
        errors.append("skill catalog omitted one or more skill directories")
    return {
        "ok": not errors,
        "skill_count": len(skill_dirs),
        "errors": errors,
        "warnings": sorted(set(warnings)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate installable Route Generator skills.")
    parser.add_argument("--tool-catalog", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = redact(validate_all(repo_root(), args.tool_catalog))
    print(json.dumps(result, indent=2) if args.json or not result["ok"] else f"Validated {result['skill_count']} skills.")
    if not result["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
