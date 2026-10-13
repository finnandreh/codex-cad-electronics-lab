# Addressed LED product — complete digital workflow

Designed with OpenAI Codex for Finn Andre. The editable KiCad PCB and schematic remain unchanged from the checked four-IC design: 8 low-current LED outputs, 16 addresses, two HCT164 shift registers, HCT688 comparator and HCT273 storage register. PCB 110 × 80 mm. Three control signals plus 5V and ground.

## Files

- Original native KiCad project, BOM, schematic PDF and manufacturing layers/drills.
- Native KiCad component STEP and FreeCAD import with all 40 component models plus board. STEP does not include copper or silkscreen. Imported models retain their upstream KiCad-library licences; verify redistribution rights for any public model release.
- `Enclosure/`: editable FreeCAD base, lid and separate ESP32 cradle; case-only STEP and Z0 closed STL meshes. CAD opens with a lifted lid. Manufacturing exports show the assembled lid position. Main body 190 × 115 × 34 mm, wall/floor/lid 2.4 mm. LED apertures 3.4 mm; guides are illustrative, not qualified optical components.
- `Control-Demo/`: local Node HTTP controls, real Aedes MQTT broker, real MQTT web/device-simulator clients, pinned dependency lock, Start-Demo.cmd and an unflashed ESP32 example. See its README for the command/state contract and setup.

## Checked / still pending

Native PCB DRC: 0 violations, 0 unconnected pads, 0 footprint errors. 65,536 ideal logic frames passed. Case: three valid native solids, no modelled case/electronics intersections, eight aligned LED axes, closed STL meshes. Actual local MQTT acknowledgements, wrong-address hold, invalid commands and origin/client restrictions passed.

This is an unbuilt prototype. Native schematic ERC, firmware compilation/flashing, assembly, supply sequencing, electrical loading, signal integrity, fastener strength, printed tolerance, actual connector/cable fit, light-guide optics, cooling and RF testing remain pending. ESP32 envelope uses official board dimensions but simplified component heights. Current firmware does not sense actual LED outputs. The browser demo simulates the device. A physical device needs a separate authenticated reachable broker; do not expose the loopback demo.

The Gerber ZIP contains 8 machine files: front/back copper, front/back mask, front silkscreen, outline, PTH and NPTH drills. Review fabrication preview and options before submitting to PCBWay. No order was placed.

The film uses actual KiCad layers and native FreeCAD feature/parameter tours recorded with OBS, plus actual local web controls. It is an edited explanation of the complete digital workflow, not uninterrupted footage of the original design session. Paid Azure Ryan narration is credited; matching earlier speech was reused.

Official ESP32 drawing: https://dl.espressif.com/dl/schematics/esp32_devkitc_v4_dimensions.pdf

Project workflow: https://finnandre.no/resources/kicad-pcb-design-with-codex/

OpenAI, KiCad, FreeCAD, OBS, Microsoft and PCBWay attribution does not imply sponsorship or endorsement. Third-party dependencies and component models retain their respective licences.
