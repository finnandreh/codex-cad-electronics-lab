# Codex CAD & Electronics Lab

Open, inspectable CAD and electronics experiments by **Finn Andre Hotvedt**.
The repository connects native project files, manufacturing-oriented exports,
verification notes and short demonstrations. It is intended as a learning and
evidence resource—not as a catalogue of production-certified products.

The work was developed by Finn Andre Hotvedt with **OpenAI Codex** used as a
coding, CAD-automation and verification assistant. This is an independent
project and is not sponsored, certified or endorsed by OpenAI, Arduino,
Raspberry Pi, Espressif, PJRC, Seeed Studio, Texas Instruments, KiCad or
FreeCAD.

## What is here

### FreeCAD enclosure series

| Project | Reference basis | Native source | Exports | Video |
|---|---|---:|---:|---|
| Original control box | User requirements | FCStd | STEP + STL | [YouTube](https://youtube.com/shorts/aSlC_pHwm3w) |
| Vented wall box | User requirements | FCStd | STEP + STL | [YouTube](https://youtube.com/shorts/YksfvrERqcE) |
| Sloped desk box | User requirements | FCStd | STEP + STL | [YouTube](https://youtube.com/shorts/CappjeAqJ10) |
| Arduino UNO R4 WiFi case | [Arduino documentation](https://docs.arduino.cc/hardware/uno-r4-wifi/) | FCStd | STEP + STL | [YouTube](https://youtube.com/shorts/f9JGq1Lt9iA) |
| Arduino Nano ESP32 case | [Arduino documentation](https://docs.arduino.cc/hardware/nano-esp32/) | FCStd | STEP + STL | [YouTube](https://youtube.com/shorts/Nnz0JP0rjxY) |
| Arduino Nano Every case | [Arduino documentation](https://docs.arduino.cc/hardware/nano-every/) | FCStd | STEP + STL | [YouTube](https://youtube.com/shorts/B6qXtXM9weI) |
| Raspberry Pi Pico 2 W case | [Raspberry Pi drawing](https://pip.raspberrypi.com/documents/RP-008304-DS) | FCStd | STEP + STL | [YouTube](https://youtube.com/shorts/0EeUTEl4Bvc) |
| Arduino Nano 33 BLE Sense Rev2 case | [Arduino documentation](https://docs.arduino.cc/hardware/nano-33-ble-sense-rev2/) | FCStd | STEP + STL | [YouTube](https://youtube.com/shorts/lx_XKFIRO3s) |
| Arduino Nano Matter case | [Arduino documentation](https://docs.arduino.cc/hardware/nano-matter/) | FCStd | STEP + STL | [YouTube](https://youtube.com/shorts/HLhrCJWROGE) |
| ESP32-DevKitC V4 case | [Espressif documentation](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html) | FCStd | STEP + STL | [YouTube](https://youtube.com/shorts/zuW0kFK4ihY) |
| Teensy 4.1 case | [PJRC documentation](https://www.pjrc.com/store/teensy41.html) | FCStd | STEP + STL | [YouTube](https://youtube.com/shorts/UJIxXmdg7ow) |
| Seeed XIAO ESP32C3 case | [Seeed documentation](https://wiki.seeedstudio.com/XIAO_ESP32C3_Getting_Started/) | FCStd | STEP + STL | [YouTube](https://youtube.com/shorts/zEbMOSpfGsM) |
| Seeed XIAO SAMD21 case | [Seeed documentation](https://wiki.seeedstudio.com/Seeeduino-XIAO/) | FCStd | STEP + STL | [YouTube](https://youtube.com/shorts/16ucF9Jwm48) |
| Arduino Nano 33 IoT case | [Arduino documentation](https://docs.arduino.cc/hardware/nano-33-iot/) | FCStd | STEP + STL | [YouTube](https://youtube.com/shorts/3WT94s_HcS0) |
| Jetson Orin Nano reference dev-kit case | [NVIDIA documentation](https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/hardware_layout.html) | case-only FCStd | case-only STEP + STL | GitHub release |

Videos in this table were scheduled for 12 October 2026 (Europe/Oslo) when
this first public evidence package was prepared. A link is not evidence that a
scheduled video is already public; verify the current YouTube status directly.
The Jetson reel has no social publication slot in this release.

Each directory contains native FreeCAD source, case-only exports, selected
rendered views, a project note, captions where available and SHA-256 hashes.
Third-party board reference images and vendor CAD models are deliberately not
redistributed.

### KiCad project

[`kicad/codex-pulse-5v`](kicad/codex-pulse-5v/) contains an editable KiCad
7 project for a 5 V TLC555CP astable LED timer:

- native schematic and two-layer PCB;
- bill of materials and netlist;
- project-local stock KiCad footprints with their original licence boundary;
- Gerber and plated/non-plated drill outputs;
- schematic, PCB and mechanical previews;
- a component STEP export;
- a factual verification record.

The recorded KiCad DRC result is zero violations, zero unconnected pads and
zero footprint errors. The design is **unbuilt**: electrical operation,
timing, assembly, purchased-part fit and manufacturability have not been
physically tested.

## The workflow behind the files

“Built with a prompt” does not mean that a model appeared without engineering
work. The recorded workflow is:

1. translate a requirement into explicit dimensions and constraints;
2. retrieve and reconcile an official drawing or datasheet where applicable;
3. create a parametric native project;
4. place the board/reference geometry and check connector access;
5. export neutral and manufacturing-oriented formats;
6. reopen or parse saved files and compare expected geometry and nets;
7. state the untested boundaries;
8. capture the real native application and prepare narration/captions;
9. publish source and evidence so others can inspect the claim.

See [Evidence method](docs/EVIDENCE-METHOD.md) for the distinction between
observed, checked and still-unknown facts.

## Safety and manufacturing boundary

These are prototype and learning files. Before fabrication or use:

- compare dimensions with the exact hardware revision in hand;
- check connector and cable-overmould clearance;
- choose actual screws, inserts and tolerances for the print process;
- evaluate ventilation, temperature, RF behaviour and electrical safety;
- run current CAD/EDA checks with your own toolchain;
- inspect Gerbers and drills with the intended board manufacturer.

Do not treat a software geometry check, DRC report or successful file reopen as
a physical fit, electrical, thermal, RF, compliance or manufacturing test.

## Licence

Original project source and documentation are released under the MIT License;
see [LICENSE](LICENSE). Original images, captions and video published from this
repository are available under [CC BY 4.0](MEDIA-LICENSE.md). Third-party
materials retain their own licences; see
[THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).

## More context

- [FreeCAD with Codex — Finnandre](https://finnandre.no/resources/freecad-with-codex/)
- [KiCad PCB design with Codex — Finnandre](https://finnandre.no/resources/kicad-pcb-design-with-codex/)
- [Finnandre Open](https://finnandre.no/resources/)
- [Finn Andre Hotvedt on YouTube](https://www.youtube.com/@finnandrehotvedt6974)
