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

On the ESP32-S3 CrowPanel, closing a short RFC2217 monitor session has been
observed to leave the app visually stuck or blank while the workbench host stays
reachable. For now, treat monitor close as a possible DUT perturbation and run a
reset-aware identity command afterward:

```bash
devcontainer exec --workspace-folder . tools/espwb-esptool flash-id
```

`tools/validate-workbench.sh` skips its RFC2217 open/close test by default for
this reason. Set `RUN_RFC2217_TEST=1` only when intentionally debugging the
monitor path.

`logger.deassert_rts_dtr: true` was tested and did not prevent the blank/frozen
state after RFC2217 close.

## Troubleshooting

- If `firmware.factory.bin` is missing, do not guess offsets.
- If `SLOT1` does not show ESP32-D0WDQ6 and 4MB flash, stop.
- If the workbench API does not come back after esptool, check `rfc2217-portal` on the workbench.
- If `ssh` fails before connecting because of host SSH config, the project
  wrappers default to `SSH_CONFIG=/dev/null`; if `/host-ssh` is not mounted,
  pass `ESPWB_SSH_KEY=/home/ff/.ssh/id_rsa` without printing key contents.
- If compile is slow, this is expected on first run because caches are being populated.

## Safety rules

- No secrets in git.
- No flashing slots other than `SLOT1` unless explicitly approved.
- No `sudo` unless explicitly approved.
- No GitHub push yet.
