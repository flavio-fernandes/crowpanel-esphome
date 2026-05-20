# Next Codex prompt

Paste this into a fresh Codex thread:

```text
Read AGENTS.md, README.md, docs/current-state.md, docs/roadmap.md, docs/esphome-workbench-cheatsheet.md, docs/github-setup.md, docs/project-sources.md, docs/reference/crowpanel/hardware-facts.md, docs/reference/crowpanel/esphome-lvgl-notes.md, and docs/esp-codex-platform-extraction-plan.md.

We are working in the CrowPanel ESPHome repo on the Elecrow CrowPanel 1.28 inch HMI ESP32 rotary display in workbench SLOT1.

Current pushed commit on main should be:
Add CrowPanel LVGL diagnostic

Important safety/workflow constraints:
- Follow AGENTS.md.
- Flash SLOT1 only.
- Flash only through tools/espwb-esptool.
- RFC2217 is monitor-only.
- Do not use RFC2217 for flashing or reset control.
- Do not use sudo or modify files outside this workspace.
- Do not print, copy, commit, or upload secrets.
- Keep CrowPanel YAML growth incremental.

Validated hardware baseline:
- Current flashed example: examples/crowpanel-128-lvgl-diagnostic/crowpanel-128-lvgl-diagnostic.yaml
- Previous known-good IO diagnostic: examples/crowpanel-128-io-diagnostic/crowpanel-128-io-diagnostic.yaml
- Board identity: ESP32-S3 QFN56 rev v0.2, 8MB embedded PSRAM, 16MB flash, USB-Serial/JTAG.
- Display works with ESPHome ili9xxx GC9A01A at 20MHz.
- Display pins: SCLK GPIO10, MOSI GPIO11, CS GPIO9, DC GPIO3, reset GPIO14.
- Backlight/control outputs: GPIO46 LEDC at 60%, GPIO40 on, GPIO1/GPIO2 on.
- Rear RGB LEDs work: GPIO48, 5 WS2812 LEDs, GRB, brightness 40%, use_psram false.
- Touch works: CST816 on I2C SDA GPIO6, SCL GPIO7, address 0x15, INT GPIO5, reset GPIO13, transform mirror_y true and swap_xy true.
- Rotary works: GPIO45/GPIO42 with pullups; direction can be adjusted later by swapping A/B if desired.
- Knob button works: GPIO41, input pullup, inverted active-low.
- Runtime validation captured rotary values in both directions, repeated knob button press/release logs, touch coordinates, and continued LCD update returns during one serial session.
- First LVGL diagnostic exists at examples/crowpanel-128-lvgl-diagnostic/crowpanel-128-lvgl-diagnostic.yaml.
- The LVGL diagnostic validates, compiles, and has been flashed to SLOT1 through tools/espwb-esptool.
- Camera capture artifacts/crowpanel-camera-20260520T204817Z.jpg confirmed the LVGL page on the round LCD and blue rear LEDs.
- LVGL runtime input validation captured touch logs, rotary movement in both directions, knob button press/release logs, and visible rotary-to-LVGL status label feedback.
- The RFC2217-close blank/frozen behavior reproduced on the LVGL diagnostic, and tools/espwb-esptool flash-id recovered it.
- Camera helpers exist and work:
  - tools/crowpanel-camera-capture
  - tools/crowpanel-camera-sequence
  Captures go under ignored artifacts/.

Known caveat:
- Closing a short RFC2217 serial monitor session can leave the CrowPanel app visually blank/frozen with rear LEDs stuck on the last color, while the workbench host remains reachable.
- Camera-only observation shows the diagnostic can keep looping without an active serial monitor.
- logger.deassert_rts_dtr: true was tested and did not fix the RFC2217-close blank/frozen behavior.
- Current workaround: after closing a serial monitor, reset/recover through:
  ESPWB_SSH_KEY=/path/to/workbench/key tools/espwb-esptool flash-id
- The project wrappers ignore global SSH config by default with SSH_CONFIG=/dev/null. If /host-ssh is not mounted in Codex, set ESPWB_SSH_KEY locally without printing key contents.
- tools/validate-workbench.sh skips the RFC2217 open/close test by default; RUN_RFC2217_TEST=1 is only for intentional monitor-path debugging.

Start by summarizing the state briefly.

Then take the next step:
Review the local reusable boilerplate repo and decide whether to create/push a GitHub repo for it.

Constraints for the next step:
- Do not modify the CrowPanel firmware while planning/extracting boilerplate.
- Do not push or create a GitHub repo without explicit approval.
- Extract only reusable, boring project infrastructure and docs patterns.
- Do not include CrowPanel-specific YAML, hardware references, artifacts, generated firmware, secrets, or workbench host private details.
- Candidate reusable pieces: devcontainer foundation, AGENTS.md template, README template, workbench wrapper pattern, validate-workbench pattern, GitHub setup notes, docs/current-state and roadmap templates, ignored artifact/build-output patterns, and a tiny generic ESPHome blink example.
- Local repo exists with initial commit "Create ESP Codex platform starter".
- Ask before pushing or creating the GitHub repo.
```
