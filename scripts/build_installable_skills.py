#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

from generate_skills_lock import build_lock
from skill_catalog import repo_root


def _write_zip(skill_dir: Path, destination: Path) -> None:
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(skill_dir.rglob("*")):
            if not path.is_file():
                continue
            relative = Path(skill_dir.name) / path.relative_to(skill_dir)
            info = zipfile.ZipInfo(str(relative), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o644 & 0xFFFF) << 16
            archive.writestr(info, path.read_bytes())


def main() -> None:
    parser = argparse.ArgumentParser(description="Build deterministic, self-contained skill zip files.")
    parser.add_argument("--version", default="0.3.0")
    parser.add_argument("--out", type=Path, default=Path("dist/installable"))
    args = parser.parse_args()
    root = repo_root()
    output = args.out if args.out.is_absolute() else root / args.out
    output.mkdir(parents=True, exist_ok=True)
    lock = build_lock(root, args.version)
    for skill_dir in sorted((root / ".agents" / "skills").iterdir()):
        if skill_dir.is_dir():
            _write_zip(skill_dir, output / f"{skill_dir.name}-{args.version}.zip")
    (output / "skills.lock.json").write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"skill_count": len(lock["skills"]), "output": str(output), "bundle_sha256": lock["bundle_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
