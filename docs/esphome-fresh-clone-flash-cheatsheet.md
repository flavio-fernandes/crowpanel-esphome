# Fresh clone to flashed CrowPanel firmware

This complements `docs/esphome-workbench-cheatsheet.md` with the full path from
a new checkout to firmware written to the CrowPanel in workbench `SLOT1`.

Architecture:

```text
Mac -> VS Code SSH -> Argon/Linux host -> devcontainer -> workbench -> SLOT1 CrowPanel
```

Related setup notes:

- Workbench/devcontainer setup summary: `docs/session-10-handoff.md`
- Argon and reusable platform provisioning notes: `docs/platform-cookiecutter-plan.md`
- Short command reference: `docs/esphome-workbench-cheatsheet.md`
- Local config file rules: `config/README.md`
- CrowPanel ESPHome configs: `esphome/README.md`
- Home Assistant helper package: `config/home-assistant/ego-charger-helpers.yaml`

## 1. Clone the repo on Argon

```bash
mkdir -p ~/src
cd ~/src
git clone https://github.com/flavio-fernandes/crowpanel-esphome.git
cd crowpanel-esphome
```

Keep the checkout directory named `crowpanel-esphome`. The current
`.devcontainer/devcontainer.json` uses `/workspaces/crowpanel-esphome` as its
workspace folder, so cloning into a differently named directory can make
relative commands like `tools/validate-workbench.sh` miss the repo root.

If you already have the checkout, update it instead of cloning another copy:

```bash
cd ~/src/crowpanel-esphome
git status --short
git pull --ff-only
```

## 2. Create local workbench env

```bash
cp config/workbench.env.example config/workbench.env
$EDITOR config/workbench.env
```

Fill in the real workbench values for the Argon network. A typical local file
looks like this, with the IP adjusted for your workbench:

```bash
WORKBENCH_IP=192.0.2.10
WORKBENCH_USER=pi
ESPWB_SLOT=SLOT1
ALLOW_NON_SLOT1=0
HOST_SSH_DIR=/host-ssh
SSH_CONFIG=/dev/null
WORKBENCH_URL=http://${WORKBENCH_IP}:8080
ESP_PORT=rfc2217://${WORKBENCH_IP}:4001?ign_set_control
RUN_RFC2217_TEST=0
```

If the devcontainer cannot use the `/host-ssh` mount, add this to
`config/workbench.env` with the real key path available inside the container:

```bash
ESPWB_SSH_KEY=/host-ssh/id_rsa
```

Do not print, commit, or copy SSH private key contents. The project wrappers
copy the key to a temporary local file and clean it up.

## 3. Create local ESPHome secrets

```bash
cp esphome/secrets.yaml.example esphome/secrets.yaml
$EDITOR esphome/secrets.yaml
```

Use real local values:

```yaml
wifi_ssid: "your-wifi"
wifi_password: "your-password"
api_encryption_key: "your-api-key"
ota_password: "your-ota-password"
```

`esphome/secrets.yaml` is ignored by git. `esphome/crowpanel.yaml` requires all
four values because it uses Wi-Fi, encrypted Home Assistant API, and OTA.

Generate a new ESPHome API encryption key from an existing ESPHome environment
or the ESPHome dashboard, then paste only the key value into the local secrets
file. Do not reuse a public example value.

The CrowPanel diagnostic examples may not require these secrets, but keeping
the file populated avoids surprises when switching between examples and
`esphome/crowpanel.yaml`.

## 4. Prepare Home Assistant helpers for `crowpanel.yaml`

`esphome/crowpanel.yaml` is an EGO charger timer panel. By default it imports
these Home Assistant entities:

```text
switch.ego_charger
sensor.ego_charger_power
input_number.ego_charger_preset_duration_minutes
input_datetime.ego_charger_timer_end_time
input_boolean.ego_charger_timer_active
input_boolean.ego_charger_panel_pending_off
```

Install or include `config/home-assistant/ego-charger-helpers.yaml` as a Home
Assistant package to create the helper entities. You still need a real
`switch.ego_charger` and `sensor.ego_charger_power`, or you need to edit the
substitutions at the top of `esphome/crowpanel.yaml` to match your local entity
IDs before compiling.

After the device is added to Home Assistant, allow the ESPHome integration for
this device to make Home Assistant service calls. The panel uses explicit
`switch.turn_on` and `switch.turn_off` calls for the charger switch.

## 5. Build or open the devcontainer

From the repo root on Argon:

```bash
devcontainer up --workspace-folder .
```

If `.devcontainer/Dockerfile` or `.devcontainer/devcontainer.json` changed,
rebuild the image and replace the running container:

```bash
devcontainer up --workspace-folder . --remove-existing-container
```

Run commands through the devcontainer:

```bash
devcontainer exec --workspace-folder . esphome version
devcontainer exec --workspace-folder . rg --version
devcontainer exec --workspace-folder . python3 -m esptool version
devcontainer exec --workspace-folder . tools/validate-workbench.sh
```

`tools/validate-workbench.sh` checks the local toolchain, workbench API, SSH to
the workbench, the reset-aware helper, and `SLOT1` flash identity. It skips the
RFC2217 open/close monitor test by default because RFC2217 is for monitoring
only and can perturb the CrowPanel USB-serial path.

## 6. Compile firmware

### Option A: compile the production charger panel

Use this path for `esphome/crowpanel.yaml`:

```bash
devcontainer exec --workspace-folder . esphome config esphome/crowpanel.yaml
devcontainer exec --workspace-folder . esphome compile esphome/crowpanel.yaml
```

The expected factory firmware path is:

```text
esphome/.esphome/build/crowpanel/.pioenvs/crowpanel/firmware.factory.bin
```

If that file is missing, stop and fix the compile. Do not guess offsets or flash
another binary.

If that file exists from an earlier run but the compile you just ran did not
finish successfully, treat the file as stale and do not flash it. The ignored
`.esphome/` directory is a cache/build output directory, not source of truth.

### Option B: compile the known-good LVGL diagnostic

```bash
devcontainer exec --workspace-folder . esphome config examples/crowpanel-128-lvgl-diagnostic/crowpanel-128-lvgl-diagnostic.yaml
devcontainer exec --workspace-folder . esphome compile examples/crowpanel-128-lvgl-diagnostic/crowpanel-128-lvgl-diagnostic.yaml
```

The expected factory firmware path is:

```text
examples/crowpanel-128-lvgl-diagnostic/.esphome/build/crowpanel-128-lvgl-diagnostic/.pioenvs/crowpanel-128-lvgl-diagnostic/firmware.factory.bin
```

If that file is missing, stop and fix the compile. Do not guess offsets or flash
another binary.

If that file exists from an earlier run but the compile you just ran did not
finish successfully, treat the file as stale and do not flash it. The ignored
`.esphome/` directory is a cache/build output directory, not source of truth.

## 7. Check the board identity before flashing

```bash
devcontainer exec --workspace-folder . tools/espwb-esptool flash-id
```

For the current safe workbench target, expect `SLOT1` and an ESP32-class chip.
Older validation notes recorded an ESP32-D0WDQ6 with 4MB flash for the Feather
test board; the CrowPanel LVGL target is ESP32-S3 with 16MB flash. If the slot or
chip does not match the device you intend to flash, stop.

## 8. Flash the CrowPanel through the reset-aware helper

Use the command matching the YAML you just compiled.

For `esphome/crowpanel.yaml`:

```bash
devcontainer exec --workspace-folder . tools/espwb-esptool write-flash 0x0 esphome/.esphome/build/crowpanel/.pioenvs/crowpanel/firmware.factory.bin
```

For the LVGL diagnostic:

```bash
devcontainer exec --workspace-folder . tools/espwb-esptool write-flash 0x0 examples/crowpanel-128-lvgl-diagnostic/.esphome/build/crowpanel-128-lvgl-diagnostic/.pioenvs/crowpanel-128-lvgl-diagnostic/firmware.factory.bin
```

This command SSHs to the workbench and runs:

```text
/usr/local/bin/espwb-local-esptool SLOT1 write-flash 0x0 firmware.factory.bin
```

It intentionally does not flash over RFC2217 and does not use RFC2217 reset
control.

## 9. Quick post-flash check

Run another reset-aware identity check:

```bash
devcontainer exec --workspace-folder . tools/espwb-esptool flash-id
```

For `esphome/crowpanel.yaml`, the panel should boot into the EGO charger timer
UI, connect to Wi-Fi, and connect to Home Assistant. If HA helpers are present
and the ESPHome integration is allowed to call HA services, the touch target,
knob button, and rotary ring should control the configured charger timer flow.

The diagnostic should bring up the round display, touch label, rotary arc, knob
button handling, backlight, output enables, power light, and blue ambient LEDs.

## 10. Monitor DUT logs

Use the project monitor wrapper to watch raw DUT serial logs through RFC2217:

```bash
devcontainer exec --workspace-folder . tools/espwb-monitor
```

The wrapper reads `config/workbench.env`, uses `${ESP_PORT}`, and does not use
RFC2217 for flashing. Press `Ctrl-C` to exit the monitor.

Closing an RFC2217 monitor session can leave the CrowPanel display visually
blank or frozen. To make the common path safer, `tools/espwb-monitor` runs this
reset-aware recovery check automatically after the monitor exits:

```bash
tools/espwb-esptool flash-id
```

Set `ESPWB_MONITOR_RECOVER=0` only when intentionally debugging the RFC2217
close behavior and you do not want that automatic check.

## 11. Capture a physical verification photo

Use the workbench camera to verify the display after flashing:

```bash
tools/crowpanel-camera-capture
```

Captures normally go under ignored `artifacts/`. To replace the README image
with a fresh in-use shot, capture directly to the committed docs image path:

```bash
tools/crowpanel-camera-capture docs/images/crowpanel-ego-charger-in-use.jpg
```

## 12. Recover a blank or stuck DUT

If the CrowPanel display is blank after a flash, first run a reset-aware
identity check. This can recover a blank/frozen state caused by closing an
RFC2217 serial monitor:

```bash
devcontainer exec --workspace-folder . tools/espwb-esptool flash-id
```

If the display is still blank, treat the flashed app as suspect. Rebuild and
flash the known-good LVGL diagnostic through the reset-aware helper:

```bash
devcontainer exec --workspace-folder . esphome config examples/crowpanel-128-lvgl-diagnostic/crowpanel-128-lvgl-diagnostic.yaml
devcontainer exec --workspace-folder . esphome compile examples/crowpanel-128-lvgl-diagnostic/crowpanel-128-lvgl-diagnostic.yaml
devcontainer exec --workspace-folder . tools/espwb-esptool write-flash 0x0 examples/crowpanel-128-lvgl-diagnostic/.esphome/build/crowpanel-128-lvgl-diagnostic/.pioenvs/crowpanel-128-lvgl-diagnostic/firmware.factory.bin
```

Confirm recovery with the workbench camera:

```bash
tools/crowpanel-camera-capture
```

## Safety reminders

- Flash only `SLOT1` unless you explicitly decide otherwise.
- Use `tools/espwb-esptool` for `chip-id`, `flash-id`, `read-flash`,
  `write-flash`, and firmware flashing.
- Use RFC2217 only for serial monitoring.
- Keep `config/workbench.env` and `esphome/secrets.yaml` out of git.
- Do not run `sudo` or change workbench system services from this workflow.
