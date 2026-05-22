# Examples

The ESPHome examples in this directory are intended to be compiled from the
repo root inside the devcontainer.

Start here for a full fresh-clone to flashed-device workflow:

- `../docs/esphome-fresh-clone-flash-cheatsheet.md`

Short reference:

- `../docs/esphome-workbench-cheatsheet.md`

Current CrowPanel LVGL diagnostic target:

```bash
devcontainer exec --workspace-folder . esphome config examples/crowpanel-128-lvgl-diagnostic/crowpanel-128-lvgl-diagnostic.yaml
devcontainer exec --workspace-folder . esphome compile examples/crowpanel-128-lvgl-diagnostic/crowpanel-128-lvgl-diagnostic.yaml
devcontainer exec --workspace-folder . tools/espwb-esptool write-flash 0x0 examples/crowpanel-128-lvgl-diagnostic/.esphome/build/crowpanel-128-lvgl-diagnostic/.pioenvs/crowpanel-128-lvgl-diagnostic/firmware.factory.bin
```

Flashing must go through `tools/espwb-esptool` and the default workbench slot is
`SLOT1`.

Do not flash a `firmware.factory.bin` from `.esphome/` unless you just compiled
the matching YAML successfully. Build outputs are ignored generated state and
can be stale after display-driver experiments.

The `crowpanel-128-display-test` example is a focused native display smoke test.
It must enable GPIO40 plus the GPIO1/GPIO2 output rails before drawing; use the
LVGL diagnostic for the documented end-to-end CrowPanel flash path.
