# Roadmap

Last reviewed: 2026-05-28.

## Completed

- Created the CrowPanel ESPHome workspace, devcontainer, ignore rules, and
  reset-aware workbench wrappers.
- Validated the workbench path through the devcontainer and `SLOT1`.
- Built and flashed small Feather/HUZZAH32 ESPHome blink and heartbeat
  examples.
- Captured CrowPanel source links, hardware facts, and ESPHome/LVGL bring-up
  notes under `docs/reference/crowpanel/`.
- Installed the CrowPanel in `SLOT1`, confirmed ESP32-S3 identity, 8MB PSRAM,
  and 16MB flash, and backed up the factory/demo firmware to ignored local
  artifacts.
- Brought up CrowPanel hardware incrementally: logger-only, GPIO46 backlight,
  display, GPIO40/GPIO1/GPIO2 enables, GPIO48 WS2812 LEDs, CST816 touch,
  rotary encoder, and active-low knob button.
- Validated the LVGL diagnostic on the round LCD using ESPHome `mipi_spi`
  GC9A01A at 20MHz.
- Kept native display diagnostics on ESPHome `ili9xxx` because native
  `mipi_spi` display-test builds compiled but stayed blank on the physical LCD.
- Added `tools/espwb-monitor`, with post-monitor `flash-id` recovery for the
  RFC2217 close caveat.
- Created, refreshed, pushed, and made public the reusable platform starter repo,
  `flavio-fernandes/esp-codex-platform`.
- Added the Home Assistant EGO charger timer firmware in
  `esphome/crowpanel.yaml`.
- Added the Home Assistant helper package in
  `config/home-assistant/ego-charger-helpers.yaml`.
- Added production UI behavior notes, a production test matrix, and README
  photos for the charger panel.

## Current state

- Main firmware: `esphome/crowpanel.yaml`.
- Main purpose: EGO charger timer panel for Home Assistant.
- Main setup guide: `docs/esphome-fresh-clone-flash-cheatsheet.md`.
- Short workbench guide: `docs/esphome-workbench-cheatsheet.md`.
- Current state details: `docs/current-state.md`.
- Current GitHub visibility observed on 2026-05-28:
  `flavio-fernandes/crowpanel-esphome` is public and
  `flavio-fernandes/esp-codex-platform` is public.

## Remaining CrowPanel work

- Run `esphome config` and `esphome compile` for `esphome/crowpanel.yaml` after
  any firmware change.
- Run or update `docs/ego-charger-production-test-matrix.md` when charger logic,
  Home Assistant helper entity names, or UI behavior changes.
- Keep the substitutions at the top of `esphome/crowpanel.yaml` aligned with
  the real Home Assistant charger switch and power sensor.
- Verify the ESPHome integration still allows the device to perform Home
  Assistant actions after adding or re-pairing the device.
- Continue using `tools/espwb-monitor` for serial logs and
  `tools/espwb-esptool flash-id` for reset-aware recovery after monitor close.
- Keep generated firmware, local captures, `.esphome/`, `config/workbench.env`,
  and `esphome/secrets.yaml` out of commits.

## Platform port candidates

The spin-off repo is `flavio-fernandes/esp-codex-platform`. The useful generic
changes identified after the fork were ported and pushed in `1c756d9 Refresh
ESP platform starter workflow`.

Already ported:

- Add `tools/espwb-monitor` as a generic RFC2217 monitor wrapper with optional
  post-monitor `tools/espwb-esptool flash-id` recovery.
- Port the stronger `tools/validate-workbench.sh` command checks for `file`,
  `jq`, `rg`, `shellcheck`, `tree`, and `unzip`.
- Port the `.devcontainer/Dockerfile` package additions that make those checks
  meaningful: `file`, `ripgrep`, `shellcheck`, `tree`, `unzip`, `usbutils`, and
  `xz-utils`.
- Refresh `docs/workbench-cheatsheet.md` in the platform repo with the current
  RFC2217 monitor caveat, stale-firmware warning, and reset-aware recovery
  pattern in a hardware-neutral form.
- Add a generic public-hygiene checklist based on
  `docs/public-release-checklist.md`.
Still keep `tools/crowpanel-camera-*`, CrowPanel YAML, Home Assistant helper
  packages, CrowPanel hardware notes, charger UI docs, photos, and test matrix
  out of the platform repo because they are device-specific.
