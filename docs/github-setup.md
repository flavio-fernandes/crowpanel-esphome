# GitHub setup

Last reviewed: 2026-05-28.

## Current repositories

- CrowPanel repo: `flavio-fernandes/crowpanel-esphome`
- Remote: `origin`
- Local branch: `main`
- Remote branch: `origin/main`
- Visibility observed through the GitHub connector on 2026-05-28: public.

Related spin-off:

- Platform starter repo: `flavio-fernandes/esp-codex-platform`
- Visibility observed through the GitHub connector on 2026-05-28: public.
- Initial commit: `57c98ed Create ESP Codex platform starter`
- Latest published platform refresh observed locally:
  `1c756d9 Refresh ESP platform starter workflow`

Older notes in this repo describe the CrowPanel repo as private because it was
created privately first. Treat the current public visibility as intentional only
after running the public hygiene checks in `docs/public-release-checklist.md`.

## Original setup

The original CrowPanel GitHub repo was created from a normal shell with:

```bash
gh repo create crowpanel-esphome --private --source . --remote origin --push
```

The repository was later observed as public. Do not change repository
visibility from Codex without explicit approval.

## Pre-push safety checks

Before pushing, verify the tracked file set and ignored build outputs:

```bash
git status --short
git log --oneline --decorate -5
git remote -v
git ls-files
git status --ignored --short
git diff --check
```

Do not push if any of these are tracked:

- `secrets.yaml`
- `.env` or `.env.*`
- private keys
- tokens or passwords
- firmware binaries such as `*.bin`, `*.elf`, `*.uf2`, `*.factory.bin`, or
  `*.ota.bin`
- `artifacts/`
- `.esphome/`
- local workbench config such as `config/workbench.env`

## Codex auth note

Earlier Codex sessions saw `gh` installed but reported an invalid GitHub CLI
token while the normal shell was usable. If Codex needs GitHub CLI operations,
verify authentication in Codex's own command environment first:

```bash
gh auth status
git remote -v
```

Do not start browser auth, change GitHub authentication, push, or change
repository visibility from Codex without explicit approval.

## Safety reminders

- Keep secrets, private keys, local env files, generated firmware, `artifacts/`,
  and `.esphome/` out of git.
- Do not push to GitHub without explicit user approval.
- Do not flash from GitHub setup steps.
