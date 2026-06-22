from __future__ import annotations

from . import config, konsole


def apply_theme(is_dark: bool) -> int:
    pairs = config.load()["pairs"]
    if not pairs:
        return 0
    switched = 0
    for service in konsole.konsole_services():
        k = konsole.Konsole(service)
        # setProfile silently no-ops on an unknown profile name, so guard against
        # pairs referencing profiles this Konsole has not loaded.
        known = set(k.profile_list())
        for sid in k.session_ids():
            current = k.profile(sid)
            target = config.target_profile(current, is_dark, pairs)
            if target and target != current and target in known:
                k.set_profile(sid, target)
                switched += 1
    return switched
