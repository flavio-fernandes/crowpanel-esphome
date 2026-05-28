# Next Codex prompt

Last reviewed: 2026-05-28.

Paste this into a fresh Codex thread when continuing the current CrowPanel work:

```text
Read AGENTS.md, README.md, docs/current-state.md, docs/roadmap.md,
docs/esphome-workbench-cheatsheet.md, docs/esphome-fresh-clone-flash-cheatsheet.md,
docs/github-setup.md, docs/public-release-checklist.md,
docs/ego-charger-timer-ui.md, and docs/ego-charger-production-test-matrix.md.

We are working in the CrowPanel ESPHome repo on the Elecrow CrowPanel 1.28 inch
HMI ESP32 rotary display in workbench SLOT1.

Current main firmware:
- esphome/crowpanel.yaml
- Purpose: Home Assistant EGO charger timer panel.

Important safety/workflow constraints:
- Follow AGENTS.md.
- Flash SLOT1 only.
- Flash only through tools/espwb-esptool.
- RFC2217 is monitor-only.
- Use tools/espwb-monitor for serial logs; it runs a reset-aware flash-id after
  monitor exit by default.
- Do not use RFC2217 for flashing or reset control.
- Do not run sudo.
- Do not print, copy, commit, or upload secrets.
- Do not push to GitHub or change repo visibility without explicit approval.

Current repo facts:
- flavio-fernandes/crowpanel-esphome was observed as public on 2026-05-28.
- flavio-fernandes/esp-codex-platform was observed as public on 2026-05-28.
- The local sibling esp-codex-platform checkout was not present next to this
  checkout during the 2026-05-28 review.

If changing firmware:
- Run esphome config and esphome compile for the changed YAML.
- Do not flash any firmware.factory.bin unless it was just compiled from the
  same YAML.
- Keep config/workbench.env, esphome/secrets.yaml, .esphome/, artifacts/, and
  generated firmware out of git.

If reviewing platform follow-up:
- The spin-off repo is flavio-fernandes/esp-codex-platform.
- Generic port candidates identified during the 2026-05-28 review were applied
  in platform commit 1c756d9; future candidates are listed in docs/roadmap.md.
- Do not include CrowPanel-specific YAML, Home Assistant helper packages,
  CrowPanel hardware notes, photos, local artifacts, generated firmware, or
  secrets in the platform repo.
```
