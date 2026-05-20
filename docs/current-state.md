# Current state

## Repository

- Repo: `https://github.com/flavio-fernandes/crowpanel-esphome.git`
- Branch: `main`
- Roadmap: `docs/roadmap.md`

Current validated commits:

- `a4f612e` Add CrowPanel ESPHome devcontainer foundation
- `271bd8f` Add known-good ESPHome workbench blink example
- `529d390` Document GitHub setup for argon workflow
- `c35f23b` Add HUZZAH32 heartbeat blink example

## Architecture

Mac -> VS Code SSH -> argon -> devcontainer -> workbench -> SLOT1 board

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
- MAC observed during flash-id: `3c:0f:02:db:e9:14`

## Current CrowPanel firmware state

- Factory/demo firmware was backed up before flashing ESPHome.
- Backup path: `artifacts/crowpanel-slot1-factory-demo-2026-05-19.bin`
- Backup size: 16,777,216 bytes
- Backup SHA-256: `e11671b2f0d95d75cb4e992138795cae351c29363ec51bae2d73e3e67a7c3bbc`
- Current flashed ESPHome example:
  `examples/crowpanel-128-io-diagnostic/crowpanel-128-io-diagnostic.yaml`
- Current firmware scope: minimal ESP32-S3 ESPHome logger with 16MB flash,
  octal 80MHz PSRAM configuration, GPIO46 LEDC screen backlight diagnostics,
  GPIO40 diagnostics, GPIO1/GPIO2 output enables, GPIO48 WS2812 ambient LED
  diagnostics, and an Elecrow-style ESPHome `ili9xxx` GC9A01A display fill
  diagnostic using SCLK GPIO10, MOSI GPIO11, CS GPIO9, DC GPIO3, and reset
  GPIO14. The diagnostic runs the GC9A01A SPI bus at 20MHz, keeps backlight at
  60%, keeps GPIO40/GPIO1/GPIO2 enabled, and keeps the WS2812 buffer out of
  PSRAM. No touch, rotary, LVGL, Wi-Fi, API, OTA, or Home Assistant integration
  yet.
- Serial monitor status: RFC2217 monitor shows the diagnostic firmware cycling
  phases every 5 seconds:
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
- Optional next debugging aid: point a camera at the CrowPanel from argon and
  capture still frames into `artifacts/` so Codex can compare visual output
  with serial logs.
- Camera debugging is available on argon:
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

`gh` works in the normal argon shell, but Codex once reported invalid GitHub authentication. The initial GitHub repo creation and push were completed manually from the argon shell. Future GitHub operations from Codex should verify `gh auth status` inside Codex's own command environment before attempting GitHub operations.
