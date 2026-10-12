#!/usr/bin/env python3
"""Offline structural checks for the public evidence package."""

from __future__ import annotations

import collections
import hashlib
import json
import pathlib
import re
import struct
import sys
import zipfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SENSITIVE = re.compile(
    rb"C:\\Users|/home/|/root/|BEGIN (?:RSA|OPENSSH|EC) PRIVATE KEY|"
    rb"api[_-]?key|access[_-]?token|password|moodscape",
    re.IGNORECASE,
)


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stl_edges(path: pathlib.Path) -> tuple[int, int]:
    data = path.read_bytes()
    triangles: list[tuple[tuple[float, float, float], ...]] = []
    if len(data) >= 84 and 84 + struct.unpack("<I", data[80:84])[0] * 50 == len(data):
        count = struct.unpack("<I", data[80:84])[0]
        for index in range(count):
            offset = 84 + index * 50 + 12
            values = struct.unpack("<9f", data[offset : offset + 36])
            triangles.append(tuple(tuple(round(v, 6) for v in values[i : i + 3]) for i in (0, 3, 6)))
    else:
        vertices = [tuple(round(float(v), 6) for v in match.groups()) for match in re.finditer(
            rb"vertex\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)", data
        )]
        if len(vertices) % 3:
            raise ValueError(f"invalid ASCII STL vertex count: {path}")
        triangles = [tuple(vertices[i : i + 3]) for i in range(0, len(vertices), 3)]

    edges: collections.Counter[tuple[tuple[float, float, float], tuple[float, float, float]]] = collections.Counter()
    for triangle in triangles:
        for left, right in ((triangle[0], triangle[1]), (triangle[1], triangle[2]), (triangle[2], triangle[0])):
            edges[tuple(sorted((left, right)))] += 1
    boundary = sum(1 for uses in edges.values() if uses != 2)
    return len(triangles), boundary


def check() -> dict[str, object]:
    failures: list[str] = []
    fcstd: list[dict[str, object]] = []
    stls: list[dict[str, object]] = []
    steps: list[dict[str, object]] = []

    for path in sorted(ROOT.glob("freecad/*/source/*.FCStd")):
        try:
            with zipfile.ZipFile(path) as archive:
                bad = archive.testzip()
                names = set(archive.namelist())
                payload = b"".join(archive.read(name) for name in names if name.lower().endswith((".xml", ".txt")))
            if bad or "Document.xml" not in names or SENSITIVE.search(payload):
                failures.append(f"FCStd failed: {path.relative_to(ROOT)}")
            fcstd.append({"path": str(path.relative_to(ROOT)), "entries": len(names), "sha256": sha256(path)})
        except Exception as exc:  # noqa: BLE001
            failures.append(f"FCStd unreadable: {path.relative_to(ROOT)}: {exc}")

    for path in sorted(ROOT.glob("freecad/*/exports/*.stl")):
        try:
            triangles, boundary_edges = stl_edges(path)
            if not triangles or boundary_edges:
                failures.append(f"STL topology failed: {path.relative_to(ROOT)}")
            stls.append({
                "path": str(path.relative_to(ROOT)),
                "triangles": triangles,
                "non_manifold_or_boundary_edges": boundary_edges,
                "sha256": sha256(path),
            })
        except Exception as exc:  # noqa: BLE001
            failures.append(f"STL unreadable: {path.relative_to(ROOT)}: {exc}")

    for path in sorted(ROOT.glob("**/*.step")):
        data = path.read_bytes()
        solids = len(re.findall(rb"MANIFOLD_SOLID_BREP", data, re.IGNORECASE))
        closed_shells = len(re.findall(rb"CLOSED_SHELL", data, re.IGNORECASE))
        valid_structure = data.lstrip().startswith(b"ISO-10303-21") and data.rstrip().endswith(b"END-ISO-10303-21;")
        if not valid_structure or SENSITIVE.search(data):
            failures.append(f"STEP failed: {path.relative_to(ROOT)}")
        steps.append({
            "path": str(path.relative_to(ROOT)),
            "manifold_solids": solids,
            "closed_shells": closed_shells,
            "sha256": sha256(path),
        })

    required_kicad = [
        "Codex-Pulse-5V.kicad_pro",
        "Codex-Pulse-5V.kicad_sch",
        "Codex-Pulse-5V.kicad_pcb",
        "BOM.csv",
        "NETLIST.xml",
        "VERIFICATION.json",
        "DRC-FINAL.txt",
    ]
    kicad_root = ROOT / "kicad" / "codex-pulse-5v"
    missing = [name for name in required_kicad if not (kicad_root / name).is_file()]
    if missing:
        failures.append(f"missing KiCad files: {missing}")
    verification = json.loads((kicad_root / "VERIFICATION.json").read_text(encoding="utf-8"))
    if any(verification.get(key) != 0 for key in ("drc_violations", "unconnected_pads", "footprint_errors")):
        failures.append("recorded KiCad DRC counts are not zero")

    text_suffixes = {".md", ".txt", ".json", ".csv", ".xml", ".srt", ".svg", ".kicad_pro", ".kicad_sch", ".kicad_pcb", ".kicad_mod", ".gbr", ".drl", ".gbrjob"}
    for path in sorted(item for item in ROOT.rglob("*") if item.is_file() and item.suffix.lower() in text_suffixes):
        if SENSITIVE.search(path.read_bytes()):
            failures.append(f"sensitive-pattern match: {path.relative_to(ROOT)}")

    return {
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "freecad_native_files": len(fcstd),
        "stl_files": len(stls),
        "step_files": len(steps),
        "kicad_required_files_present": not missing,
        "recorded_kicad_drc": {
            "violations": verification.get("drc_violations"),
            "unconnected_pads": verification.get("unconnected_pads"),
            "footprint_errors": verification.get("footprint_errors"),
        },
        "freecad": fcstd,
        "stl": stls,
        "step": steps,
    }


if __name__ == "__main__":
    result = check()
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    raise SystemExit(0 if result["status"] == "pass" else 1)

