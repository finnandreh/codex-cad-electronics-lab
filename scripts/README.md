# Sanitized native build sources

These scripts are public, path-sanitized versions of the Python used inside
native FreeCAD and KiCad sessions during the documented work.

They are evidence of the construction method, not a supported one-click build
system. FreeCAD scripts require FreeCAD's Python modules and GUI session. KiCad
scripts target the recorded KiCad 7 Python API and expect explicit environment
paths for the workspace, output folder and installed libraries.

No task-local bridge credential, OBS control credential, private workstation
path, private archive receipt or vendor CAD source is included.

The local application bridge used in production was bound to the same machine
and was separate from OBS Studio's local WebSocket control. These scripts do
not expose an internet-facing FreeCAD service.

## FreeCAD

- `control_box_template.py`: parametric control-box primitives and checks;
- `wall_demo.py`: wall-mount and vent variant;
- `desk_demo.py`: sloped desktop variant;
- `board_case.py`: board-reference case sequence and case-only exports.

`board_case.init()` requires an explicit absolute output directory. Vendor
drawings/models must be obtained directly under their own terms and configured
locally; they are not bundled here.

## KiCad

The four scripts show the recorded sequence from schematic/design data to PCB
layout, footprint localization and final DRC evidence. Set these paths for a
compatible local environment:

- `CAD_LAB_WORKSPACE`
- `CODEX_PULSE_OUT`
- `KICAD_7_SHARE`
- `KICAD_FOOTPRINTS`
- optionally `TLC555_DATASHEET`

Review the code and rerun current ERC/DRC before using generated manufacturing
files. The supplied PCB remains an unbuilt prototype.

