# GitHub setup

Step 10D1 was completed manually from the argon shell after the validated local commits were reviewed.

## Final repository

- Repository: `flavio-fernandes/crowpanel-esphome`
- Visibility: private
- Remote: `https://github.com/flavio-fernandes/crowpanel-esphome.git`
- Local branch: `main`
- Remote branch: `origin/main`

Current pushed commits:

```text
271bd8f Add known-good ESPHome workbench blink example
a4f612e Add CrowPanel ESPHome devcontainer foundation
```

## Working setup

The working command used from the argon shell was:

```bash
gh repo create crowpanel-esphome --private --source . --remote origin --push
```

The resulting remote is:

```bash
origin  https://github.com/flavio-fernandes/crowpanel-esphome.git (fetch)
origin  https://github.com/flavio-fernandes/crowpanel-esphome.git (push)
```

## Pre-push safety checks

Before pushing, verify the tracked file set and ignored build outputs:

```bash
git status --short
git log --oneline --decorate -5
git remote -v
git ls-files
git status --ignored --short
```

Do not push if any of these are tracked:

- `secrets.yaml`
- `.env` or `.env.*`
- private keys
- firmware binaries such as `*.bin`, `*.elf`, `*.uf2`, `*.factory.bin`, or `*.ota.bin`
- `artifacts/`
- `.esphome/`

Expected ignored generated paths after the blink example build:

```text
artifacts/
examples/feather-huzzah32-blink/.esphome/
```

## Codex auth mismatch note

Codex saw `gh` installed, but `gh auth status` reported an invalid token in `/home/ff/.config/gh/hosts.yml` for `flavio-fernandes`.

Codex initially saw an invalid `gh` token before the normal argon shell re-authenticated `gh`. After re-authentication, Codex should verify `gh auth status` in its own command environment before attempting GitHub operations.

Manual GitHub setup from the argon shell succeeded anyway, which means the interactive shell environment and the Codex command environment did not agree about usable GitHub authentication at that time. If future Codex-driven GitHub commands fail while manual shell commands work, re-check:

```bash
gh auth status
git remote -v
```

Do not start browser auth or change GitHub authentication from Codex without explicit approval.

## Safety reminders

- Keep the repository private unless explicitly changed by the user.
- Do not push secrets, private keys, `.env` files, generated firmware, `artifacts/`, or `.esphome/`.
- Do not push to GitHub without explicit user approval.
- Do not create CrowPanel YAML in one large jump.
- Do not flash from GitHub setup steps.
