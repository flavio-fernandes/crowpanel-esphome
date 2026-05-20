# Session 10 handoff

## Current session title

10 -- CrowPanel ESPHome LVGL Devcontainer on Linux Host + ESP Workbench

## Suggested next session title

11 -- CrowPanel ESPHome LVGL First Build, Flash, and Serial Validation

## Goal

Use VS Code from Mac, SSH into a Linux host, and from there use Docker/devcontainers that interact with the ESP workbench.

Target firmware stack:

- ESPHome
- LVGL
- Elecrow CrowPanel 1.28 inch ESP32 rotary display

## Current architecture

Mac -> VS Code SSH / regular ssh to Linux host -> Linux host runs Docker and devcontainers -> Linux host reaches workbench over isolated LAN -> workbench controls ESP boards over USB

## Network facts

- Mac cannot directly reach workbench.
- Mac can SSH to the Linux host.
- Linux host name/user: local setup value, not committed.
- workbench hostname: `workbench`
- workbench user: `pi`
- workbench IP: local setup value in ignored `config/workbench.env`
- workbench API from Linux host: `${WORKBENCH_URL}`
- workbench service: `rfc2217-portal`

## Important flashing rule

RFC2217 is OK for serial monitor only.

Do not use RFC2217 reset control for flashing.

For chip-id, flash-id, read-flash, write-flash, and firmware flashing, SSH to workbench and run local esptool through:

`/usr/local/bin/espwb-local-esptool`

Example:

```bash
tools/espwb-esptool flash-id
```

## Validated Step 10A

Step 10A passed with no warnings or failures.

Validated:

- workspace skeleton exists
- baseline path exists locally
- Linux host arch is `aarch64`
- Docker works without sudo
- Docker Engine observed: `29.5.0`
- docker buildx available
- docker compose available
- devcontainer CLI observed: `0.87.0`
- Linux host can reach workbench API
- workbench API showed `slots_configured: 7`, `slots_running: 1`
- SSH to workbench works
- `/usr/local/bin/espwb-local-esptool` exists and is executable
- `SLOT1 flash-id` works through the reset-aware helper
- workbench API came back after flash-id
- smoke wrapper exists locally

Detected board in SLOT1 during Step 10A:

- ESP32-D0WDQ6 revision v1.0
- MAC: observed locally; omitted from committed docs
- flash size: 4MB

## Workspace

This repository checkout.

Expected directories:

- `.devcontainer/`
- `tools/`
- `esphome/`
- `docs/`
- `artifacts/`

## Codex guardrails

Codex may edit files inside this workspace.

Codex must not:

- run `sudo`
- modify files outside this workspace
- modify SSH key directories
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
