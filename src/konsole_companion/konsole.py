from __future__ import annotations

import os
from dataclasses import dataclass
from xml.etree import ElementTree

from PySide6.QtDBus import QDBusConnection, QDBusInterface, QDBusMessage

SERVICE_PREFIX = "org.kde.konsole"
SESSION_IFACE = "org.kde.konsole.Session"
WINDOW_IFACE = "org.kde.konsole.Window"
INTROSPECT_IFACE = "org.freedesktop.DBus.Introspectable"


class KonsoleError(RuntimeError):
    pass


@dataclass
class Tab:
    profile: str
    directory: str
    name: str | None
    color: str | None


def _bus() -> QDBusConnection:
    return QDBusConnection.sessionBus()


def konsole_services() -> list[str]:
    reply = _bus().interface().registeredServiceNames()
    names = reply.value()
    return [
        n for n in names
        if n == SERVICE_PREFIX or n.startswith(SERVICE_PREFIX + "-")
    ]


def _call(service: str, path: str, interface: str, method: str, *args):
    iface = QDBusInterface(service, path, interface, _bus())
    if not iface.isValid():
        raise KonsoleError(f"invalid interface {interface} at {service}{path}")
    msg = iface.call(method, *args)
    if msg.type() == QDBusMessage.MessageType.ErrorMessage:
        raise KonsoleError(msg.errorMessage())
    return msg.arguments()


def _children(service: str, path: str) -> list[str]:
    xml = _call(service, path, INTROSPECT_IFACE, "Introspect")[0]
    root = ElementTree.fromstring(xml)
    return [n.get("name") for n in root.findall("node") if n.get("name")]


class Konsole:
    def __init__(self, service: str):
        self.service = service

    def window_ids(self) -> list[str]:
        return _children(self.service, "/Windows")

    def session_ids(self) -> list[str]:
        return _children(self.service, "/Sessions")

    def current_window(self) -> str | None:
        ids = self.window_ids()
        return ids[0] if ids else None

    def profile_list(self) -> list[str]:
        window = self.current_window()
        if window is None:
            return []
        return list(
            _call(self.service, f"/Windows/{window}", WINDOW_IFACE, "profileList")[0]
        )

    def window_session_ids(self, window_id: str) -> list[str]:
        ids = _call(
            self.service, f"/Windows/{window_id}", WINDOW_IFACE, "sessionList"
        )[0]
        return [str(i) for i in ids]

    def new_session(
        self, window_id: str, profile: str = "", directory: str = ""
    ) -> str:
        path = f"/Windows/{window_id}"
        if profile and directory:
            args = _call(self.service, path, WINDOW_IFACE, "newSession", profile, directory)
        elif profile:
            args = _call(self.service, path, WINDOW_IFACE, "newSession", profile)
        else:
            args = _call(self.service, path, WINDOW_IFACE, "newSession")
        return str(args[0])

    def _session_call(self, sid: str, method: str, *args):
        return _call(self.service, f"/Sessions/{sid}", SESSION_IFACE, method, *args)

    def profile(self, sid: str) -> str:
        return self._session_call(sid, "profile")[0]

    def set_profile(self, sid: str, name: str) -> None:
        self._session_call(sid, "setProfile", name)

    def process_id(self, sid: str) -> int:
        return int(self._session_call(sid, "processId")[0])

    def tab_title_format(self, sid: str) -> str:
        return self._session_call(sid, "tabTitleFormat", 0)[0]

    def set_tab_title_format(self, sid: str, fmt: str) -> None:
        self._session_call(sid, "setTabTitleFormat", 0, fmt)

    def cwd(self, sid: str) -> str | None:
        try:
            return os.readlink(f"/proc/{self.process_id(sid)}/cwd")
        except (OSError, KonsoleError):
            return None

    def custom_name(self, sid: str) -> str | None:
        fmt = self.tab_title_format(sid)
        if fmt and "%" not in fmt:
            return fmt
        return None

    def tab_color(self, sid: str) -> str | None:
        color = self._session_call(sid, "tabColor")[0]
        if not color or color == "#000000":
            return None
        return color

    def set_tab_color(self, sid: str, color: str) -> None:
        self._session_call(sid, "setTabColor", color)

    def capture_tab(self, sid: str) -> Tab:
        return Tab(
            profile=self.profile(sid),
            directory=self.cwd(sid) or "",
            name=self.custom_name(sid),
            color=self.tab_color(sid),
        )


def current_konsole() -> Konsole | None:
    services = konsole_services()
    return Konsole(services[0]) if services else None
