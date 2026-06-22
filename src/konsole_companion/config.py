from __future__ import annotations

import json
import os

CONFIG_DIR = os.path.join(
    os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),
    "konsole-companion",
)
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULTS = {
    "pairs": [],
}


def load() -> dict:
    try:
        with open(CONFIG_FILE) as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        data = {}
    merged = dict(DEFAULTS)
    merged.update(data)
    return merged


def save(data: dict) -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)


def target_profile(current: str, is_dark: bool, pairs: list[dict]) -> str | None:
    for pair in pairs:
        if current in (pair.get("light"), pair.get("dark")):
            return pair["dark"] if is_dark else pair["light"]
    return None
