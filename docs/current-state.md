# Current state

## Repository

- Repo: `https://github.com/flavio-fernandes/crowpanel-esphome.git`
- Branch: `main`

Current validated commits:

- `a4f612e` Add CrowPanel ESPHome devcontainer foundation
- `271bd8f` Add known-good ESPHome workbench blink example
- `529d390` Document GitHub setup for argon workflow

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

- Board style: Adafruit ESP32 HUZZAH / Feather ESP32 style board
- Onboard LED: GPIO13
- Detected chip: ESP32-D0WDQ6
- Detected flash: 4MB

## Safety rules

- RFC2217 is monitor-only.
- Flashing goes through `tools/espwb-esptool`.
- Use `SLOT1` only unless explicitly approved.
- No secrets in git.
- No `sudo` without explicit approval.
- No GitHub push unless explicitly approved.

## Current unresolved issue

`gh` works in the normal argon shell, but Codex once reported invalid GitHub authentication. The initial GitHub repo creation and push were completed manually from the argon shell. Future GitHub operations from Codex should verify `gh auth status` inside Codex's own command environment before attempting GitHub operations.
