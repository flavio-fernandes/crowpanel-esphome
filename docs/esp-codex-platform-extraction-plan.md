# ESP Codex platform extraction plan

Goal: create a reusable, boring starter repo for future ESPHome and embedded
workbench projects, based on the workflow proven in this CrowPanel repo.

Proposed repo name: `esp-codex-platform`.

## Extraction principles

- Keep the platform generic: ESPHome + devcontainer + workbench workflow, not
  CrowPanel firmware.
- Preserve safety defaults: project-local tools, no `sudo`, no secrets, no
  generated firmware in git, and no flashing paths that bypass the reset-aware
  helper.
- Prefer templates and examples over clever generators for the first version.
- Leave project-specific hardware facts, camera captures, firmware backups,
  CrowPanel YAML, and Home Assistant UI details in this repo.

## Include

- `.devcontainer/` template for ESPHome, esptool, serial tooling, and VS Code.
- `AGENTS.md` template with safe/unsafe workspace operations.
- `README.md` template that explains the Mac -> SSH host -> devcontainer ->
  workbench -> ESP board workflow.
- `tools/espwb-ssh` pattern for workbench SSH without relying on global SSH
  config.
- `tools/espwb-esptool` pattern for reset-aware `chip-id`, `flash-id`,
  `read-flash`, and `write-flash` through `SLOT1`.
- `tools/validate-workbench.sh` pattern with RFC2217 open/close testing opt-in.
- Generic ESPHome examples:
  - `examples/generic-blink/generic-blink.yaml`
  - `examples/generic-heartbeat/generic-heartbeat.yaml`
- Documentation templates:
  - `docs/current-state.md`
  - `docs/roadmap.md`
  - `docs/project-sources.md`
  - `docs/github-setup.md`
  - `docs/workbench-cheatsheet.md`
  - `docs/reference/README.md`
- Ignore rules for `artifacts/`, `.esphome/`, firmware binaries, secrets, keys,
  and local environment files.

## Exclude

- CrowPanel pinouts, YAML examples, photos, camera captures, firmware backups,
  and hardware-specific notes.
- `secrets.yaml`, private keys, tokens, `.env` files, generated firmware, and
  build outputs.
- Home Assistant API/OTA/UI config. Add those later in device-specific repos.
- Hardcoded private workbench details beyond safe placeholders.

## Proposed layout

```text
esp-codex-platform/
  AGENTS.md
  README.md
  .devcontainer/
    Dockerfile
    devcontainer.json
  .gitattributes
  .gitignore
  .vscode/
    settings.json
  docs/
    current-state.md
    github-setup.md
    project-sources.md
    roadmap.md
    workbench-cheatsheet.md
    reference/
      README.md
  examples/
    generic-blink/
      .gitignore
      generic-blink.yaml
    generic-heartbeat/
      .gitignore
      generic-heartbeat.yaml
  tools/
    espwb-esptool
    espwb-ssh
    validate-workbench.sh
```

## First implementation pass

1. Create the repo directory outside this workspace only after explicit approval.
2. Copy reusable files from this repo.
3. Replace project-specific names, paths, IPs, slot warnings, and board examples
   with placeholders or generic defaults.
4. Keep `SLOT1` as the safe default in workbench tooling.
5. Run a no-secrets tracked-file review before the first commit.
6. Create a local initial commit.
7. Push or create GitHub only after explicit approval.

## Open choices before creating the repo

- Repo location: sibling checkout next to this project.
- GitHub visibility: private by default.
- Template style: plain starter repo first; Cookiecutter or Copier can come
  later if the plain version proves useful.
