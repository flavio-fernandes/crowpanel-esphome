# Current state

Last reviewed: 2026-05-28.

## Repository

- Repository: `flavio-fernandes/crowpanel-esphome`
- Remote: `origin`
- Branch: `main`
- GitHub visibility observed through the GitHub connector on 2026-05-28:
  public.
- Roadmap: `docs/roadmap.md`

## Architecture

```text
Mac -> VS Code SSH -> Linux host -> devcontainer -> workbench -> SLOT1 CrowPanel
```

## Primary firmware

`esphome/crowpanel.yaml` is now the main firmware. It is a Home Assistant EGO
charger timer UI for the Elecrow CrowPanel 1.28-inch ESP32-S3 rotary touch
display.

Current firmware scope:

- ESPHome ESP-IDF firmware for `esp32-s3-devkitc-1`, 16MB flash, octal 80MHz
  PSRAM, and `min_version: 2025.10.0`.
- Wi-Fi, encrypted ESPHome API, OTA, Home Assistant imported entities, and
  explicit `switch.turn_on` / `switch.turn_off` actions.
- LVGL UI on the round GC9A01A panel through ESPHome `mipi_spi` at 20MHz.
- CST816 touch, rotary encoder, knob button, GPIO46 backlight, GPIO40/GPIO1/
  GPIO2 power enables, and GPIO48 WS2812 ambient LEDs.
- Local state machine for OFF, ON, CHARGING, start-pending, stop-pending, and
  pending-off recovery.
- Diagnostic Home Assistant entities/buttons for test taps, ring movement,
  action result, effective state, Wi-Fi, IP, SSID, and reboot.

The firmware expects these Home Assistant entities by default:

```text
switch.ego_charger
sensor.ego_charger_power
input_number.ego_charger_preset_duration_minutes
input_datetime.ego_charger_timer_end_time
input_boolean.ego_charger_timer_active
input_boolean.ego_charger_panel_pending_off
```

The helper entities live in
`config/home-assistant/ego-charger-helpers.yaml`. A real charger switch and
power sensor still need to exist locally, or the substitutions at the top of
`esphome/crowpanel.yaml` need to be changed before compiling.

## Known-good examples

- Generic ESP32 smoke tests:
  - `examples/feather-huzzah32-blink/feather-huzzah32-blink.yaml`
  - `examples/feather-huzzah32-heartbeat/feather-huzzah32-heartbeat.yaml`
- CrowPanel hardware bring-up examples:
  - `examples/crowpanel-128-minimal/crowpanel-128-minimal.yaml`
  - `examples/crowpanel-128-backlight/crowpanel-128-backlight.yaml`
  - `examples/crowpanel-128-display-test/crowpanel-128-display-test.yaml`
  - `examples/crowpanel-128-io-diagnostic/crowpanel-128-io-diagnostic.yaml`
  - `examples/crowpanel-128-lvgl-diagnostic/crowpanel-128-lvgl-diagnostic.yaml`
  - `examples/crowpanel-128-ha-wifi-symbol/crowpanel-128-ha-wifi-symbol.yaml`

The LVGL diagnostic is still the smallest end-to-end CrowPanel display, touch,
rotary, button, and LED target. The production charger panel is
`esphome/crowpanel.yaml`.

## SLOT1 board facts

- Board: Elecrow CrowPanel 1.28 inch HMI ESP32 rotary display.
- Chip: ESP32-S3 QFN56, revision v0.2.
- Features observed during bring-up: Wi-Fi, Bluetooth LE, dual core, embedded
  8MB PSRAM, 16MB flash, USB-Serial/JTAG.
- `tools/espwb-esptool` resolves the current SLOT1 serial path on the
  workbench.
- Factory/demo firmware was backed up under ignored local `artifacts/` before
  ESPHome flashing.

## Validated hardware baseline

- Display: GC9A01A 240 x 240 round panel, SCLK GPIO10, MOSI GPIO11, CS GPIO9,
  DC GPIO3, reset GPIO14, `invert_colors: true`.
- LVGL display path: ESPHome `mipi_spi`, 20MHz. This is the validated path for
  LVGL firmware.
- Native diagnostic display path: ESPHome `ili9xxx`, 20MHz. Native `mipi_spi`
  display-test builds compiled but stayed blank on the physical LCD, so the
  native diagnostics intentionally remain on `ili9xxx`.
- Touch: CST816 at I2C address `0x15`, SDA GPIO6, SCL GPIO7, INT GPIO5, reset
  GPIO13, `mirror_y: true`, `swap_xy: true`.
- Rotary: GPIO45/GPIO42 with pullups.
- Knob press: GPIO41 with pullup and active-low inverted logic.
- Backlight and enables: GPIO46 LEDC, GPIO40, GPIO1, GPIO2.
- Ambient LEDs: GPIO48, five WS2812 LEDs, GRB, `use_psram: false`.

## Workflow

Compile and flash only from the devcontainer:

```bash
devcontainer exec --workspace-folder . esphome config esphome/crowpanel.yaml
devcontainer exec --workspace-folder . esphome compile esphome/crowpanel.yaml
devcontainer exec --workspace-folder . tools/espwb-esptool flash-id
devcontainer exec --workspace-folder . tools/espwb-esptool write-flash 0x0 esphome/.esphome/build/crowpanel/.pioenvs/crowpanel/firmware.factory.bin
```

Only flash a `firmware.factory.bin` immediately after a successful compile of
the same YAML. Ignored `.esphome/` build trees can contain stale binaries.

## Monitor caveat

RFC2217 is for serial monitoring only. Closing a short RFC2217 monitor session
has been observed to leave the ESP32-S3/CrowPanel app visually blank or frozen
while the workbench host stays reachable. `tools/espwb-monitor` therefore runs
`tools/espwb-esptool flash-id` after the monitor exits by default.

`tools/validate-workbench.sh` keeps the RFC2217 open/close test opt-in through
`RUN_RFC2217_TEST=1`.

## Reusable platform repo

- Repository: `flavio-fernandes/esp-codex-platform`
- GitHub visibility observed through the GitHub connector on 2026-05-28:
  public.
- Latest published platform commit observed locally: `1c756d9 Refresh ESP
  platform starter workflow`
- Initial commit: `57c98ed Create ESP Codex platform starter`
- Local sibling checkout expected by older docs was not present next to this
  checkout during the 2026-05-28 review.
- Scope: reusable ESPHome/devcontainer/workbench starter with generic docs,
  safe workbench wrappers, validation script, ignore rules, and generic blink
  examples. CrowPanel-specific YAML, hardware facts, artifacts, generated
  firmware, secrets, and Home Assistant device UI are intentionally excluded.

Port candidates identified after the fork were applied to the platform repo in
`1c756d9`; future candidates are tracked in `docs/roadmap.md`.

## Safety rules

- Flashing goes through `tools/espwb-esptool`.
- Use `SLOT1` only unless explicitly approved.
- RFC2217 is monitor-only.
- Keep secrets, private keys, local env files, generated firmware,
  `.esphome/`, and `artifacts/` out of git.
- Do not run `sudo` or push to GitHub without explicit approval.
