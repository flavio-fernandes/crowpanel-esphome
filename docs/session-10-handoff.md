# Session 10 handoff

Status: historical archive. Reviewed 2026-05-28.

This file used to contain the early Step 10 handoff for creating the
CrowPanel ESPHome devcontainer and workbench wrappers. Those tasks are now
complete, and the project has moved on to the Home Assistant EGO charger panel
in `esphome/crowpanel.yaml`.

Use these current docs instead:

- Current state: `docs/current-state.md`
- Roadmap: `docs/roadmap.md`
- Fresh clone and flash workflow:
  `docs/esphome-fresh-clone-flash-cheatsheet.md`
- Short workbench reference: `docs/esphome-workbench-cheatsheet.md`
- GitHub and public hygiene: `docs/github-setup.md` and
  `docs/public-release-checklist.md`

Historical facts worth keeping:

- The architecture was established as:

```text
Mac -> VS Code SSH -> Linux host -> devcontainer -> workbench -> SLOT1 board
```

- RFC2217 was reserved for serial monitoring only.
- Flashing was routed through `/usr/local/bin/espwb-local-esptool` on the
  workbench via `tools/espwb-esptool`.
- The first validated SLOT1 smoke target was a Feather/HUZZAH32 ESP32 blink
  example before the CrowPanel was installed.
- The no-secrets, no-`sudo`, no-non-SLOT1, no-unapproved-push guardrails from
  that session still apply through `AGENTS.md`.
