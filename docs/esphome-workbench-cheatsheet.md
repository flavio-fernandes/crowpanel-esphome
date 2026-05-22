# ESPHome workbench cheat sheet

## Current architecture

Mac -> VS Code SSH -> Linux host -> devcontainer -> workbench -> SLOT1 board

## Required assumptions

- Docker works without `sudo` on the Linux host.
- The devcontainer CLI works on the Linux host.
- Local workbench settings are in ignored `config/workbench.env`.
- The workbench API is reachable at `${WORKBENCH_URL}`.
- SSH to `${WORKBENCH_USER}@${WORKBENCH_IP}` works.
- `/usr/local/bin/espwb-local-esptool` exists on the workbench.
- `SLOT1` is the only safe default slot.

## Devcontainer commands

```bash
devcontainer up --workspace-folder .
devcontainer exec --workspace-folder . esphome version
devcontainer exec --workspace-folder . tools/validate-workbench.sh
```

After changing `.devcontainer/Dockerfile` or `.devcontainer/devcontainer.json`,
rebuild and replace the running container:

```bash
devcontainer up --workspace-folder . --remove-existing-container
devcontainer exec --workspace-folder . rg --version
devcontainer exec --workspace-folder . tools/validate-workbench.sh
```

## ESPHome validation commands

```bash
devcontainer exec --workspace-folder . esphome config examples/crowpanel-128-lvgl-diagnostic/crowpanel-128-lvgl-diagnostic.yaml
devcontainer exec --workspace-folder . esphome compile examples/crowpanel-128-lvgl-diagnostic/crowpanel-128-lvgl-diagnostic.yaml
```

Only flash a factory image immediately after a successful compile of the same
YAML. The ignored `.esphome/` build tree can contain stale binaries from older
experiments, and `tools/espwb-esptool write-flash` will flash whatever file path
you pass it.

## Pre-flash identity check

```bash
devcontainer exec --workspace-folder . tools/espwb-esptool flash-id
```

Expected safe identity before flashing the current SLOT1 board:

- ESP32-S3 QFN56
- 16MB flash
- SLOT1 only

## Known-good flash command

```bash
devcontainer exec --workspace-folder . tools/espwb-esptool write-flash 0x0 examples/crowpanel-128-lvgl-diagnostic/.esphome/build/crowpanel-128-lvgl-diagnostic/.pioenvs/crowpanel-128-lvgl-diagnostic/firmware.factory.bin
```

## Blank Screen Recovery

If the DUT is visually stuck or blank after a bad firmware flash or after
closing an RFC2217 serial monitor, keep using the reset-aware workbench helper.
Do not flash through RFC2217.

First try a reset-aware identity check. This often recovers a blank/frozen app
after a serial-monitor close because the helper takes control of the physical
SLOT1 USB serial path and resets the DUT:

```bash
devcontainer exec --workspace-folder . tools/espwb-esptool flash-id
```

If the display is still blank because the flashed app is bad, rebuild the
known-good LVGL diagnostic and flash its factory image:

```bash
devcontainer exec --workspace-folder . esphome config examples/crowpanel-128-lvgl-diagnostic/crowpanel-128-lvgl-diagnostic.yaml
devcontainer exec --workspace-folder . esphome compile examples/crowpanel-128-lvgl-diagnostic/crowpanel-128-lvgl-diagnostic.yaml
devcontainer exec --workspace-folder . tools/espwb-esptool write-flash 0x0 examples/crowpanel-128-lvgl-diagnostic/.esphome/build/crowpanel-128-lvgl-diagnostic/.pioenvs/crowpanel-128-lvgl-diagnostic/firmware.factory.bin
```

After flashing, the LVGL diagnostic should bring the round display back. A
camera capture is the quickest physical confirmation:

```bash
tools/crowpanel-camera-capture
```

## Serial Monitor Logs

RFC2217 is for monitoring only, not flashing or reset control.

Use the project monitor wrapper from the repo root. It reads
`config/workbench.env`, opens raw DUT serial logs over `${ESP_PORT}`, and runs a
reset-aware `flash-id` after the monitor exits because closing RFC2217 sessions
can leave the CrowPanel visually blank or frozen:

```bash
devcontainer exec --workspace-folder . tools/espwb-monitor
```

Press `Ctrl-C` to stop monitoring. The wrapper then runs:

```bash
tools/espwb-esptool flash-id
```

Set `ESPWB_MONITOR_RECOVER=0` only when intentionally debugging the RFC2217
close behavior and you do not want the automatic post-monitor reset check.

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
- If `firmware.factory.bin` exists but you did not just compile that exact YAML
  successfully, treat it as stale and do not flash it.
- If `SLOT1` does not show ESP32-S3 QFN56 and 16MB flash for the CrowPanel,
  stop.
- If the workbench API does not come back after esptool, check `rfc2217-portal` on the workbench.
- If `ssh` fails before connecting because of host SSH config, the project
  wrappers default to `SSH_CONFIG=/dev/null`; if `/host-ssh` is not mounted,
  set `ESPWB_SSH_KEY` in `config/workbench.env` or in the shell without
  printing key contents.
- If compile is slow, this is expected on first run because caches are being populated.

## Safety rules

- No secrets in git.
- No flashing slots other than `SLOT1` unless explicitly approved.
- No `sudo` unless explicitly approved.
- No GitHub push yet.
