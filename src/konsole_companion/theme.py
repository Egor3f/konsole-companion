from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot, SLOT
from PySide6.QtDBus import QDBusConnection, QDBusVariant

PORTAL_SERVICE = "org.freedesktop.portal.Desktop"
PORTAL_PATH = "/org/freedesktop/portal/desktop"
SETTINGS_IFACE = "org.freedesktop.portal.Settings"
NAMESPACE = "org.freedesktop.appearance"
KEY = "color-scheme"


class ThemeWatcher(QObject):
    changed = Signal()

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

    @Slot(str, str, QDBusVariant)
    def _on_setting_changed(self, namespace: str, key: str, value) -> None:
        if namespace == NAMESPACE and key == KEY:
            self.changed.emit()
