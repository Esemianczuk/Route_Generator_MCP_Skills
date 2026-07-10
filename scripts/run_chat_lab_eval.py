#!/usr/bin/env python3
from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-base-url", default="http://127.0.0.1:8002")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        print(f"Would run Chat Lab evals against {args.api_base_url}.")
        return
    raise SystemExit("Real Chat Lab evals need an authenticated user token; use --dry-run or the UI harness.")


if __name__ == "__main__":
    main()

