# Codex LED Lab

Designed with OpenAI Codex for Finn Andre. A real, isolated MQTT broker and two real MQTT clients run on the computer. The ESP32, GPIO and electrical LED hardware are simulated.

## Run the demonstration

Install Node.js 20 or newer from https://nodejs.org/. Run `Start-Demo.cmd` in this folder. It uses the pinned package lock and installs only missing local dependencies. Open http://127.0.0.1:8788/. The broker uses MQTT 3.1.1 at 127.0.0.1:18884. Both listeners bind only to loopback. Press Ctrl+C in that command window to stop them. If those ports are busy, resolve that conflict rather than terminating an unknown process.

Choose address 5, then Alternating LEDs: the acknowledged mask becomes 85 (0x55). Send All LEDs on to address 6: the stored pattern remains 0x55. Return to address 5: All LEDs on stores 255. Requested buttons are separate from acknowledged outputs. Animate wiring draws five paths between named pins.

Command topic: `codex/address-led/set`, JSON `{ "version":1, "seq":1, "address":5, "mask":85 }`. State: `codex/address-led/state/5`. The browser uses its local HTTP server, which is an MQTT client; it does not connect directly to the TCP broker. Local client names and exact topics are restricted. This is an isolated teaching demo, not a production authentication design.

## Physical follow-on

The ESP32 example is uncompiled, unflashed and not bench-tested. It needs Arduino ESP32, PubSubClient 2.8 and ArduinoJson 7. Copy `secrets.example.h` to `secrets.h` privately and configure your own authenticated TLS test broker and CA. No credentials are included. The loopback simulator rejects a physical client; do not expose it by changing its bind address. A hardware integration requires a separately configured broker and web-to-device bridge, proper identities and ACLs, and physical acceptance testing. This package does not claim that deployment is complete.

GPIO23 → J1.3 DATA; GPIO18 → J1.4 CLOCK; GPIO19 → J1.5 STROBE; GND → J1.2; regulated 5V → J1.1. Use short local wires and clean edges. The PCB's HCT logic is powered at 5V and accepts 3.3V push-pull control levels. Select one ESP32 supply method; USB and external inputs must not be combined. The eight outputs are low-current indicators, not power drivers.

The firmware sends address then LED byte, MSB first, with STROBE high while shifting. Settle, pulse low, then high; no clock edges during that pulse. A reported frame means software transmitted it, not that physical outputs were sensed. The board needs initialized outputs; reset/power sequencing and transient behavior need bench checks. Firmware sequence values are monotonic per boot; define reset/session handling before using a long-lived production controller.

## Evidence and sources

`RUNTIME-CHECKS.json` records real MQTT acknowledgements, wrong-address hold, invalid commands, foreign-origin rejection and unknown MQTT client denial. No physical hardware was connected. See the enclosure geometry report for model checks and limitations.

- https://github.com/moscajs/aedes
- https://github.com/mqttjs/MQTT.js
- https://github.com/knolleary/pubsubclient
- https://arduinojson.org/v7/api/json/deserializejson/
- https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html

Software dependencies retain their own licences. Do not distribute `node_modules`, real secrets or private machine logs with this source.
