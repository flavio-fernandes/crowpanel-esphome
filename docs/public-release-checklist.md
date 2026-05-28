# Public hygiene checklist

Last reviewed: 2026-05-28.

The CrowPanel GitHub repo was observed as public through the GitHub connector on
2026-05-28. Run this checklist before any push, public release, visibility
change, or large documentation update.

```bash
git status --short
git status --ignored --short
git ls-files
git diff --check
git grep -n -E '<private-lan-regex>|<secret-regex>'
rg -n '<private-lan-regex>|<secret-regex>'
```

Confirm that tracked files do not include:

- `config/workbench.env`
- `esphome/secrets.yaml`
- `.env` or `.env.*`
- private keys, tokens, passwords, or certificates
- generated firmware such as `*.bin`, `*.elf`, `*.factory.bin`, or `*.ota.bin`
- generated ESPHome or PlatformIO build directories
- local captures under `artifacts/`
- private LAN IPs, device MACs, usernames, hostnames, or Tailscale names

Local setup values belong in ignored files such as `config/workbench.env`.
Committed docs should use placeholders like `192.0.2.10`.
