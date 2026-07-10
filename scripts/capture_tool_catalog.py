#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from mcp_smoke import MOCK_TOOLS


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--out", default="reports/tool_catalog.json")
    args = parser.parse_args()
    if not args.mock:
        raise SystemExit("Use --mock unless a concrete MCP client transport is configured.")
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"tools": [{"name": tool} for tool in MOCK_TOOLS]}, indent=2), encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()

