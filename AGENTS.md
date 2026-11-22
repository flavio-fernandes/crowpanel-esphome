# Codex instructions for this workspace

Scope: this workspace only.

Safe things to do:

- Edit files in this workspace.
- Freely edit and run commands inside this repo.
- Add project-local scripts, docs, ESPHome YAML, and devcontainer files.
- Build or rebuild the devcontainer.
- Run validation scripts in `tools/`.
- Use `tools/espwb-esptool` for chip-id, flash-id, read-flash, and write-flash on `SLOT1`.
- Install small missing developer tools only after asking, limited to packages like `ripgrep`, `jq`, `tree`, `shellcheck`, `git`, `curl`, and `unzip`.

Do not do these without explicit user approval:

- Do not run `sudo`.
- Do not run `sudo` for Docker, SSH keys, systemd, Tailscale, firewall, `/usr/local/bin`, or bench service changes.
- Do not modify files outside this workspace.
- Do not modify SSH key directories.
- Do not print, copy, commit, or upload private keys, tokens, passwords, or `secrets.yaml`.
- Do not push to GitHub.
- Do not flash slots other than `SLOT1`.
- Do not create a large CrowPanel ESPHome YAML in one jump.

Important workflow rules:

- Use only restricted `ssh bench-agent <verb>` through the tools; no admin shell.
- Monitoring uses serial-follow and never resets on exit.
- Hardware needs explicit task approval. The CrowPanel is not currently installed;
  do not infer board identity from the default slot.
- Hold the approved slot for the entire job and release it in cleanup.
- Verify identity, back up unknown firmware, and compile the exact image before flashing.
- Local client checks use bench/dev/setup-venv.sh then bench/dev/check.sh; fake SSH only.
- The upstream esp-codex-platform bench/DESIGN.md defines the wire contract.
