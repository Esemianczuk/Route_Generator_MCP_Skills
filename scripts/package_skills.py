#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tarfile
from pathlib import Path

from skill_catalog import catalog, repo_root


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default="0.1.0")
    parser.add_argument("--out", default="dist")
    args = parser.parse_args()
    root = repo_root()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    manifest = catalog(root)
    manifest["version"] = args.version
    (out / "catalog.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    archive = out / f"route-generator-mcp-skills-{args.version}.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        for rel in [".agents", "references", "docs", "README.md", "LICENSE", "AGENTS.md"]:
            path = root / rel
            if path.exists():
                tar.add(path, arcname=rel)
    print(archive)


if __name__ == "__main__":
    main()

