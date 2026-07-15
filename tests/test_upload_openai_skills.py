from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from upload_openai_skills import _multipart_zip


def test_hosted_skill_upload_uses_openai_files_array_field(tmp_path: Path) -> None:
    archive = tmp_path / "route-generator-core-0.2.0.zip"
    archive.write_bytes(b"locked-skill-archive")

    body, boundary = _multipart_zip(archive)

    assert f"--{boundary}\r\n".encode() in body
    assert b'name="files[]"' in body
    assert b'name="files"' not in body
    assert f'filename="{archive.name}"'.encode() in body
    assert b"locked-skill-archive" in body
