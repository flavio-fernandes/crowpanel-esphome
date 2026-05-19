# Session 10 handoff

## Current session title

10 -- CrowPanel ESPHome LVGL Devcontainer on Argon + ESP Workbench

## Suggested next session title

11 -- CrowPanel ESPHome LVGL First Build, Flash, and Serial Validation

## Goal

Use VS Code from Mac, SSH into argon, and from argon use Docker/devcontainers that interact with the ESP workbench.

Target firmware stack:

- ESPHome
- LVGL
- Elecrow CrowPanel 1.28 inch ESP32 rotary display

## Current architecture

Mac -> VS Code SSH / regular ssh to argon -> argon runs Docker and devcontainers -> argon reaches workbench over isolated LAN -> workbench controls ESP boards over USB

## Network facts

- Mac cannot directly reach workbench.
- Mac can SSH to argon using `ssh ff@argon`.
- argon hostname: `argon`
- argon user: `ff`
- argon Tailscale host: `argon.tail76a4e5.ts.net`
- workbench hostname: `workbench`
- workbench user: `pi`
- workbench IP: `192.168.1.235`
- workbench API from argon: `http://192.168.1.235:8080`
- workbench service: `rfc2217-portal`

## Important flashing rule

RFC2217 is OK for serial monitor only.

Do not use RFC2217 reset control for flashing.

For chip-id, flash-id, read-flash, write-flash, and firmware flashing, SSH to workbench and run local esptool through:

`/usr/local/bin/espwb-local-esptool`

Example:

```bash
ssh pi@192.168.1.235 /usr/local/bin/espwb-local-esptool SLOT1 flash-id
```

## Validated Step 10A

Step 10A passed with no warnings or failures.

Validated:

- workspace skeleton exists at `/home/ff/src/crowpanel-esphome`
- baseline path exists: `/home/ff/espwb-baseline-20260517-112011`
- argon arch is `aarch64`
- Docker works without sudo
- Docker Engine observed: `29.5.0`
- docker buildx available
- docker compose available
- devcontainer CLI observed: `0.87.0`
- argon can reach workbench API
- workbench API showed `slots_configured: 7`, `slots_running: 1`
- SSH to workbench works
- `/usr/local/bin/espwb-local-esptool` exists and is executable
- `SLOT1 flash-id` works through the reset-aware helper
- workbench API came back after flash-id
- smoke wrapper exists at `/home/ff/src/espwb-smoke/tools/espwb-esptool`

Detected board in SLOT1 during Step 10A:

- ESP32-D0WDQ6 revision v1.0
- MAC: `ac:67:b2:09:e9:5c`
- flash size: 4MB

## Workspace

`/home/ff/src/crowpanel-esphome`

Expected directories:

- `.devcontainer/`
- `tools/`
- `esphome/`
- `docs/`
- `artifacts/`

## Codex guardrails

Codex may edit files inside `/home/ff/src/crowpanel-esphome`.

Codex must not:

- run `sudo`
- modify files outside this workspace
- modify `/home/ff/.ssh`
- print or copy private keys
- commit secrets
- push to GitHub without explicit review
- flash slots other than SLOT1
- use RFC2217 reset control for flashing
- create a large CrowPanel ESPHome YAML in one jump

## Next planned step

Step 10B -- Create the ESPHome/CrowPanel devcontainer.

Step 10B should create:

- `.devcontainer/Dockerfile`
- `.devcontainer/devcontainer.json`
- `tools/espwb-ssh`
- `tools/espwb-esptool`
- `tools/validate-workbench.sh`
- `README.md`
- `AGENTS.md`
- `.gitignore`
- local git repo only

Do not push to GitHub yet.

GitHub push should wait until after Step 10C passes and files are reviewed.
