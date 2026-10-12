# Codex Pulse: 5 V LED timer

An editable KiCad 7 prototype built from scratch around a TLC555CP CMOS timer
in an astable configuration. The output drives a red LED through 1 kΩ and the
board includes a reset pushbutton, supply/control decoupling and four M3
mounting holes.

## Design summary

- regulated input: 5 V at J1 (pin 1 +5 V, pin 2 GND);
- timer: TLC555CP, PDIP-8;
- nominal frequency: 0.686 Hz;
- nominal duty cycle: 52.4%;
- PCB: 50 × 35 × 1.6 mm, two copper layers;
- 12 electrical components and four 3.2 mm non-plated mounting holes;
- requested minimum clearance: 0.25 mm;
- track width: 0.30 mm;
- via: 0.60/0.30 mm.

Component tolerances affect timing. C1 and C4 are polarized. Check the
TLC555CP package and pin-1 orientation before assembly.

## Source and outputs

- `Codex-Pulse-5V.kicad_pro`, `.kicad_sch`, `.kicad_pcb`: native project;
- `BOM.csv`: bill of materials;
- `NETLIST.xml`: exported connectivity;
- `gerbers/`: copper, mask, silkscreen, outline and drill outputs;
- `Codex-Pulse-5V.step`: native KiCad component STEP export;
- PDFs, SVG and PNG files: inspectable previews;
- `DESIGN.json`, `VERIFICATION.json`, `STEP-READBACK.json`: structured record.

The project-local footprint copies come from the official KiCad libraries and
retain the library licence boundary described in the repository's
`THIRD-PARTY-NOTICES.md`.

## Recorded checks

- native schematic/netlist export: pass;
- schematic-to-design comparison: 30 electrical pins across eight nets;
- PCB-to-schematic pin/net comparison: pass;
- native PCB reopen: pass;
- KiCad DRC: 0 violations, 0 unconnected pads, 0 footprint errors;
- component STEP readback: 13 valid solids;
- visual review of schematic, copper and mechanical preview: pass.

KiCad 7.0.6 was the recorded native version. Its installed CLI did not expose
a schematic ERC command, so native ERC was **not run**. The netlist and pin
functions were inspected separately; this is not equivalent to ERC.

## Test boundary

This is an unbuilt prototype. No electrical, timing, assembly, purchased-part
fit, fabrication or physical test has been performed, and no fabrication
order is claimed. Inspect the current Gerbers/drills and rerun ERC/DRC in your
own supported KiCad toolchain before fabrication.

References:

- [Texas Instruments TLC555 datasheet, SLFS043K](https://www.ti.com/lit/ds/symlink/tlc555.pdf)
- [Texas Instruments TLC555 product page](https://www.ti.com/product/TLC555)

