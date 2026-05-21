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

`esphome/secrets.yaml` is ignored by git. The current
`examples/crowpanel-128-lvgl-diagnostic/crowpanel-128-lvgl-diagnostic.yaml`
does not require these secrets, but keeping the file populated avoids surprises
when compiling examples that do use Wi-Fi, API, or OTA.

## 4. Build or open the devcontainer

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

## 5. Compile the CrowPanel LVGL diagnostic YAML

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

## 6. Check the board identity before flashing

```bash
devcontainer exec --workspace-folder . tools/espwb-esptool flash-id
```

For the current safe workbench target, expect `SLOT1` and an ESP32-class chip.
Older validation notes recorded an ESP32-D0WDQ6 with 4MB flash for the Feather
test board; the CrowPanel LVGL target is ESP32-S3 with 16MB flash. If the slot or
chip does not match the device you intend to flash, stop.

## 7. Flash the CrowPanel through the reset-aware helper

```bash
devcontainer exec --workspace-folder . tools/espwb-esptool write-flash 0x0 examples/crowpanel-128-lvgl-diagnostic/.esphome/build/crowpanel-128-lvgl-diagnostic/.pioenvs/crowpanel-128-lvgl-diagnostic/firmware.factory.bin
```

This command SSHs to the workbench and runs:

```text
/usr/local/bin/espwb-local-esptool SLOT1 write-flash 0x0 firmware.factory.bin
```

It intentionally does not flash over RFC2217 and does not use RFC2217 reset
control.

## 8. Quick post-flash check

Run another reset-aware identity check:

```bash
devcontainer exec --workspace-folder . tools/espwb-esptool flash-id
```

The diagnostic should bring up the round display, touch label, rotary arc, knob
button handling, backlight, output enables, power light, and blue ambient LEDs.

## Safety reminders

- Flash only `SLOT1` unless you explicitly decide otherwise.
- Use `tools/espwb-esptool` for `chip-id`, `flash-id`, `read-flash`,
  `write-flash`, and firmware flashing.
- Use RFC2217 only for serial monitoring.
- Keep `config/workbench.env` and `esphome/secrets.yaml` out of git.
- Do not run `sudo` or change workbench system services from this workflow.
