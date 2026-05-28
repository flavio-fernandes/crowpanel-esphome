# ESPHome and LVGL notes for CrowPanel

Captured: 2026-05-19

Reviewed: 2026-05-28.

This is not firmware. It began as the compatibility and bring-up plan before
creating the first CrowPanel ESPHome YAML. Keep using it as the hardware/LVGL
reference trail; use `../../current-state.md` for the current firmware state.

## Capability mapping

| CrowPanel feature | Likely ESPHome component path | Notes |
| --- | --- | --- |
| ESP32-S3R8 MCU | `esp32`, ESP-IDF framework likely preferred | Need select a board id and PSRAM/flash settings deliberately. |
| GC9A01A 240 x 240 SPI display | `display: mipi_spi` for LVGL; `display: ili9xxx` for native diagnostics | Elecrow's ESPHome lessons and bruxy70 `esphome-lvgl` guidance originally used `ili9xxx` for GC9A01A round displays, but ESPHome deprecated `ili9xxx`. The current validated LVGL path is `mipi_spi` GC9A01A at 20MHz. Native display-test/diagnostic examples still use the physically proven `ili9xxx` path because the native `mipi_spi` display-test stayed blank. |
| CST816D capacitive touch | `touchscreen: cst816` | ESPHome `cst816` requires I2C and supports the CST816 family. |
| Rotary knob rotation | `sensor: rotary_encoder` | Use GPIO45/GPIO42 from Elecrow. Direction can be reversed by swapping A/B in config. |
| Knob press | `binary_sensor: gpio` | GPIO41. Useful as an LVGL select/enter input later. |
| Backlight | `output` plus `light`, or simple GPIO first | GPIO46 is a strapping pin; bring this up carefully after boot. |
| Ambient LEDs | `light: esp32_rmt_led_strip` or equivalent addressable LED path | GPIO48, 5 WS2812 LEDs. Defer until basic display/touch/encoder are stable. |
| SSD1306 OLED | `display: ssd1306_i2c` | Present on GPIO38/GPIO39, but not needed for first CrowPanel display bring-up. |
| Home Assistant | `api`, HA sensor imports, services, events | Add after the local UI and hardware path are stable. |
| LVGL UI | `lvgl` | ESPHome LVGL supports displays, touchscreens, and rotary encoder style input. |

## ESPHome/LVGL constraints to remember

- LVGL should own rendering once enabled.
- The graphical display should avoid a `lambda` once LVGL is driving it.
- ESPHome LVGL docs recommend `auto_clear_enabled: false` and usually
  `update_interval: never` for displays used by LVGL.
- Touch can be added before LVGL as a hardware validation step.
- Rotary can be added before LVGL as a sensor validation step.
- Home Assistant integration should wait until the local hardware loop is known
  good, so network/API issues do not get mixed with display/touch bugs.
- Home Assistant service/action calls from ESPHome require explicitly enabling
  that device to perform HA actions in the ESPHome integration settings.
- For the 240 x 240 round display, design UI screens as 240 x 240 SVG mockups
  first when the layout is non-trivial; remember that pixels outside the
  inscribed circle are physically hidden.
- Keep the first LVGL page static and boring: one display, one touchscreen, one
  page, a small font set, and no Home Assistant entities until rendering and
  input are proven.

## LVGL YAML shape to prefer later

For the first real LVGL YAML, keep sections in this order:

1. `substitutions`
2. `esphome`
3. `esp32`
4. `psram`
5. `logger`
6. `i2c`
7. `output`
8. `light`
9. `touchscreen`
10. `display`
11. `image`
12. `font`
13. `lvgl`
14. `sensor`, `text_sensor`, `binary_sensor`, `switch`, `number`

Notes from `bruxy70/ha-development`:

- Use lowercase snake_case IDs.
- Define fonts and images before LVGL references them.
- Prefer `style_definitions` for repeated LVGL styles.
- Use `on_release` rather than `on_value` for sliders/arcs that call Home
  Assistant services.
- Use `scrollbar_mode: "off"` and `scrollable: false` on containers that
  should not capture drag gestures.
- For arc widgets, consider `adv_hittest: true` so touches through the center
  do not trigger the arc accidentally.
- Lambda text must return the type ESPHome expects, usually `std::string` for
  dynamic label text.

## Recommended bring-up sequence

1. Confirm physical SLOT1 identity after the CrowPanel is installed.
2. Create the smallest ESP32-S3 ESPHome YAML with serial logger only.
3. Validate with `esphome config`.
4. Compile without flashing first.
5. Flash only through `tools/espwb-esptool` on `SLOT1`.
6. Add one low-risk GPIO indicator or backlight test after boot.
7. Add SPI display with a built-in test card or minimal native rendering.
8. Add CST816D touch and log touch events.
9. Add rotary encoder and knob press logging.
10. Add LVGL with one static page.
11. Add Home Assistant API/imported entities and UI interactions.

## Initial bring-up rule

- LVGL.
- Home Assistant API.
- OTA.
- Wi-Fi credentials beyond what is strictly necessary, if any.
- Display, touch, rotary, OLED, and WS2812 all at once.
- Any large UI definition.

This rule applied to the first hardware bring-up YAMLs. The current production
firmware intentionally includes LVGL, Wi-Fi, API, OTA, and Home Assistant
entities after those pieces were validated incrementally.

## Early validation commands

Use the existing workbench flow:

```bash
devcontainer exec --workspace-folder . esphome config <crowpanel-yaml>
devcontainer exec --workspace-folder . esphome compile <crowpanel-yaml>
devcontainer exec --workspace-folder . tools/espwb-esptool flash-id
```

Only after config, compile, and identity checks pass:

```bash
devcontainer exec --workspace-folder . tools/espwb-esptool write-flash 0x0 <firmware.factory.bin>
```

Do not use RFC2217 for flashing or reset control.

## Bring-up notes

- 2026-05-19: `examples/crowpanel-128-backlight/crowpanel-128-backlight.yaml`
  compiled and flashed, but the screen remained visually blank because that
  firmware did not initialize or draw to the GC9A01A panel.
- 2026-05-19: `examples/crowpanel-128-display-test/crowpanel-128-display-test.yaml`
  validated, compiled, and flashed. It enables GPIO46 on boot and draws a
  native ESPHome `mipi_spi` GC9A01A color quadrant/crosshair pattern. Awaiting
  visual confirmation on the physical LCD.
- 2026-05-20: The `mipi_spi` display test remained blank on the physical LCD.
  Elecrow's own ESPHome lessons for this exact 1.28 inch rotary CrowPanel use
  `display: ili9xxx`, `model: GC9A01A`, GPIO9 CS, GPIO3 DC, GPIO14 reset,
  GPIO10 SCLK, GPIO11 MOSI, GPIO46 LEDC backlight, `invert_colors: true`, and
  `show_test_card: true` for bring-up. The local display test is being adjusted
  to match that known Elecrow ESPHome path.
- 2026-05-20: `examples/crowpanel-128-io-diagnostic/crowpanel-128-io-diagnostic.yaml`
  validated, compiled, and flashed. Runtime logs confirm the diagnostic cycles
  every 3 seconds through GPIO48 ambient LEDs, GPIO46 backlight levels, GPIO40,
  and LCD fill updates. Awaiting physical observation of which outputs actually
  change.
- 2026-05-20: The diagnostic now also drives GPIO1 and GPIO2, matching
  Elecrow's `out1` and `out2` examples. An intermediate build boot-looped
  because `on_boot` priority `800` attempted to set GPIO46 LEDC before the
  output was initialized. The flashed build now uses `on_boot` priority `-100`;
  serial logs show phase 0/1/2 advancing without the LEDC panic.
- 2026-05-20: Last physical observation before the `on_boot` priority fix was
  solid red rear LEDs and a fully black round LCD with no visible glow. Re-test
  visually against the fixed diagnostic before concluding the display or
  backlight path is physically bad.
- 2026-05-20: A USB camera on the Linux host is now usable for visual debugging through
  `tools/crowpanel-camera-capture` and `tools/crowpanel-camera-sequence`.
  Captures after an esptool reset show the rear LEDs visually green/cyan while
  the round LCD remains black, even though serial logs continue reporting phase
  0/1/2. Next display/LED diagnostics should be camera-friendly: keep backlight
  at 100%, avoid same-period camera/firmware timing, and change one visible
  output at a time.
- 2026-05-20: The tuned IO diagnostic is stable enough to serve as the current
  visual baseline. Changes that mattered: `ili9xxx` GC9A01A `data_rate: 20MHz`,
  constant 60% GPIO46 backlight, GPIO40/GPIO1/GPIO2 held on, GPIO48 WS2812
  brightness 40%, and `use_psram: false` for the LED strip. A 125 second serial
  soak showed every LCD update returning, and camera captures confirmed the
  LCD target/crosshair plus rear RGB LEDs cycling through red, green, and blue.
- 2026-05-20: CST816 touch was added to the stable visual baseline using
  Elecrow's ESPHome pins and transform: I2C SDA GPIO6, SCL GPIO7, address
  `0x15`, INT GPIO5, reset GPIO13, `mirror_y: true`, and `swap_xy: true`.
  Taps and drags produced transformed/raw coordinate logs while the LCD/RGB
  loop continued running.
- 2026-05-20: Rotary encoder and knob button logging were added to the
  diagnostic baseline using GPIO45/GPIO42 for A/B and GPIO41 for the active-low
  press input. The refreshed YAML passed `esphome config`, compiled, flashed to
  SLOT1 through `tools/espwb-esptool`, and camera capture confirmed the LCD/RGB
  diagnostic still runs after flashing. Runtime interaction logs captured knob
  rotation in both directions plus button press/release events while touch and
  display updates continued working.
- 2026-05-21: The LVGL diagnostic display block was migrated from deprecated
  `ili9xxx` to `mipi_spi` while keeping the same GC9A01A model, GPIO9 CS, GPIO3
  DC, GPIO14 reset, 240 x 240 dimensions, `invert_colors: true`, and 20MHz SPI
  data rate. `esphome config` and `esphome compile` passed without the
  deprecation warning, flashing to SLOT1 verified successfully, and camera
  capture `artifacts/crowpanel-camera-20260521T202218Z.jpg` showed the LVGL UI
  rendered on the round LCD.
- 2026-05-21: The older display-test and IO diagnostic examples were briefly
  migrated to `mipi_spi` and both YAML files passed `esphome config` and
  `esphome compile`, but flashing the native display-test left the physical LCD
  blank. Those native diagnostics were restored to `ili9xxx`; the LVGL
  diagnostic remains on the physically verified `mipi_spi` path. The
  display-test boot sequence stayed aligned with the stable post-initialization
  GPIO46 backlight pattern.
- 2026-05-20: Workbench temporarily became unreachable from the Linux host with
  incomplete ARP and `Destination Host Unreachable`; reboot restored SSH and
  RFC2217. Current boot health was normal and journal history was volatile, so
  no prior-boot root cause was available. If this repeats, capture uptime,
  `vcgencmd get_throttled`, `journalctl --list-boots`, and network reachability
  before rebooting.
