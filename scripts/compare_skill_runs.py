#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline")
    parser.add_argument("candidate")
    parser.add_argument("--out", default="reports/skill_delta.md")
    args = parser.parse_args()
    baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    candidate = json.loads(Path(args.candidate).read_text(encoding="utf-8"))
    base_by_id = {item["id"]: item for item in baseline["results"]}
    lines = ["# Skill Delta", ""]
    lines.append(f"Baseline pass: {baseline['summary']['pass_count']}/{baseline['summary']['case_count']}")
    lines.append(f"Candidate pass: {candidate['summary']['pass_count']}/{candidate['summary']['case_count']}")
    lines.append("")
    lines.append("| Case | Baseline | Candidate | Change |")
    lines.append("| --- | ---: | ---: | ---: |")
    for item in candidate["results"]:
        before = base_by_id[item["id"]]["score"]
        after = item["score"]
        lines.append(f"| {item['id']} | {before:.2f} | {after:.2f} | {after - before:+.2f} |")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(args.out)


if __name__ == "__main__":
    main()

