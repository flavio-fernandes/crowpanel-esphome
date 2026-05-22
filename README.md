# CrowPanel ESPHome workspace

Goal: develop ESPHome + LVGL firmware for the Elecrow CrowPanel 1.28 inch ESP32 rotary display using this path:

Mac -> VS Code SSH -> Linux host -> Docker/devcontainer -> ESP workbench -> USB ESP board

Current safety rule:

- Use `tools/espwb-esptool` for flashing and esptool operations.
- Use RFC2217 only for serial monitoring.
- Do not use RFC2217 reset control for flashing.

Important paths:

- Workspace: this repository checkout
- Local workbench settings: `config/workbench.env`
- Workbench API: `${WORKBENCH_URL}`
- Workbench helper: `/usr/local/bin/espwb-local-esptool`
- Default slot: `SLOT1`
- Default RFC2217 monitor port: `${ESP_PORT}`

First-time local setup:

```bash
cp config/workbench.env.example config/workbench.env
$EDITOR config/workbench.env
```

Useful commands inside the devcontainer:

```bash
tools/validate-workbench.sh
tools/espwb-esptool flash-id
tools/espwb-esptool chip-id
tools/espwb-monitor
python3 -m esptool version
esphome version
```

`tools/espwb-monitor` opens raw DUT serial logs over the RFC2217 monitor port
and runs a reset-aware `tools/espwb-esptool flash-id` after the monitor exits to
recover from the known CrowPanel blank/frozen-on-monitor-close behavior.

Known-good example:

- Throwaway Feather/HUZZAH32 blink YAML: `examples/feather-huzzah32-blink/feather-huzzah32-blink.yaml`
- ESPHome workbench cheat sheet: `docs/esphome-workbench-cheatsheet.md`

Step flow:

1. Validate baseline and skeleton.
2. Create devcontainer and workbench tools.
3. Validate devcontainer.
4. Add minimal ESPHome boilerplate.
5. Add CrowPanel display, backlight, LVGL, rotary, touch, and Home Assistant pieces incrementally.
