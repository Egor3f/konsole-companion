from __future__ import annotations

import sys

from PySide6.QtCore import QCoreApplication

from .tabguard import TabGuard
from .theme import ThemeWatcher


def main() -> int:
    app = QCoreApplication(sys.argv)
    watcher = ThemeWatcher()
    guard = TabGuard(watcher)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
