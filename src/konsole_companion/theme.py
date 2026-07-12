from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot, SLOT
from PySide6.QtDBus import (
    QDBusConnection,
    QDBusInterface,
    QDBusMessage,
    QDBusVariant,
)

PORTAL_SERVICE = "org.freedesktop.portal.Desktop"
PORTAL_PATH = "/org/freedesktop/portal/desktop"
SETTINGS_IFACE = "org.freedesktop.portal.Settings"
NAMESPACE = "org.freedesktop.appearance"
KEY = "color-scheme"


def _to_int(value) -> int | None:
    # The portal wraps the value in one or two layers of variant; unwrap all.
    while isinstance(value, QDBusVariant):
        value = value.variant()
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _is_dark(value) -> bool | None:
    n = _to_int(value)
    if n is None:
        return None
    return n == 1


def current_is_dark() -> bool | None:
    iface = QDBusInterface(
        PORTAL_SERVICE, PORTAL_PATH, SETTINGS_IFACE,
        QDBusConnection.sessionBus(),
    )
    msg = iface.call("ReadOne", NAMESPACE, KEY)
    if msg.type() == QDBusMessage.MessageType.ErrorMessage:
        msg = iface.call("Read", NAMESPACE, KEY)
    if msg.type() == QDBusMessage.MessageType.ErrorMessage:
        return None
    return _is_dark(msg.arguments()[0])


class ThemeWatcher(QObject):
    changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        ok = QDBusConnection.sessionBus().connect(
            PORTAL_SERVICE,
            PORTAL_PATH,
            SETTINGS_IFACE,
            "SettingChanged",
            self,
            SLOT("_on_setting_changed(QString,QString,QDBusVariant)"),
        )
        if not ok:
            raise RuntimeError("failed to subscribe to portal SettingChanged")

    def current_is_dark(self) -> bool | None:
        return current_is_dark()

    @Slot(str, str, QDBusVariant)
    def _on_setting_changed(self, namespace: str, key: str, value) -> None:
        if namespace == NAMESPACE and key == KEY:
            dark = _is_dark(value)
            if dark is not None:
                self.changed.emit(dark)
