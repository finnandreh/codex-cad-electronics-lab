# Third-party notices and reference boundaries

## OpenAI Codex

OpenAI Codex was used as a coding, CAD-automation and verification assistant.
OpenAI does not sponsor, certify or endorse this independent project.

## FreeCAD and KiCad

FreeCAD and KiCad are open-source tools owned by their respective projects and
contributors. This repository is not an official FreeCAD or KiCad project.

The project-local footprints in `kicad/codex-pulse-5v/footprints/` and
`kicad/addressed-led-4ic/footprints/` are copies of stock KiCad library
footprints. The addressed-LED assembly exports also include component geometry
originating from the KiCad 3D model library. KiCad libraries are published
under the Creative Commons CC-BY-SA 4.0 licence with the KiCad libraries
exception. These library assets are not relicensed under this repository's MIT
licence. See the authoritative notice at
<https://www.kicad.org/libraries/license/>.

## Hardware vendors

Arduino, Raspberry Pi, Espressif, PJRC, Seeed Studio, Texas Instruments and
NVIDIA product names are used only to identify the documented hardware or
datasheet reference. No endorsement is implied.

The addressed-LED design cites Texas Instruments datasheets for the specified
HCT logic and Espressif's official ESP32-DevKitC documentation. Those documents
are linked, not copied. The local demonstration depends on Aedes, MQTT.js,
PubSubClient and ArduinoJson under their respective upstream licences.

Vendor drawings, reference images and CAD models are not redistributed unless
their redistribution terms were verified. The FreeCAD manufacturing exports
in this repository contain the generated case geometry only. Follow the
official source links in each project README for the vendor material.
