# Addressed LED board — complete digital prototype workflow

Designed with OpenAI Codex for Finn Andre, 12 October 2026.

This public project connects the complete digital evidence chain shown in the
film: editable KiCad schematic and PCB, BOM and Gerbers, an editable FreeCAD
enclosure, case-only manufacturing exports, a loopback web/MQTT demonstration
and an uncompiled ESP32 firmware example.

- [10-minute workflow film on YouTube](https://www.youtube.com/watch?v=lBj9bRSQ6mM)
- [Exact 600-second MP4 release asset](https://github.com/finnandreh/codex-cad-electronics-lab/releases/download/evidence-2026-10-12/Codex-KiCad-FreeCAD-MQTT-Full-Workflow-10min-EN-v5.mp4)
- [Captions](media/CAPTIONS-FULL-WORKFLOW-v5.srt) and [29 chapters](media/CHAPTERS-FULL-WORKFLOW-v5.txt)
- [Manufacturing handoff ZIP](manufacturing/Codex-Address-LED-4IC-Gerbers-v1.zip)

The film SHA-256 is
`36e50339378d485888e99282146dba78f6cee45e7d6a15c356c44fe37dfe8331`.
Its 600-second duration is the edited film length, not an independently timed
claim about total development time.

Open `Codex-Address-LED-4IC.kicad_pro` in KiCad 7.0.6 or compatible newer KiCad.
The schematic embeds its symbols; used official stock footprints are copied into
the project-local `footprints` libraries. Confirm the dimensions of the actual
purchased components before fabrication. No fabrication order has been placed.

The 110 × 80 mm two-layer board has four ICs, eight red indicator LEDs, four
address jumpers and four 3.2 mm non-plated mounting holes. It is a demonstration
of addressed serial output storage, not a high-current LED or motor driver.

| Function | Part | Package |
| --- | --- | --- |
| Serial data shift | U1 CD74HCT164E | PDIP-14, 7.62 mm |
| Serial address shift | U2 CD74HCT164E | PDIP-14, 7.62 mm |
| Address equality and commit gating | U3 CD74HCT688E | PDIP-20, 7.62 mm |
| Eight stored outputs | U4 CD74HCT273E | PDIP-20, 7.62 mm |

This separates the shift and output-storage functions commonly associated with
a 74HC595. U4 is an edge-triggered octal register, rather than a transparent
latch. Only the matching addressed module receives a positive commit-clock edge.

## Connections and initialization

J1 and J2 are electrically parallel, with the same order:
1 = regulated +5 V, 2 = GND, 3 = DATA, 4 = CLOCK, 5 = STROBE.
Do not reverse these headers. Do not connect the 5 V supply to an ESP32 GPIO.
Use a common ground and short local wires; this is not a validated cable bus.

Use the specified **HCT** logic at 4.5–5.5 V. Its input thresholds are compatible
with valid 3.3 V push-pull logic levels. A 5 V **HC** substitution does not have
the same guaranteed input threshold. DATA, CLOCK and STROBE have 10 kΩ
pull-downs to GND; there is no 5 V signal pull-up feeding a controller GPIO.
The controller must establish STROBE HIGH before generating any CLOCK edges.
Keep the controller and board powered appropriately; power-sequencing and
unpowered-input injection behavior must be checked on actual hardware.

Power-up register states are not guaranteed. Press RESET after power-up to clear
both shift registers and all LED outputs, or initialize each board with a valid
write. RESET is local, active LOW; it is not one of the three bus signals.
Change address jumpers with power removed, then initialize again.

## Address and frame format

Fitted address jumpers contribute 1, 2, 4 and 8; open contributes zero.
Example: jumpers 1 + 4 select address 5. All open selects address 0.
Give each parallel module a different address if individual control is wanted.

1. Keep STROBE HIGH, CLOCK LOW.
2. Shift the address byte MSB first, then the LED byte MSB first: 16 rising CLOCK
   edges. Address upper four bits must be zero; accepted addresses are 0–15.
3. For the reference sequence, leave 500 μs for DATA setup, then CLOCK HIGH for
   500 μs and LOW again. This deliberately slow example is not a maximum rating.
4. After the last falling CLOCK edge, wait at least 100 μs.
5. Set STROBE LOW for 100 μs, then HIGH. The selected comparator output rises and
   U4 captures the LED byte. Do not generate CLOCK edges while STROBE is LOW.
6. Keep data stable for at least 100 μs after STROBE rises.

Bit 0 controls LED 0. A HIGH stored output lights its red LED through 2.2 kΩ,
approximately 1 mA at typical red-LED voltage. LED brightness/current depends on
the purchased LED and output voltage; no external load capability is specified.

## Checks and manufacturing exports

The final native PCB was reopened and its pin nets compared with the schematic.
KiCad DRC reports zero violations, zero unconnected pads and zero footprint
errors. An ideal event-level model checked all 256 address bytes × 256 output
bytes, including invalid addresses and non-selected-board retention. This is
not SPICE simulation, a physical measurement or proof of signal integrity.
Native schematic ERC was not run; the installed KiCad 7 CLI has no ERC command.
Electrical, assembly, power-up and multi-board timing tests remain necessary.

`gerbers/` contains F.Cu, B.Cu, F.Mask, B.Mask, F.Silkscreen and Edge.Cuts, plus
separate PTH and NPTH Excellon drill files. The manufacturing ZIP includes these
eight machine files; drill-map PDFs are for human review. The ZIP can be uploaded
to PCBWay after inspecting its fabrication preview and selected manufacturing
options. Sending files is not approval to place an order or to pay for one.

The `Control-Demo/` directory provides a real loopback-only Aedes MQTT broker,
two real MQTT clients and a local web interface. The ESP32, GPIO and electrical
hardware are simulated. `Enclosure/` contains the editable FreeCAD case and
case-only STEP/STL exports. See [the full workflow note](FULL-WORKFLOW-README.md)
for the exact checked and still-unknown boundaries.

## Source and licence boundary

The original design, documentation and controller example are covered by the
repository MIT licence. The project-local stock KiCad footprints and embedded
component models retain the KiCad library terms and exception described in the
repository [third-party notices](../../THIRD-PARTY-NOTICES.md). Dependencies
retain their own licences. No real credentials, workstation paths, raw capture
logs or internal authorization receipts are included. `secrets.example.h`
contains placeholders only; create a private `secrets.h` for any hardware test.

References: [TI HCT164](https://www.ti.com/lit/ds/symlink/cd74hct164.pdf),
[TI HCT688](https://www.ti.com/lit/ds/symlink/cd74hct688.pdf),
[TI HCT273](https://www.ti.com/lit/ds/symlink/cd74hct273.pdf),
[KiCad scripting](https://docs.kicad.org/7.0/en/pcbnew/pcbnew.html#scripting),
[PCBWay KiCad export guide](https://www.pcbway.com/blog/help_center/How_to_Generate_Gerber_and_Drill_Files_in_KiCad_7_0_ab0d12bb.html).

Production: real native KiCad layer changes captured with OBS Studio, paid
Microsoft Azure Speech (Ryan), editing/captions with FFmpeg and OpenAI Codex.
Attribution does not imply endorsement by OpenAI, KiCad, TI or PCBWay.
