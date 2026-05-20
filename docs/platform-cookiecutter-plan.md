# Platform cookiecutter plan

Long-term goal: turn the CrowPanel workspace pattern into a reusable, boringly repeatable platform for future ESPHome and embedded workbench projects.

## Argon bootstrap

- Verify OS, architecture, Docker Engine, Docker Compose, and devcontainer CLI.
- Confirm the user can run Docker without `sudo`.
- Install only the small developer tools needed for local workflow, after approval.
- Create a standard workspace layout under the user's source directory.
- Capture baseline logs under project-local `artifacts/`.
- Document network facts, SSH access, and any host-specific assumptions.

## Workbench bootstrap

- Verify workbench API reachability from the Linux host.
- Verify SSH access to the workbench without exposing private keys.
- Verify `/usr/local/bin/espwb-local-esptool` exists and is executable.
- Confirm slot inventory and default the project to `SLOT1`.
- Keep RFC2217 reserved for serial monitoring only.
- Route chip-id, flash-id, read-flash, write-flash, and firmware flashing through the reset-aware local helper.

## ESP project template

- Provide a minimal `.devcontainer/` with ESPHome, esptool, serial tooling, and editor extensions.
- Include project-local wrappers in `tools/` for workbench SSH and esptool operations.
- Start ESPHome YAML as a small skeleton and add board features incrementally.
- Include a clear secrets strategy using committed examples and ignored real secrets.
- Add static validation scripts before adding hardware-specific complexity.
- Keep generated files, firmware binaries, cache directories, and local artifacts out of git.

## Project sources and reference capture

- Keep `docs/project-sources.md` as the index of upstream references.
- Store small reference snapshots under `docs/reference/` when they explain local wrapper or template choices.
- Record session handoffs with validated facts, current risks, and the next planned step.
- Prefer primary sources for hardware pinouts, display behavior, touch, rotary encoder, and ESPHome component details.

## GitHub setup flow

- Keep the repo local until the devcontainer build and validation pass.
- Review `git status --short`, `git diff --check`, and ignored secret/build-output behavior before the first commit.
- Create the first commit only after the Step 10C review.
- Push to GitHub only after explicit user approval.
- Use a private repo by default unless the user chooses otherwise.
