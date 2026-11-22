# ESPHome bench cheatsheet

The CrowPanel is not installed on the bench. These commands are for a future
approved installation, not permission to write whichever board is in SLOT1.
The wire contract is esp-codex-platform `bench/DESIGN.md`.

## Configure and inspect

```bash
cp config/bench.env.example config/bench.env
BENCH_STATIC_ONLY=1 tools/validate-bench.sh  # no network or hardware
tools/validate-bench.sh                    # help, status, health only
tools/wb status
tools/wb health --json
```

Configure the restricted SSH alias and verified host keys outside the repo.
Use `BENCH_AGENT`, `BENCH_SLOT` and optional SSH paths in ignored local config.
Never use an admin login or copy private keys. See [configuration](../config/README.md).

## Hold, identify, back up, compile, write

Only after approval and confirming the installed slot:

```bash
tools/wb hold SLOT1 60 crowpanel-development
tools/espwb-esptool flash-id
tools/espwb-esptool read-flash 0x0 ALL artifacts/pre-flash.bin
esphome config esphome/crowpanel.yaml
esphome compile esphome/crowpanel.yaml
tools/espwb-esptool write-flash 0x0 esphome/.esphome/build/crowpanel/.pioenvs/crowpanel/firmware.factory.bin
```

Stop on any failed step. Expect ESP32-S3 and 16MB flash for this CrowPanel;
identity must match before writing. Only use the merged factory image from
that successful compile. Backups contain secrets and must remain private.
Another slot needs explicit approval, `BENCH_ALLOW_NON_SLOT1=1` and matching
`BENCH_SLOT`; explicit slots passed to `wb` are not changed by those settings.

## Verify and release

```bash
tools/espwb-monitor 60
tools/wb serial-tail SLOT1 50
tools/crowpanel-camera-capture artifacts/crowpanel-proof.jpg
tools/crowpanel-camera-sequence 4 3
tools/wb history 10
tools/wb release SLOT1
```

Use a fresh firmware marker and inspect the actual photo. Keep the hold until
verification is finished; release it in cleanup even if a step fails.
Native-USB ESP serial ownership is opt-in on the server, so an empty monitor
is not proof of a bad application. The monitor follows for 300 seconds by
default (maximum 600), and exiting it never resets the device.

The historical flash-id-after-monitor-close advice is retired because reader
connections no longer own the serial port or toggle its modem lines.
[Old transport evidence](history/esphome-workbench-cheatsheet.md) is history only.

## Camera behavior

Capture prints a JPEG path; sequence prints one path per frame, retaining the
CrowPanel timestamped directory and `frame-01.jpg` naming. Defaults are four
frames with three seconds between captures, with no sleep after the last.
Optional `BENCH_CAMERA_WIDTH`, `HEIGHT`, `SKIP`, and `EXPOSURE` override server
settings. Old `CROWPANEL_CAMERA_*` names warn; local camera device selection is
retired because only the server owns the camera.

## Recovery and errors

SSH failure 255 means OFF; health exit 1 means DEGRADED. Tool status codes are
preserved: 2 usage, 65 busy, 66 absent, 68 flash failure, 69 held, 70 wrong kind,
71 application did not return. Diagnose before retrying; don't stop other slots.
Use `tools/wb usb-reset SLOT1` only with approval and a hold. Native-USB ESP does
not support the UART-only `reset` verb. Check history, logs and the actual image
before rebuilding a known-good diagnostic. Never use arbitrary remote shell commands.
