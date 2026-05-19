# ESPHome configs

This directory will hold CrowPanel ESPHome YAML files.

For now, do not add full display, touch, rotary encoder, or LVGL config until the devcontainer and workbench tools are validated.

Secrets strategy:

- Put real secrets in `esphome/secrets.yaml`.
- Never commit `secrets.yaml`.
- Commit only safe examples such as `secrets.yaml.example`.
