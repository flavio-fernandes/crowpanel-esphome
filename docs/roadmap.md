# Roadmap

## Bench migration

Client tools now use restricted `bench-agent` SSH verbs from esp-codex-platform
W11. No host shell, key copying, network serial service, or monitor-exit reset
is needed. CrowPanel camera commands retain JPEG paths and timed sequences.
Configuration uses `BENCH_*`; supported old names warn for one release.

This is a code-only migration. The CrowPanel is not installed on the bench;
no new firmware, display, Wi-Fi, or Home Assistant validation is claimed.
Previous milestones are preserved in [history](history/roadmap.md).

## Remaining CrowPanel work

- Commission the CrowPanel on an explicitly approved slot before hardware use.
- Check identity, hold the slot, and back up unknown firmware before flashing.
- Run ESPHome config and compile after firmware changes; never flash stale output.
- Run [the production test matrix](ego-charger-production-test-matrix.md) after
  charger logic, Home Assistant entity, or UI changes.
- Keep local charger switch and power sensor substitutions aligned with HA;
  allow the ESPHome integration to perform HA actions.
- Keep generated firmware, photos, secrets and local configuration out of git.

## Guides

- [Fresh clone to flash](esphome-fresh-clone-flash-cheatsheet.md)
- [Bench commands](esphome-bench-cheatsheet.md)
- [Current state](current-state.md)

Device-specific YAML, camera presentation, UI docs, and HA packages stay here;
the reusable transport and server design belong to esp-codex-platform.
