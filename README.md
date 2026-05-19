# CrowPanel ESPHome workspace

Goal: develop ESPHome + LVGL firmware for the Elecrow CrowPanel 1.28 inch ESP32 rotary display using this path:

Mac -> VS Code SSH -> argon -> Docker/devcontainer -> ESP workbench -> USB ESP board

Current safety rule:

- Use `tools/espwb-esptool` for flashing and esptool operations.
- Use RFC2217 only for serial monitoring.
- Do not use RFC2217 reset control for flashing.

Important paths:

- Workspace on argon: `/home/ff/src/crowpanel-esphome`
- Workbench API: `http://192.168.1.235:8080`
- Workbench helper: `/usr/local/bin/espwb-local-esptool`
- Default slot: `SLOT1`
- Default RFC2217 monitor port: `rfc2217://192.168.1.235:4001?ign_set_control`

Useful commands inside the devcontainer:

```bash
tools/validate-workbench.sh
tools/espwb-esptool flash-id
tools/espwb-esptool chip-id
python3 -m esptool version
esphome version
```

Step flow:

1. Validate baseline and skeleton.
2. Create devcontainer and workbench tools.
3. Validate devcontainer.
4. Add minimal ESPHome boilerplate.
5. Add CrowPanel display, backlight, LVGL, rotary, touch, and Home Assistant pieces incrementally.
