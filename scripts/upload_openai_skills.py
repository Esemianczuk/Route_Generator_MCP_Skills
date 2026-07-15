#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import secrets
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from redaction import redact
from skill_catalog import repo_root


def _multipart_zip(path: Path) -> tuple[bytes, str]:
    boundary = "----route-skill-" + secrets.token_hex(12)
    header = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="files"; filename="{path.name}"\r\n'
        "Content-Type: application/zip\r\n\r\n"
    ).encode("utf-8")
    body = header + path.read_bytes() + f"\r\n--{boundary}--\r\n".encode("utf-8")
    return body, boundary


def _upload(url: str, api_key: str, path: Path) -> dict[str, Any]:
    body, boundary = _multipart_zip(path)
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "route-generator-mcp-skills-uploader/0.2.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:2000]
        raise RuntimeError(f"OpenAI skill upload failed with HTTP {exc.code}: {detail}") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload built skills to the official OpenAI /v1/skills endpoint.")
    parser.add_argument("--execute", action="store_true", help="Perform uploads. Without this flag, print the plan only.")
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    parser.add_argument("--base-url", default="https://api.openai.com/v1")
    parser.add_argument("--input", type=Path, default=Path("dist/installable"))
    parser.add_argument("--out", type=Path, default=Path("dist/openai.skills.json"))
    parser.add_argument("--skill", action="append", default=[])
    args = parser.parse_args()
    root = repo_root()
    input_dir = args.input if args.input.is_absolute() else root / args.input
    archives = sorted(input_dir.glob("*.zip"))
    if args.skill:
        requested = set(args.skill)
        archives = [path for path in archives if any(path.name.startswith(name + "-") for name in requested)]
    if not archives:
        raise SystemExit("No skill archives found. Run build_installable_skills.py first.")
    plan = {"endpoint": args.base_url.rstrip("/") + "/skills", "archives": [path.name for path in archives], "execute": args.execute}
    if not args.execute:
        print(json.dumps(plan, indent=2))
        return
    api_key = os.getenv(args.api_key_env, "").strip()
    if not api_key:
        raise SystemExit(f"{args.api_key_env} is required with --execute.")
    uploaded = [_upload(plan["endpoint"], api_key, path) for path in archives]
    output = args.out if args.out.is_absolute() else root / args.out
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(redact({"endpoint": plan["endpoint"], "skills": uploaded}), indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"uploaded": len(uploaded), "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()
