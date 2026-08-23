from __future__ import annotations

import json
import os

from . import konsole

DATA_DIR = os.path.join(
    os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share")),
    "konsole-companion",
    "tabsets",
)


def _path(name: str) -> str:
    return os.path.join(DATA_DIR, name + ".json")


def list_sets() -> list[str]:
    if not os.path.isdir(DATA_DIR):
        return []
    return sorted(
        f[:-5] for f in os.listdir(DATA_DIR) if f.endswith(".json")
    )


def capture(window_id: str | None = None) -> list[dict]:
    k = konsole.current_konsole()
    if not k:
        return []
    if window_id is None:
        window_id = k.current_window()
    sids = k.window_session_ids(window_id) if window_id else k.session_ids()
    tabs = []
    for sid in sids:
        t = k.capture_tab(sid)
        tabs.append(
            {
                "profile": t.profile,
                "directory": t.directory,
                "name": t.name,
                "color": t.color,
            }
        )
    return tabs


def save(name: str, tabs: list[dict]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(_path(name), "w") as f:
        json.dump({"tabs": tabs}, f, indent=2)


def load(name: str) -> list[dict]:
    with open(_path(name)) as f:
        return json.load(f)["tabs"]


def delete(name: str) -> None:
    try:
        os.remove(_path(name))
    except OSError:
        pass


def rename(old: str, new: str) -> None:
    os.replace(_path(old), _path(new))


def restore(name: str, window_id: str | None = None) -> int:
    tabs = load(name)
    k = konsole.current_konsole()
    if not k or not tabs:
        return 0
    if window_id is None:
        window_id = k.current_window()
    if window_id is None:
        return 0
    created = 0
    for t in tabs:
        sid = k.new_session(
            window_id, t.get("profile") or "", t.get("directory") or ""
        )
        if t.get("name"):
            k.set_tab_title_format(sid, t["name"])
        if t.get("color"):
            k.set_tab_color(sid, t["color"])
        created += 1
    return created
