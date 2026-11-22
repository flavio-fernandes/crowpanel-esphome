# Current state

## Firmware and hardware scope

`esphome/crowpanel.yaml` remains the EGO charger timer firmware for the Elecrow
CrowPanel 1.28-inch ESP32-S3 rotary touch display. The main UI uses LVGL,
GC9A01A through `mipi_spi` at 20MHz, CST816 touch, rotary encoder, knob button,
backlight, power enables and ambient LEDs. Native diagnostic examples retain
`ili9xxx`; the LVGL diagnostic remains the small end-to-end test target.

Home Assistant helpers are in `config/home-assistant/ego-charger-helpers.yaml`.
Supply the real charger switch/power sensor locally and allow HA service calls
in the ESPHome integration. No firmware or HA configuration changed in this migration.

The earlier hardware baseline and physical evidence are preserved in
[history/current-state.md](history/current-state.md) and
[the hardware reference](reference/crowpanel/hardware-facts.md).
**The CrowPanel is not currently installed on the bench.** SLOT1 is only a
wrapper default, not a claim of attached device identity.

## Current transport

Developer environment -> restricted `bench-agent` SSH -> configured USB slot.
The client follows esp-codex-platform W11 and its `bench/DESIGN.md` contract.
Use `tools/espwb-esptool` for identity, backup and merged-image writes;
`tools/espwb-monitor` uses bounded serial-follow and never resets on exit.
Native-USB ESP monitoring is disabled by default on the server; an operator
must explicitly configure it if serial logs are required.

The old flash-id-after-monitor-close workaround is historical because the
new serial owner is independent of monitor clients; closing a reader cannot
cause the retired transport's modem-line wedge.

`tools/crowpanel-camera-capture` captures remotely, preserves JPEG paths and
uses atomic private downloads. `tools/crowpanel-camera-sequence` retains
`frame-01.jpg` style paths, four frames and three-second intervals by default.
Server camera defaults apply unless overridden in local `config/bench.env`.

## Verification boundary

This migration is verified with fake-SSH client tests and ShellCheck only.
No hardware was touched and no firmware was compiled or flashed. Prior
physical observations must not be treated as Argon/CrowPanel acceptance.

Follow [the bench guide](esphome-bench-cheatsheet.md) and
[the fresh-clone guide](esphome-fresh-clone-flash-cheatsheet.md).
Keep holds through verification, release on failure too, never commit backups,
and never flash output left over from an unsuccessful compile.
