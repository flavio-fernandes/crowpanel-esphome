# ESPHome configs

This directory holds CrowPanel ESPHome YAML files.

Current primary firmware:

- `crowpanel.yaml` - EGO charger timer UI for the Elecrow CrowPanel 1.28-inch
  ESP32-S3 rotary touch display.

See `../docs/esphome-fresh-clone-flash-cheatsheet.md` for the fresh clone,
secrets, compile, and flash workflow.

Secrets strategy:

- Put real secrets in `esphome/secrets.yaml`.
- Never commit `secrets.yaml`.
- Commit only safe examples such as `secrets.yaml.example`.
