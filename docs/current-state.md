# Current state

## Repository

- Repo: configured as `origin`; keep visibility private unless intentionally
  publishing a sanitized public copy.
- Branch: `main`
- Roadmap: `docs/roadmap.md`

Current validated commits:

- `a4f612e` Add CrowPanel ESPHome devcontainer foundation
- `271bd8f` Add known-good ESPHome workbench blink example
- `529d390` Document GitHub setup workflow
- `c35f23b` Add HUZZAH32 heartbeat blink example

## Architecture

Mac -> VS Code SSH -> Linux host -> devcontainer -> workbench -> SLOT1 board

## Known-good workflow

The validated path is:

1. Create a tiny ESPHome YAML.
2. Run `esphome config`.
3. Run `esphome compile`.
4. Flash the generated factory image through `tools/espwb-esptool write-flash`.
5. Verify real GPIO13 LED blinking on the SLOT1 board.

The known-good throwaway example is:

`examples/feather-huzzah32-blink/feather-huzzah32-blink.yaml`

## Current SLOT1 board

- Board: Elecrow CrowPanel 1.28 inch HMI ESP32 rotary display
- Detected device path on workbench: `/dev/ttyACM0` or `/dev/ttyACM1` after
  unplug/replug; `tools/espwb-esptool` resolves the current SLOT1 path.
- Detected chip: ESP32-S3 QFN56, revision v0.2
- Detected features: Wi-Fi, Bluetooth LE, dual core, embedded 8MB PSRAM
- Detected flash: 16MB
- USB mode: USB-Serial/JTAG
- MAC observed during flash-id: stored locally when needed; omitted from
  committed docs.

## Current CrowPanel firmware state

- Factory/demo firmware was backed up before flashing ESPHome.
- Backup path: `artifacts/crowpanel-slot1-factory-demo-2026-05-19.bin`
- Backup size: 16,777,216 bytes
- Backup SHA-256: `e11671b2f0d95d75cb4e992138795cae351c29363ec51bae2d73e3e67a7c3bbc`
- Current flashed ESPHome example:
  `examples/crowpanel-128-lvgl-diagnostic/crowpanel-128-lvgl-diagnostic.yaml`
- Previous known-good IO diagnostic:
  `examples/crowpanel-128-io-diagnostic/crowpanel-128-io-diagnostic.yaml`
- Current firmware scope: minimal ESP32-S3 ESPHome logger with 16MB flash,
  octal 80MHz PSRAM configuration, GPIO46 LEDC screen backlight at 60%,
  GPIO40/GPIO1/GPIO2 output enables, GPIO48 WS2812 ambient LEDs, CST816 touch,
  rotary encoder, knob button, and one ESPHome LVGL page on the validated
  `mipi_spi` GC9A01A display path using SCLK GPIO10, MOSI GPIO11, CS GPIO9, DC
  GPIO3, and reset GPIO14. The LVGL page has a title, arc, status label, and
  button. It does not include Wi-Fi, API, OTA, or Home Assistant integration.
- Previous IO diagnostic serial monitor status: RFC2217 monitor showed the
  diagnostic firmware cycling phases every 5 seconds:
  - phase 0: LCD red target/crosshair, ambient red
  - phase 1: LCD green target/crosshair, ambient green
  - phase 2: LCD blue target/crosshair, ambient blue
- Important diagnostic correction: an intermediate build used `on_boot`
  priority `800`, logged `ledc.output: Not yet initialized`, and boot-looped
  with `StoreProhibited`. The currently flashed build uses `on_boot` priority
  `-100`, and logs confirm the phase loop is running without that crash.
- Later diagnostic correction: the first fixed build could still become
  visually stuck. The stable build lowers display data rate from the ESPHome
  default 40MHz to 20MHz, uses constant 60% backlight, disables PSRAM for the
  WS2812 strip, and avoids dimming/toggling rails during the display test.
- 2026-05-20 validation: after flashing the tuned diagnostic, a 125 second
  RFC2217 monitor captured repeated red/green/blue cycles with every
  `Updating LCD` followed by `LCD update returned`. Camera sequence
  `artifacts/crowpanel-camera-20260520T165832Z/` visually confirmed the round
  LCD and rear RGB LEDs changing colors.
- 2026-05-20 touchscreen validation: added CST816 touch using Elecrow's
  ESPHome pins and transform (`address: 0x15`, SDA GPIO6, SCL GPIO7, INT
  GPIO5, reset GPIO13, `mirror_y: true`, `swap_xy: true`). After flashing,
  serial logs captured transformed/raw coordinates during taps and drags while
  the display loop continued returning from LCD updates.
- 2026-05-20 rotary/button validation: added Elecrow rotary encoder pins
  GPIO45/GPIO42 with pullups and knob button GPIO41 with pullup/inverted
  active-low logic. A live RFC2217 monitor captured rotary values moving in
  both directions, repeated `Knob button pressed`/`Knob button released` logs,
  touch coordinates, and continued `LCD update returned` logs during the same
  session.
- 2026-05-20 first LVGL diagnostic: added
  `examples/crowpanel-128-lvgl-diagnostic/crowpanel-128-lvgl-diagnostic.yaml`
  as a small sibling of the validated IO diagnostic. It keeps the validated
  ESP32-S3, PSRAM, display, backlight, RGB LED, CST816 touch, rotary encoder,
  and knob button pin baseline, removes the display lambda, sets
  `auto_clear_enabled: false`, and lets LVGL render one page with a title,
  arc, status label, and button. `esphome config` passed, `esphome compile`
  succeeded, SLOT1 `flash-id` confirmed the expected ESP32-S3 QFN56 rev v0.2
  with 8MB PSRAM and 16MB flash, and the firmware was
  flashed through `tools/espwb-esptool write-flash`. Camera capture
  `artifacts/crowpanel-camera-20260520T204817Z.jpg` visually confirmed the LVGL
  page on the round LCD and blue rear LEDs. RFC2217 was not opened during this
  validation, so post-flash touch, rotary, and knob-button LVGL interactions
  still need a hands-on runtime check.
- 2026-05-20 LVGL input validation: a short 45 second RFC2217 monitor session
  captured touch events updating transformed/raw coordinates, rotary values
  moving in both directions (`94` up through `96`, then down through `64`, then
  back to `66`), and knob button press/release logs. A pre-monitor camera frame
  `artifacts/crowpanel-camera-20260520T205835Z.jpg` showed the LVGL status
  label already updated to `Rotary 58`, confirming rotary-to-LVGL display
  feedback. After the monitor closed, camera capture
  `artifacts/crowpanel-camera-20260520T205941Z.jpg` showed the known
  RFC2217-close blank/frozen display behavior on the LVGL diagnostic as well.
  Running `tools/espwb-esptool flash-id` recovered/reset the DUT, and camera
  capture `artifacts/crowpanel-camera-20260520T210004Z.jpg` confirmed the LVGL
  page returned.
- 2026-05-21 display-driver cleanup: the LVGL diagnostic was migrated from the
  deprecated `ili9xxx` display platform to ESPHome `mipi_spi` GC9A01A at 20MHz,
  compiled, flashed to SLOT1, and camera-verified on the physical round LCD.
  The native display-test was later flashed with `mipi_spi` and stayed blank, so
  the non-LVGL native display diagnostics remain on the physically proven
  `ili9xxx` path until the native `mipi_spi` path is understood.
- 2026-05-21 stale-artifact warning: the ignored `.esphome/` build directory can
  retain old `firmware.factory.bin` files after YAML changes. Flashing a factory
  image by path without a successful fresh compile of the same YAML can replay a
  stale bad build. The documented flash target is the LVGL diagnostic factory
  image immediately after compiling the LVGL diagnostic YAML.
- 2026-05-21 display-test recovery: after a fresh rebuild and flash, the native
  `crowpanel-128-display-test` stayed blank until it was updated to enable the
  same GPIO1/GPIO2 output rails used by `crowpanel-128-io-diagnostic`, in
  addition to GPIO40/backlight. A rebuilt factory image then flashed
  successfully and camera capture
  `artifacts/crowpanel-camera-20260522T010845Z.jpg` showed the display-test
  target pattern on the round LCD.
- 2026-05-21 backlight example cleanup: `crowpanel-128-backlight` now enables
  GPIO40 plus GPIO1/GPIO2 before blinking GPIO46, matching the CrowPanel power
  setup used by the display-capable examples.
- 2026-05-21 monitor wrapper: `tools/espwb-monitor` now opens raw DUT serial
  logs over the RFC2217 `${ESP_PORT}` from `config/workbench.env` and runs
  `tools/espwb-esptool flash-id` on exit to recover from the known
  blank/frozen-after-monitor-close behavior. A short timeout-driven monitor run
  captured diagnostic phase logs, ran the recovery check, and camera capture
  `artifacts/crowpanel-camera-20260522T013654Z.jpg` confirmed the display was
  not blank afterward.
- 2026-05-20 workbench outage note: the workbench temporarily became
  unreachable from the Linux host (`Destination Host Unreachable`, incomplete
  ARP for the local workbench host). After reboot, SSH/RFC2217 recovered. Current boot health
  looked normal: no throttling (`throttled=0x0`), low load, free memory, disk
  35% used, and `rfc2217-portal.service` active. The previous boot was not
  retained in `journalctl --list-boots`, so no root cause was recoverable from
  logs.
- 2026-05-20 serial-close finding: camera-only observation shows the visual
  diagnostic can keep looping without an active serial monitor. Short RFC2217
  monitor sessions can leave the ESP32-S3/CrowPanel app visually stuck or blank
  with the rear LEDs frozen when the serial session closes. This has now been
  reproduced with both the IO diagnostic and the LVGL diagnostic. The workbench
  host can remain reachable in this state, so this currently looks more like a
  USB-Serial/JTAG/RFC2217 lifecycle issue than a total workbench failure. Use
  `tools/espwb-esptool flash-id` to recover the DUT after closing a monitor.
  A firmware-side test with `logger.deassert_rts_dtr: true` still reproduced
  the blank/frozen display after serial close, so the current mitigation is
  workflow/tooling rather than an ESPHome logger setting.
- 2026-05-20 tooling correction: the project workbench SSH wrappers now ignore
  global SSH config by default with `SSH_CONFIG=/dev/null`, because a malformed
  host SSH config can break project-local workbench commands before they connect.
  If `/host-ssh` is not mounted in the Codex session, set `ESPWB_SSH_KEY`
  locally when running the workbench wrappers. Do not print or commit key
  contents.
- Camera debugging is available on the Linux host:
  - USB device: Creative Technology Live! Cam Chat HD
  - Stable V4L path:
    `/dev/v4l/by-id/usb-Creative_Technology_Ltd._Live__Cam_Chat_HD_VF0790_2015032504121-video-index0`
  - Capture helper: `tools/crowpanel-camera-capture`
  - Sequence helper: `tools/crowpanel-camera-sequence`
  - Captures are written under ignored `artifacts/`.
- Earlier 2026-05-20 camera observation after resetting the CrowPanel with
  `tools/espwb-esptool flash-id`: serial logs showed phase 0/1/2 cycling, but
  camera frames showed the rear LEDs visually staying green/cyan and the round
  LCD remaining black. That failure was superseded by the tuned stable build
  described above.
- Previous CrowPanel display test example:
  `examples/crowpanel-128-display-test/crowpanel-128-display-test.yaml`
- Previous CrowPanel backlight example:
  `examples/crowpanel-128-backlight/crowpanel-128-backlight.yaml`
- Previous CrowPanel baseline example:
  `examples/crowpanel-128-minimal/crowpanel-128-minimal.yaml`

## Safety rules

- RFC2217 is monitor-only.
- Flashing goes through `tools/espwb-esptool`.
- Use `SLOT1` only unless explicitly approved.
- No secrets in git.
- No `sudo` without explicit approval.
- No GitHub push unless explicitly approved.

## Current unresolved issue

`gh` works in the normal shell, but Codex once reported invalid GitHub authentication. The initial GitHub repo creation and push were completed manually from the shell. Future GitHub operations from Codex should verify `gh auth status` inside Codex's own command environment before attempting GitHub operations.

## Reusable platform repo

- Local path: sibling `esp-codex-platform` checkout
- Local initial commit: `57c98ed Create ESP Codex platform starter`
- Status: private GitHub repo created and pushed.
- Scope: reusable ESPHome/devcontainer/workbench starter with generic docs,
  safe workbench wrappers, validation script, ignore rules, and generic blink
  examples. CrowPanel-specific YAML, hardware facts, artifacts, generated
  firmware, secrets, and Home Assistant device UI were intentionally excluded.
