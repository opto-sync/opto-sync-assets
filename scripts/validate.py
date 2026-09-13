#!/usr/bin/env python3
"""Validate that every exported asset is present, in-tree, and digest-bound.

Consumers (for example the Flutter launcher-icon build) must verify
`branding/app-logo.png` against `asset-manifest.json` before deriving platform
assets. This script is the repository-side half of that contract.
"""
from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from pathlib import Path

PACKAGE = "opto-sync/opto-sync-assets"
REQUIRED_KEYS = {
    "path",
    "mediaType",
    "sha256",
    "bytes",
    "width",
    "height",
    "role",
    "brandApproval",
}
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

root = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"asset package contract: {message}", file=sys.stderr)
    sys.exit(1)


manifest = json.loads((root / "asset-manifest.json").read_text(encoding="utf-8"))
if set(manifest) != {"schemaVersion", "package", "assets"}:
    fail("unexpected top-level manifest keys")
if manifest["schemaVersion"] != 1:
    fail("unsupported schemaVersion")
if manifest["package"] != PACKAGE:
    fail("package identity mismatch")
assets = manifest["assets"]
if not isinstance(assets, list) or not assets:
    fail("assets must be a non-empty list")

listed: set[Path] = set()
for asset in assets:
    if not isinstance(asset, dict) or set(asset) != REQUIRED_KEYS:
        fail(f"asset entry keys must be exactly {sorted(REQUIRED_KEYS)}")
    relative = asset["path"]
    if not isinstance(relative, str) or relative.startswith("/") or ".." in Path(relative).parts:
        fail(f"asset path must be relative and in-tree: {relative!r}")
    path = root / relative
    if path in listed:
        fail(f"duplicate asset entry: {relative}")
    listed.add(path)
    if path.is_symlink() or not path.is_file():
        fail(f"missing or non-regular asset: {relative}")
    if not path.resolve().is_relative_to(root.resolve()):
        fail(f"asset escapes the repository: {relative}")
    if not isinstance(asset["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", asset["sha256"]):
        fail(f"sha256 must be 64 lowercase hex characters: {relative}")
    data = path.read_bytes()
    if len(data) != asset["bytes"]:
        fail(f"byte length drift: {relative}")
    if hashlib.sha256(data).hexdigest() != asset["sha256"]:
        fail(f"sha256 drift: {relative}")
    if asset["mediaType"] != "image/png":
        fail(f"unsupported media type: {asset['mediaType']}")
    if data[:8] != PNG_SIGNATURE or data[12:16] != b"IHDR":
        fail(f"not a PNG image: {relative}")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (asset["width"], asset["height"]):
        fail(f"declared dimensions drift: {relative}")
    if asset["role"] == "app-launcher-source" and (width != height or width < 1024):
        fail(f"launcher source must be square and at least 1024px: {relative}")
    if asset["brandApproval"] not in {"pending", "approved"}:
        fail(f"brandApproval must be pending or approved: {relative}")

for candidate in sorted((root / "branding").rglob("*")):
    if candidate.is_file() and candidate not in listed:
        fail(f"unlisted exported asset: {candidate.relative_to(root)}")

print("asset package contract: valid")
