#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default=str(Path.home() / ".agents" / "skills"))
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1] / ".agents" / "skills"
    target = Path(args.target)
    target.mkdir(parents=True, exist_ok=True)
    for skill_dir in source.iterdir():
        if skill_dir.is_dir():
            destination = target / skill_dir.name
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(skill_dir, destination)
            print(destination)


if __name__ == "__main__":
    main()
