# ESPHome workbench cheat sheet

## Current architecture

Mac -> VS Code SSH -> argon -> devcontainer -> workbench -> SLOT1 board

## Required assumptions

- Docker works without `sudo` on argon.
- The devcontainer CLI works on argon.
- The workbench API is reachable at `http://192.168.1.235:8080`.
- SSH to `pi@192.168.1.235` works.
- `/usr/local/bin/espwb-local-esptool` exists on the workbench.
- `SLOT1` is the only safe default slot.

## Devcontainer commands

```bash
devcontainer up --workspace-folder .
devcontainer exec --workspace-folder . esphome version
devcontainer exec --workspace-folder . tools/validate-workbench.sh
```

## ESPHome validation commands

```bash
devcontainer exec --workspace-folder . esphome config examples/feather-huzzah32-blink/feather-huzzah32-blink.yaml
devcontainer exec --workspace-folder . esphome compile examples/feather-huzzah32-blink/feather-huzzah32-blink.yaml
```

## Pre-flash identity check

```bash
devcontainer exec --workspace-folder . tools/espwb-esptool flash-id
```

Expected safe identity before flashing the current SLOT1 board:

- ESP32-D0WDQ6
- 4MB flash
- SLOT1 only

## Known-good flash command

```bash
devcontainer exec --workspace-folder . tools/espwb-esptool write-flash 0x0 examples/feather-huzzah32-blink/.esphome/build/feather-huzzah32-blink/.pioenvs/feather-huzzah32-blink/firmware.factory.bin
```

## Serial monitor note

RFC2217 is for monitoring only, not flashing or reset control.

## Troubleshooting

- If `firmware.factory.bin` is missing, do not guess offsets.
- If `SLOT1` does not show ESP32-D0WDQ6 and 4MB flash, stop.
- If the workbench API does not come back after esptool, check `rfc2217-portal` on the workbench.
- If compile is slow, this is expected on first run because caches are being populated.

## Safety rules

- No secrets in git.
- No flashing slots other than `SLOT1` unless explicitly approved.
- No `sudo` unless explicitly approved.
- No GitHub push yet.
