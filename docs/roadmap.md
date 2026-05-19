# Roadmap

## Completed milestones

- Created the CrowPanel ESPHome workspace at `/home/ff/src/crowpanel-esphome`.
- Added and validated the devcontainer foundation.
- Added reset-aware workbench wrappers in `tools/`.
- Validated the workbench path from inside the devcontainer.
- Built and flashed a throwaway ESPHome Feather/HUZZAH32 blink example on `SLOT1`.
- Confirmed real GPIO13 onboard LED blinking every 500 ms.
- Created and pushed the private GitHub repo `flavio-fernandes/crowpanel-esphome`.
- Added handoff docs for future Codex threads.

## Current repo state

- Repo: `https://github.com/flavio-fernandes/crowpanel-esphome.git`
- Branch: `main`
- Current architecture: Mac -> VS Code SSH -> argon -> devcontainer -> workbench -> SLOT1 board
- Known-good example: `examples/feather-huzzah32-blink/feather-huzzah32-blink.yaml`
- Known-good workflow: ESPHome YAML -> `esphome config` -> `esphome compile` -> `tools/espwb-esptool write-flash` -> real GPIO13 blink.

## Remaining CrowPanel project steps

- Capture Elecrow CrowPanel reference material locally.
- Identify and record the CrowPanel pinout, display controller, touch controller, rotary encoder pins, backlight behavior, and any boot/strap-sensitive pins.
- Create the first minimal CrowPanel ESPHome YAML in a small step.
- Validate `esphome config` before compiling.
- Compile the minimal CrowPanel firmware before adding display or LVGL complexity.
- Flash only through `tools/espwb-esptool` on `SLOT1`.
- Bring up hardware features incrementally:
  - serial logger
  - backlight GPIO or PWM
  - display bus and panel
  - touch
  - rotary encoder
  - LVGL
  - Home Assistant/API/OTA only after the local hardware path is stable
- Record each validated milestone in docs before expanding the YAML.

## Future reusable platform repo plan

A future reusable platform repo should be named `esp-codex-platform`.

It should capture the reusable pieces that have emerged from this CrowPanel workspace:

- argon bootstrap docs/scripts
- workbench bootstrap docs/scripts
- devcontainer template
- `tools/espwb-esptool` pattern
- `tools/validate-workbench.sh` pattern
- `AGENTS.md` template
- `README` template
- `project-sources` and reference capture template
- GitHub setup flow
- known-good ESPHome blink example
- troubleshooting docs

Do not extract `esp-codex-platform` yet.

Reason: first prove the CrowPanel compile, flash, display, touch, rotary, and LVGL workflow end to end. After those pieces are validated in this real project, extract only the reusable, boring parts into the platform repo.

## Things not to forget

- RFC2217 is for serial monitoring only.
- Flashing must go through `tools/espwb-esptool`.
- `SLOT1` is the only safe default slot unless explicitly approved.
- Do not use RFC2217 reset control for flashing.
- Do not create a large CrowPanel YAML in one jump.
- Keep secrets, `.env` files, private keys, firmware binaries, `artifacts/`, and `.esphome/` out of git.
- Verify `gh auth status` in Codex's own command environment before GitHub operations.
- Do not push to GitHub unless explicitly approved.
- Do not use `sudo` unless explicitly approved.

## Recommended next Codex thread prompt

```text
Read AGENTS.md, README.md, docs/current-state.md, docs/roadmap.md, docs/esphome-workbench-cheatsheet.md, docs/github-setup.md, and docs/project-sources.md.

Do not modify files yet.

Summarize the project state.

Then propose Step 10E0 only: capture Elecrow CrowPanel references locally.

Do not create CrowPanel YAML yet.
Do not flash anything.
```
