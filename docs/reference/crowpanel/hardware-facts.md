# CrowPanel hardware facts

Captured: 2026-05-19

Product: Elecrow CrowPanel 1.28 inch HMI ESP32 Rotary Display, 240 x 240 IPS
round touch knob screen.

Primary sources:

- Elecrow wiki: https://www.elecrow.com/wiki/CrowPanel_1.28inch-HMI_ESP32_Rotary_Display.html
- Elecrow product page: https://www.elecrow.com/crowpanel-1-28inch-hmi-esp32-rotary-display-240-240-ips-round-touch-knob-screen.html
- Elecrow GitHub: https://github.com/Elecrow-RD/CrowPanel-1.28inch-HMI-ESP32-Rotary-Display-240-240-IPS-Round-Touch-Knob-Screen

## Board summary

| Area | Fact | Source |
| --- | --- | --- |
| Main chip | ESP32-S3R8 | Elecrow wiki, product page, GitHub README |
| CPU | Xtensa LX7 dual core, up to 240 MHz | Elecrow wiki, product page, GitHub README |
| SRAM | 512 KB | Elecrow wiki, product page, GitHub README |
| PSRAM | 8 MB | Elecrow wiki, product page, GitHub README |
| Flash | 16 MB | Elecrow wiki, product page, GitHub README |
| Wireless | 2.4 GHz Wi-Fi, BLE/Bluetooth 5.0 | Elecrow wiki, product page, GitHub README |
| Power input | 5 V / 1 A | Elecrow wiki, product page, GitHub README |
| Logic power | Main chip at 3.3 V | Elecrow wiki, product page, GitHub README |
| Buttons | Reset, boot, knob press | Elecrow wiki, product page, GitHub README |
| Expansion | UART, I2C, 12-pin FPC power/burning port | Elecrow wiki, product page, GitHub README |

## Display

| Area | Fact | Source |
| --- | --- | --- |
| Size | 1.28 inch round IPS | Elecrow wiki, product page, GitHub README |
| Resolution | 240 x 240 | Elecrow wiki, product page, GitHub README |
| Driver | GC9A01 / GC9A01A family | Elecrow wiki code and product comparison |
| Bus | SPI, Elecrow sample uses SPI2_HOST, mode 0, write clock 80 MHz | Elecrow wiki code |
| SCLK | GPIO10 | Elecrow wiki code |
| MOSI | GPIO11 | Elecrow wiki code |
| MISO | Not used | Elecrow wiki code |
| DC | GPIO3 | Elecrow wiki code |
| CS | GPIO9 | Elecrow wiki code |
| RST | GPIO14 | Elecrow wiki code |
| Backlight | GPIO46 | Elecrow wiki pin list |
| Display dimensions | memory_width/panel_width 240, memory_height/panel_height 240 | Elecrow wiki code |
| Inversion | Elecrow sample sets display invert to true | Elecrow wiki code |

## Touch

| Area | Fact | Source |
| --- | --- | --- |
| Touch type | Capacitive touch | Elecrow wiki, product page, GitHub README |
| Controller | CST816D | Elecrow wiki code |
| Bus | I2C | Elecrow wiki code |
| SDA | GPIO6 | Elecrow wiki pin list |
| SCL | GPIO7 | Elecrow wiki pin list |
| INT | GPIO5 | Elecrow wiki pin list |
| RST | GPIO13 | Elecrow wiki pin list |

## Rotary encoder and buttons

| Area | Fact | Source |
| --- | --- | --- |
| Rotation A | GPIO45 | Elecrow wiki pin list, GitHub README |
| Rotation B | GPIO42 | Elecrow wiki pin list, GitHub README |
| Knob press | GPIO41 | Elecrow wiki pin list, GitHub README |
| Boot button | Present, pin not yet captured from schematic | Elecrow wiki, product page |
| Reset button | Present, reset line not yet captured from schematic | Elecrow wiki, product page |

## Other onboard devices

| Area | Fact | Source |
| --- | --- | --- |
| OLED | SSD1306 I2C, SDA GPIO38, SCL GPIO39 | Elecrow wiki pin list, GitHub README |
| RGB ambient LEDs | WS2812, GPIO48, 5 LEDs | Elecrow wiki pin list |
| Power indicator | GPIO40 | Elecrow wiki pin list |
| Test I/O | GPIO4, GPIO12 | Elecrow wiki pin list |

## Boot and strapping cautions

ESP32-S3 strapping pins include GPIO0, GPIO3, GPIO45, and GPIO46. Elecrow uses:

- GPIO3 as display DC.
- GPIO45 as rotary encoder A.
- GPIO46 as screen backlight.

Implication for bring-up: avoid strong external pulls or boot-time drive states
on those lines. Start with the vendor hardware as-is, do not attach extra loads,
and be suspicious of any firmware behavior that drives GPIO45/GPIO46 early during
boot. This is especially relevant to PWM backlight and rotary input testing.

Source: Espressif ESP32-S3 hardware design guidelines.

## Resolved bring-up questions

- Preferred first display path: `ili9xxx` with `model: GC9A01A`. The first
  `mipi_spi` attempt stayed blank on this board, while `ili9xxx` matched
  Elecrow's ESPHome examples and now produces a stable visual diagnostic.
- GPIO46 backlight is active-high and LEDC/PWM-capable when driven after boot.
  The current stable diagnostic uses a fixed 60% level.
- Current ESPHome board baseline: `esp32-s3-devkitc-1`, `flash_size: 16MB`,
  ESP-IDF framework, octal 80MHz PSRAM, and PlatformIO flags matching the
  local examples.
- Safest first firmware sequence has been proven as logger-only, then
  backlight/indicator, then display/ambient LEDs.

## Open questions for next steps

- Does the CrowPanel need `skip_probe` for CST816D/CST816-family touch startup,
  or does normal I2C probing work reliably?
- Do GPIO45/GPIO42 need swapped in ESPHome to make rotary direction feel
  natural?
- Does GPIO41 knob press need pull-up or inverted semantics?
