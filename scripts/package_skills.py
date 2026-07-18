#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_installable_skills import _write_zip
from generate_skills_lock import build_lock
from skill_catalog import repo_root


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default="0.3.2")
    parser.add_argument("--out", default="dist")
    args = parser.parse_args()
    root = repo_root()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    lock = build_lock(root, args.version)
    installable = out / "installable"
    installable.mkdir(parents=True, exist_ok=True)
    for skill_dir in sorted((root / ".agents" / "skills").iterdir()):
        if skill_dir.is_dir():
            _write_zip(skill_dir, installable / f"{skill_dir.name}-{args.version}.zip")
    lock_path = out / "skills.lock.json"
    lock_path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    print(lock_path)


if __name__ == "__main__":
    main()
