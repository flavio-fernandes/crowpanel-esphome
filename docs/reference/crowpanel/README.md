# CrowPanel reference capture

Step: 10E0

Captured: 2026-05-19

Purpose: keep the CrowPanel bring-up grounded in local, attributed notes before
creating any CrowPanel ESPHome YAML.

## Local files

- `hardware-facts.md`: Hardware facts extracted from Elecrow primary sources.
- `esphome-lvgl-notes.md`: ESPHome/LVGL capability mapping and bring-up order.

## Primary sources

### Elecrow wiki

URL: https://www.elecrow.com/wiki/CrowPanel_1.28inch-HMI_ESP32_Rotary_Display.html

Use this as the primary hardware source. It includes the board specification,
display/touch/rotary pin definitions, and the Elecrow GitHub resource link.

### Elecrow product page

URL: https://www.elecrow.com/crowpanel-1-28inch-hmi-esp32-rotary-display-240-240-ips-round-touch-knob-screen.html

Use this to corroborate the product SKU, ESP32-S3R8, 8 MB PSRAM, 16 MB flash,
240 x 240 display, GC9A01 display driver, capacitive touch, buttons, and
connectors.

### Elecrow GitHub repository

URL: https://github.com/Elecrow-RD/CrowPanel-1.28inch-HMI-ESP32-Rotary-Display-240-240-IPS-Round-Touch-Knob-Screen

Use this for source examples, datasheets, schematic/PCB files, factory firmware,
factory source code, and the README pin definitions.

### Elecrow ESPHome course

URL: https://www.elecrow.com/wiki/CrowPanel_HMI_ESP32_Rotary_Display_ESPHome_course.html

Use this for Elecrow's own ESPHome lesson sequence and the matching YAML files
under `example/esphome/` in the Elecrow GitHub repository.

## Supporting sources

### ESPHome display docs

URL: https://esphome.io/components/display/

Use this for general display behavior and the split between ESPHome's native
rendering engine and LVGL.

### ESPHome MIPI SPI display docs

URL: https://esphome.io/components/display/mipi_spi.html

Use this as the current validated ESPHome display driver path for the GC9A01A
240 x 240 panel.

### ESPHome ILI9xxx display docs

URL: https://esphome.io/components/display/ili9xxx/

Historical reference only for this repo. Early bring-up used `ili9xxx` because
Elecrow's examples used it, but ESPHome now deprecates it and the local
CrowPanel examples have been moved to `mipi_spi`.

### ESPHome CST816 touchscreen docs

URL: https://esphome.io/components/touchscreen/cst816.html

Use this for the capacitive touchscreen component. The CrowPanel wiki names the
touch controller as CST816D; ESPHome's `cst816` component supports the CST816
family.

### ESPHome rotary encoder docs

URL: https://esphome.io/components/sensor/rotary_encoder

Use this for the knob rotation input.

### ESPHome LVGL docs

URL: https://esphome.io/components/lvgl/

Use this for LVGL display/touch/encoder integration.

### bruxy70 ha-development

URL: https://github.com/bruxy70/ha-development

Use the `esphome-lvgl` skill as a practical checklist for ESPHome/LVGL YAML
structure, GC9A01A round-display conventions, touch debugging, Home Assistant
action authorization, and common LVGL pitfalls. Use the `svg-rendering` skill
for pixel-accurate 240 x 240 UI mockups before committing complex LVGL pages to
firmware.

### Espressif ESP32-S3 hardware design guidelines

URL: https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html

Use this for boot strapping pin caution. This matters because Elecrow assigns
GPIO45 and GPIO46 to user-facing hardware.

## Deliberately not captured yet

- No CrowPanel ESPHome YAML.
- No downloaded factory firmware binaries.
- No copied secrets.
- No flashing notes beyond the existing workbench safety docs.
