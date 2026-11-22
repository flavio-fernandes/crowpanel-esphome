"""The devcontainer must not set bench connection settings (PR #2 review, 2026-11-22).

tools/lib/workbench-env gives environment values precedence over config/bench.env, so a
containerEnv default would silently override the user's local configuration.
"""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


def test_devcontainer_leaves_bench_settings_to_config_file():
    text = (ROOT / ".devcontainer/devcontainer.json").read_text()
    data = json.loads(re.sub(r"^\s*//.*$", "", text, flags=re.M))
    env = data.get("containerEnv", {})
    leaked = sorted(k for k in env if k.startswith(("BENCH_", "WORKBENCH_", "ESPWB_")))
    assert leaked == [], f"containerEnv overrides config/bench.env: {leaked}"
