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

Use the restricted bench-agent flow:

```bash
devcontainer exec --workspace-folder . esphome config <crowpanel-yaml>
devcontainer exec --workspace-folder . esphome compile <crowpanel-yaml>
devcontainer exec --workspace-folder . tools/espwb-esptool flash-id
```

Only after config, compile, and identity checks pass:

```bash
devcontainer exec --workspace-folder . tools/espwb-esptool write-flash 0x0 <firmware.factory.bin>
```

Use only the restricted SSH flash verb; monitoring never resets on exit.

## Bring-up evidence

The dated physical observations are preserved in [history](../../history/crowpanel-esphome-lvgl-notes.md); they do not validate the new bench transport.
