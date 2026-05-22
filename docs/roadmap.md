# Roadmap

## Completed milestones

- Created the CrowPanel ESPHome workspace.
- Added and validated the devcontainer foundation.
- Added reset-aware workbench wrappers in `tools/`.
- Validated the workbench path from inside the devcontainer.
- Built and flashed a throwaway ESPHome Feather/HUZZAH32 blink example on `SLOT1`.
- Confirmed real GPIO13 onboard LED blinking every 500 ms.
- Created and pushed the private GitHub repo.
- Added handoff docs for future Codex threads.
- Added and flashed a HUZZAH32 heartbeat blink example on the current SLOT1 board.
- Captured CrowPanel primary sources, hardware facts, and ESPHome/LVGL bring-up
  notes locally under `docs/reference/crowpanel/`.
- Installed the CrowPanel in SLOT1, confirmed ESP32-S3 with 8MB PSRAM and 16MB
  flash, backed up the factory/demo firmware, and flashed a minimal ESPHome
  logger-only build.
- Added and flashed a GPIO46 backlight pulse example for the CrowPanel.
- Added, validated, compiled, and flashed a GC9A01A `mipi_spi` display test
  pattern for the CrowPanel; the physical LCD stayed blank.
- Reworked the display test to match Elecrow's own ESPHome lessons
  (`ili9xxx`, `model: GC9A01A`, `show_test_card: true`, GPIO46 LEDC
  backlight), compiled and flashed it, and confirmed serial heartbeat logs.
- Added, validated, compiled, and flashed a CrowPanel IO diagnostic example
  that cycles GPIO48 ambient LEDs, GPIO46 backlight levels, GPIO40, and LCD fill
  colors while logging each phase.
- Fixed the IO diagnostic `on_boot` priority after serial logs showed LEDC was
  not initialized at priority `800`; the currently flashed build uses priority
  `-100`.
- Stabilized the CrowPanel visual diagnostic by using `ili9xxx` GC9A01A at
  20MHz SPI, fixed 60% GPIO46 backlight, GPIO40/GPIO1/GPIO2 enabled, and
  GPIO48 WS2812 updates with `use_psram: false`. A 125 second serial soak and
  USB camera sequence confirmed repeated LCD and rear RGB color cycling.
- Added and flashed CST816 touchscreen logging on the stable visual diagnostic.
  Serial logs captured transformed/raw coordinates during taps and drags while
  the display/RGB loop continued running.
- Added, validated, compiled, flashed, and camera-verified the first tiny LVGL
  diagnostic example. The round LCD shows one LVGL page with a title, arc,
  status label, and button, using the validated display/touch/rotary/button
  baseline. Hands-on post-flash LVGL input behavior still needs runtime
  interaction testing.
- Validated LVGL diagnostic runtime input: touch logs, rotary movement in both
  directions, knob button press/release logs, and visible rotary-to-LVGL status
  feedback were captured. The RFC2217-close blank/frozen behavior reproduced on
  the LVGL diagnostic, and `tools/espwb-esptool flash-id` recovered the display.
- Migrated the CrowPanel LVGL diagnostic from deprecated `ili9xxx` to ESPHome
  `mipi_spi` after it compiled, flashed, and rendered correctly on the physical
  round LCD. Native display diagnostics remain on `ili9xxx` because the native
  `mipi_spi` display-test compiled but stayed blank when flashed.
- Aligned the original CrowPanel display-test boot sequence with the stable
  diagnostics by using post-initialization `on_boot` priority `-100` and a
  fixed 60% GPIO46 backlight.

## Current repo state

- Repo: configured as `origin`; keep visibility private unless intentionally
  publishing a sanitized public copy.
- Branch: `main`
- Current architecture: Mac -> VS Code SSH -> Linux host -> devcontainer -> workbench -> SLOT1 board
- Known-good example: `examples/feather-huzzah32-blink/feather-huzzah32-blink.yaml`
- Known-good heartbeat example: `examples/feather-huzzah32-heartbeat/feather-huzzah32-heartbeat.yaml`
- Current CrowPanel baseline example: `examples/crowpanel-128-minimal/crowpanel-128-minimal.yaml`
- Current CrowPanel backlight example: `examples/crowpanel-128-backlight/crowpanel-128-backlight.yaml`
- Current CrowPanel display test example: `examples/crowpanel-128-display-test/crowpanel-128-display-test.yaml`
- Current CrowPanel IO diagnostic example: `examples/crowpanel-128-io-diagnostic/crowpanel-128-io-diagnostic.yaml`
- Current CrowPanel flashed example: `examples/crowpanel-128-lvgl-diagnostic/crowpanel-128-lvgl-diagnostic.yaml`
- Current CrowPanel diagnostic status: serial logs show phase 0/1/2 cycling
  every 5 seconds, with each LCD update returning; USB camera frames confirm
  visible LCD target/crosshair and rear RGB color cycling. The native
  diagnostic display path remains `ili9xxx` GC9A01A at 20MHz, while the LVGL
  diagnostic display path is `mipi_spi` GC9A01A at 20MHz. CST816 touch logs
  transformed and raw
  tap/drag coordinates. Rotary encoder GPIO45/GPIO42 logs movement in both
  directions, and active-low knob button GPIO41 logs press/release events.
- Current CrowPanel LVGL status: the flashed LVGL diagnostic renders on the
  round display, accepts CST816 touch, logs rotary movement in both directions,
  logs knob button press/release, and updates the LVGL status label from rotary
  input.
- Known CrowPanel monitor caveat: camera-only observation confirms the visual
  diagnostic can keep looping without a serial monitor, but closing a short
  RFC2217 serial monitor session can leave the ESP32-S3 app visually stuck or
  blank with rear LEDs frozen. The workbench host can remain reachable. Current
  workaround is to reset through `tools/espwb-esptool flash-id` after monitor
  close and to keep RFC2217 open/close tests opt-in. Testing
  `logger.deassert_rts_dtr: true` did not fix this.
- Camera helpers:
  - `tools/crowpanel-camera-capture`
  - `tools/crowpanel-camera-sequence`
- Latest validation capture directory:
  `artifacts/crowpanel-camera-20260520T165832Z/`
- Latest LVGL validation capture:
  `artifacts/crowpanel-camera-20260520T204817Z.jpg`
- Latest LVGL input/recovery captures:
  `artifacts/crowpanel-camera-20260520T205835Z.jpg`,
  `artifacts/crowpanel-camera-20260520T205941Z.jpg`, and
  `artifacts/crowpanel-camera-20260520T210004Z.jpg`
- Known-good workflow: ESPHome YAML -> `esphome config` -> `esphome compile` -> `tools/espwb-esptool write-flash` -> real GPIO13 blink.

## Remaining CrowPanel project steps

- Bring up hardware features incrementally:
  - Home Assistant/API/OTA only after the local hardware path is stable
- Record each validated milestone in docs before expanding the YAML.

At this point, the local compile, flash, display, touch, rotary, button, LVGL,
camera verification, and recovery workflow has been proven end to end. It now
makes sense to create the future reusable platform repo before adding networked
Home Assistant/API/OTA complexity to this CrowPanel firmware.

## Future reusable platform repo plan

A future reusable platform repo should be named `esp-codex-platform`.

It should capture the reusable pieces that have emerged from this CrowPanel workspace:

- Linux host bootstrap docs/scripts
- workbench bootstrap docs/scripts
- devcontainer template
- `tools/espwb-esptool` pattern
- `tools/validate-workbench.sh` pattern
- `AGENTS.md` template
- `README` template
- `project-sources` and reference capture template
- GitHub setup flow
- known-good ESPHome blink example
- troubleshooting docs

The extraction plan now lives in:

`docs/esp-codex-platform-extraction-plan.md`

The CrowPanel compile, flash, display, touch, rotary, button, LVGL, camera, and
recovery workflow is now validated end to end, so `esp-codex-platform` can be
created next. Keep the first pass generic: no CrowPanel YAML, hardware facts,
artifacts, generated firmware, secrets, or Home Assistant-specific device UI.

`esp-codex-platform` has now been created locally at
the sibling `esp-codex-platform` checkout with initial commit
`57c98ed Create ESP Codex platform starter`. It has been created as a private
GitHub repo and pushed.

## Things not to forget

- RFC2217 is for serial monitoring only.
- Flashing must go through `tools/espwb-esptool`.
- `SLOT1` is the only safe default slot unless explicitly approved.
- Do not use RFC2217 reset control for flashing.
- Do not create a large CrowPanel YAML in one jump.
- Keep secrets, `.env` files, private keys, firmware binaries, `artifacts/`, and `.esphome/` out of git.
- Rebuild the devcontainer with
  `devcontainer up --workspace-folder . --remove-existing-container` after
  editing `.devcontainer/Dockerfile` or `.devcontainer/devcontainer.json`.
- Verify `gh auth status` in Codex's own command environment before GitHub operations.
- Do not push to GitHub unless explicitly approved.
- Do not use `sudo` unless explicitly approved.

## Recommended next Codex thread prompt

```text
Read AGENTS.md, README.md, docs/current-state.md, docs/roadmap.md, docs/esphome-workbench-cheatsheet.md, docs/github-setup.md, docs/project-sources.md, and docs/esp-codex-platform-extraction-plan.md.

Do not modify files yet.

Summarize the project state.

Then review the private `esp-codex-platform` starter repo and continue with the next CrowPanel/Home Assistant project requirements.

Do not modify CrowPanel firmware.
Do not flash anything.
```
