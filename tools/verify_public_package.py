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
    rb"api[_-]?key|access[_-]?token|moodscape",
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

    native_sources = list(ROOT.glob("freecad/*/source/*.FCStd"))
    native_sources.extend(ROOT.glob("kicad/addressed-led-4ic/**/*.FCStd"))
    for path in sorted(native_sources):
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

    mesh_exports = list(ROOT.glob("freecad/*/exports/*.stl"))
    mesh_exports.extend(ROOT.glob("kicad/addressed-led-4ic/**/*.stl"))
    for path in sorted(mesh_exports):
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

    addressed_root = ROOT / "kicad" / "addressed-led-4ic"
    addressed_required = [
        "Codex-Address-LED-4IC.kicad_pro",
        "Codex-Address-LED-4IC.kicad_sch",
        "Codex-Address-LED-4IC.kicad_pcb",
        "BOM.csv",
        "NETLIST.xml",
        "DRC-FINAL.txt",
        "PROTOCOL-VERIFICATION.json",
        "Enclosure/Codex-LED-ESP32-Case-v1.FCStd",
        "Enclosure/Codex-LED-ESP32-Case-only-v1.step",
        "Control-Demo/server.mjs",
        "Control-Demo/ESP32-Example/ESP32-Example.ino",
        "Control-Demo/ESP32-Example/secrets.example.h",
        "manufacturing/Codex-Address-LED-4IC-Gerbers-v1.zip",
        "media/CAPTIONS-FULL-WORKFLOW-v5.srt",
        "media/CHAPTERS-FULL-WORKFLOW-v5.txt",
    ]
    addressed_missing = [name for name in addressed_required if not (addressed_root / name).is_file()]
    if addressed_missing:
        failures.append(f"missing addressed-LED files: {addressed_missing}")

    drc_text = (addressed_root / "DRC-FINAL.txt").read_text(encoding="utf-8")
    for expected in ("Found 0 DRC violations", "Found 0 unconnected pads", "Found 0 Footprint errors"):
        if expected not in drc_text:
            failures.append(f"addressed-LED DRC record missing: {expected}")
    protocol = json.loads((addressed_root / "PROTOCOL-VERIFICATION.json").read_text(encoding="utf-8"))
    if protocol.get("status") != "PASS" or protocol.get("exhaustive_frames") != 65536:
        failures.append("addressed-LED protocol verification record is incomplete")
    runtime = json.loads((addressed_root / "Control-Demo" / "RUNTIME-CHECKS.json").read_text(encoding="utf-8"))
    if runtime.get("status") != "PASS" or runtime.get("final", {}).get("state", {}).get("simulated") is not True:
        failures.append("addressed-LED MQTT runtime record is incomplete or obscures simulation")

    gerber_names = sorted(path.name for path in (addressed_root / "gerbers").iterdir() if path.is_file())
    with zipfile.ZipFile(addressed_root / "manufacturing" / "Codex-Address-LED-4IC-Gerbers-v1.zip") as archive:
        archive_files = sorted(pathlib.PurePosixPath(name).name for name in archive.namelist() if not name.endswith("/"))
        unsafe_names = [name for name in archive.namelist() if pathlib.PurePosixPath(name).is_absolute() or ".." in pathlib.PurePosixPath(name).parts]
        if archive.testzip() or unsafe_names or archive_files != gerber_names:
            failures.append("addressed-LED manufacturing ZIP does not exactly match reviewed Gerbers")

    secret_example = (addressed_root / "Control-Demo" / "ESP32-Example" / "secrets.example.h").read_text(encoding="utf-8")
    if "YOUR_TEST_WIFI_PASSWORD" not in secret_example or "YOUR_DEVICE_PASSWORD" not in secret_example:
        failures.append("ESP32 example-secret placeholders are missing")
    if (addressed_root / "Control-Demo" / "ESP32-Example" / "secrets.h").exists():
        failures.append("real ESP32 secrets file must not be public")

    media_manifest = json.loads((ROOT / "videos" / "RELEASE-ASSETS.json").read_text(encoding="utf-8"))
    full_workflow = [item for item in media_manifest["assets"] if item["file"] == "Codex-KiCad-FreeCAD-MQTT-Full-Workflow-10min-EN-v5.mp4"]
    pulse = [item for item in media_manifest.get("youtube_only", []) if item.get("source") == "kicad/codex-pulse-5v/"]
    if len(full_workflow) != 1 or full_workflow[0].get("source") != "kicad/addressed-led-4ic/" or len(pulse) != 1:
        failures.append("KiCad film-to-source mapping is incomplete")

    text_suffixes = {".md", ".txt", ".json", ".csv", ".xml", ".srt", ".svg", ".h", ".ino", ".mjs", ".js", ".html", ".cmd", ".kicad_pro", ".kicad_sch", ".kicad_pcb", ".kicad_mod", ".gbr", ".drl", ".gbrjob"}
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
        "addressed_led_required_files_present": not addressed_missing,
        "addressed_led_protocol_frames": protocol.get("exhaustive_frames"),
        "addressed_led_mqtt_simulated": runtime.get("final", {}).get("state", {}).get("simulated"),
        "film_to_source_mappings": len(media_manifest["assets"]) + len(media_manifest.get("youtube_only", [])),
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
