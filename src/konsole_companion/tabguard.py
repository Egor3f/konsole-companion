from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, QTimer

from . import konsole

IDLE_MS = 5000
REAPPLY_RETRY_MS = 800
EMPTY_DROP_TICKS = 2


@dataclass
class _Entry:
    name: str | None = None
    color: str | None = None
    name_empty: int = 0
    color_empty: int = 0


class TabGuard(QObject):
    def __init__(self, watcher, parent=None):
        super().__init__(parent)
        self._cache: dict[tuple[str, str], _Entry] = {}
        watcher.changed.connect(self._on_theme_change)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(IDLE_MS)

    def _on_theme_change(self) -> None:
        self._reapply()
        QTimer.singleShot(REAPPLY_RETRY_MS, self._reapply)

    def _reapply(self) -> None:
        for service, sid, k in self._sessions():
            entry = self._cache.get((service, sid))
            if not entry:
                continue
            try:
                if entry.name and k.custom_name(sid) != entry.name:
                    k.set_tab_title_format(sid, entry.name)
                if entry.color and k.tab_color(sid) != entry.color:
                    k.set_tab_color(sid, entry.color)
            except konsole.KonsoleError:
                continue

    def _refresh(self) -> None:
        live: set[tuple[str, str]] = set()
        for service, sid, k in self._sessions():
            key = (service, sid)
            live.add(key)
            entry = self._cache.setdefault(key, _Entry())
            try:
                self._track(k, sid, entry)
            except konsole.KonsoleError:
                continue
        for key in list(self._cache):
            if key not in live:
                del self._cache[key]

    def _track(self, k, sid, entry):
        name = k.custom_name(sid)
        if name:
            entry.name = name
            entry.name_empty = 0
        else:
            entry.name_empty += 1
            if entry.name_empty >= EMPTY_DROP_TICKS:
                entry.name = None

        color = k.tab_color(sid)
        if color:
            entry.color = color
            entry.color_empty = 0
        else:
            entry.color_empty += 1
            if entry.color_empty >= EMPTY_DROP_TICKS:
                entry.color = None

    def _sessions(self):
        for service in konsole.konsole_services():
            k = konsole.Konsole(service)
            try:
                sids = k.session_ids()
            except konsole.KonsoleError:
                continue
            for sid in sids:
                yield service, sid, k
