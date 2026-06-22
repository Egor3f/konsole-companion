from __future__ import annotations

import sys

from PySide6.QtCore import QCoreApplication

from . import profiles, theme


def main() -> int:
    app = QCoreApplication(sys.argv)
    watcher = theme.ThemeWatcher()
    watcher.changed.connect(profiles.apply_theme)
    initial = watcher.current_is_dark()
    if initial is not None:
        profiles.apply_theme(initial)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
