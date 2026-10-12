#!/usr/bin/env python3
"""Verify release-asset names, hashes and basic MP4 container structure."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import struct


def digest(path: pathlib.Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def atoms(path: pathlib.Path) -> set[bytes]:
    found: set[bytes] = set()
    size = path.stat().st_size
    with path.open("rb") as stream:
        offset = 0
        while offset + 8 <= size:
            stream.seek(offset)
            header = stream.read(16)
            length, kind = struct.unpack(">I4s", header[:8])
            header_size = 8
            if length == 1:
                length = struct.unpack(">Q", header[8:16])[0]
                header_size = 16
            elif length == 0:
                length = size - offset
            if length < header_size or offset + length > size:
                raise ValueError(f"invalid atom at byte {offset}")
            found.add(kind)
            offset += length
    if offset != size:
        raise ValueError(f"trailing bytes after atom boundary: {size - offset}")
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("asset_directory", type=pathlib.Path)
    parser.add_argument(
        "--manifest",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parents[1] / "videos" / "RELEASE-ASSETS.json",
    )
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    results = []
    for item in manifest["assets"]:
        path = args.asset_directory / item["file"]
        if not path.is_file():
            raise FileNotFoundError(path)
        actual_hash = digest(path)
        if actual_hash != item["sha256"]:
            raise ValueError(f"hash mismatch: {path.name}")
        top_level = atoms(path)
        if not {b"ftyp", b"moov", b"mdat"}.issubset(top_level):
            raise ValueError(f"missing MP4 atoms: {path.name}: {top_level}")
        payload = path.read_bytes()
        if b"avc1" not in payload or b"mp4a" not in payload:
            raise ValueError(f"expected H.264/AAC descriptors missing: {path.name}")
        results.append({"file": path.name, "bytes": path.stat().st_size, "sha256": actual_hash})
    print(json.dumps({"status": "pass", "assets": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

