# Fresh clone to flashed CrowPanel firmware

The CrowPanel is not currently on the bench. Hardware steps below require a
future approved installation and confirmed slot identity. SLOT1 is a default,
not evidence of what is attached. See [bench commands](esphome-bench-cheatsheet.md).

## Checkout and local settings

Clone this repository into `crowpanel-esphome` (the devcontainer workspace
folder uses that name). From its root:

```bash
cp config/bench.env.example config/bench.env
cp esphome/secrets.yaml.example esphome/secrets.yaml
```

Edit these ignored files locally. Configure `BENCH_AGENT=bench-agent` using a
restricted SSH key and verified known_hosts; never an administrative login.
The wrappers use normal SSH config/agent handling, not key copying or automatic
host-key trust. In the devcontainer, forward an SSH agent or explicitly select
`BENCH_SSH_CONFIG`, `BENCH_SSH_KEY` and `BENCH_KNOWN_HOSTS` paths from the
read-only `/host-ssh` mount. See [configuration](../config/README.md).

Populate Wi-Fi, API encryption and OTA secrets from your local secret store.
Never print or commit them. ESPHome YAML references them via `!secret`.

## Home Assistant

Install `config/home-assistant/ego-charger-helpers.yaml` as an HA package.
Supply `switch.ego_charger` and `sensor.ego_charger_power`, or change local
substitutions before compilation. The helpers provide preset duration, end
time, timer-active and panel-pending-off entities. After pairing the ESPHome
device, allow it to perform Home Assistant service calls.

## Build environment and client checks

```bash
devcontainer up --workspace-folder .
devcontainer exec --workspace-folder . esphome version
devcontainer exec --workspace-folder . tools/validate-bench.sh
```

Validation calls only help, status and health; it never flashes, resets or
opens a monitor. `BENCH_STATIC_ONLY=1 tools/validate-bench.sh` is offline.
Rebuild the devcontainer after changing its Dockerfile or configuration.

For client development without hardware:

```bash
bench/dev/setup-venv.sh
bench/dev/check.sh
```

## Compile the exact target

```bash
devcontainer exec --workspace-folder . esphome config esphome/crowpanel.yaml
devcontainer exec --workspace-folder . esphome compile esphome/crowpanel.yaml
```

Factory image:
`esphome/.esphome/build/crowpanel/.pioenvs/crowpanel/firmware.factory.bin`.
For the small diagnostic instead:

```bash
devcontainer exec --workspace-folder . esphome config examples/crowpanel-128-lvgl-diagnostic/crowpanel-128-lvgl-diagnostic.yaml
devcontainer exec --workspace-folder . esphome compile examples/crowpanel-128-lvgl-diagnostic/crowpanel-128-lvgl-diagnostic.yaml
```

Its factory image is
`examples/crowpanel-128-lvgl-diagnostic/.esphome/build/crowpanel-128-lvgl-diagnostic/.pioenvs/crowpanel-128-lvgl-diagnostic/firmware.factory.bin`.
A file left in `.esphome/` after a failed compile is stale. Stop rather than
flash it, guess offsets, or substitute another binary.

## Hold, identify and back up before writing

After approval for the installed slot (commands below assume SLOT1):

```bash
devcontainer exec --workspace-folder . tools/wb hold SLOT1 60 crowpanel-development
devcontainer exec --workspace-folder . tools/espwb-esptool flash-id
devcontainer exec --workspace-folder . tools/espwb-esptool read-flash 0x0 ALL artifacts/pre-flash.bin
```

Stop unless identity matches the intended ESP32-S3 CrowPanel with 16MB flash.
Backups contain secrets: keep them local and private. Keep the hold throughout
flashing and verification and release it on failure too.

Write the factory image matching the YAML that just compiled successfully:

```bash
devcontainer exec --workspace-folder . tools/espwb-esptool write-flash 0x0 esphome/.esphome/build/crowpanel/.pioenvs/crowpanel/firmware.factory.bin
```

The wrapper streams bytes on SSH stdin to `flash-esp SLOT1 write-flash 0x0`.
There are no remote shell paths. The server verifies identity, pauses only this
slot, applies kind-aware reset handling, and records flash history.

## Verify the application, then release

```bash
devcontainer exec --workspace-folder . tools/espwb-monitor 60
devcontainer exec --workspace-folder . tools/crowpanel-camera-capture artifacts/crowpanel-proof.jpg
devcontainer exec --workspace-folder . tools/crowpanel-camera-sequence 4 3
devcontainer exec --workspace-folder . tools/wb history 10
devcontainer exec --workspace-folder . tools/wb release SLOT1
```

Serial monitoring on native-USB ESP is opt-in at the server. Follow connections
never reset on exit. The old flash-id-after-monitor-close workaround is history
because monitor readers no longer own the serial port or alter modem lines.

A successful write is not application proof. Check a fresh boot marker, inspect
the photograph, and verify the charger UI, touch, rotary control, Wi-Fi and HA
connection. The diagnostic should show the display, touch label, rotary arc,
button and LEDs. Keep captures under ignored `artifacts/`, not public docs.

If blank or stuck, inspect status/history and the image used; do not reflexively
reset on monitor close. With approval, use slot-scoped USB reset or recompile
the known-good diagnostic. Never access host services or an admin shell.
