# GitHub setup later

Do this only after Step 10C passes and the first commit is reviewed.

Suggested future flow:

```bash
cd ~/src/crowpanel-esphome

git status --short
git diff --check
git add AGENTS.md README.md .devcontainer tools docs esphome .gitignore .gitattributes .vscode/settings.json
git commit -m "Add CrowPanel ESPHome devcontainer workspace"

gh repo create crowpanel-esphome --private --source . --remote origin --push
```

Before pushing, verify that these do not appear in `git status`:

- `secrets.yaml`
- `.env`
- private keys
- firmware binaries
- `artifacts/`
- `.esphome/`
