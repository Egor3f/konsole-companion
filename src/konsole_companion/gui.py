from __future__ import annotations

import sys

from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from . import tabsets


class ManagerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Konsole Tab Sets")
        self.resize(680, 440)

        self.set_list = QListWidget()
        self.set_list.currentTextChanged.connect(self._show_preview)

        save_btn = QPushButton("Save current tabs…")
        save_btn.clicked.connect(self._save_current)

        left = QVBoxLayout()
        left.addWidget(QLabel("Saved sets"))
        left.addWidget(self.set_list)
        left.addWidget(save_btn)

        self.preview = QTreeWidget()
        self.preview.setHeaderLabels(["Tab", "Profile", "Directory"])
        self.preview.setRootIsDecorated(False)

        self.restore_btn = QPushButton("Restore")
        self.restore_btn.clicked.connect(self._restore)
        self.rename_btn = QPushButton("Rename…")
        self.rename_btn.clicked.connect(self._rename)
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self._delete)

        actions = QHBoxLayout()
        actions.addWidget(self.restore_btn)
        actions.addWidget(self.rename_btn)
        actions.addWidget(self.delete_btn)
        actions.addStretch()

        right = QVBoxLayout()
        right.addWidget(QLabel("Tabs in set"))
        right.addWidget(self.preview)
        right.addLayout(actions)

        layout = QHBoxLayout(self)
        layout.addLayout(left, 1)
        layout.addLayout(right, 2)

        self._reload()

    def _reload(self):
        current = self.set_list.currentItem()
        keep = current.text() if current else None
        self.set_list.clear()
        names = tabsets.list_sets()
        self.set_list.addItems(names)
        if keep in names:
            self.set_list.setCurrentRow(names.index(keep))
        elif names:
            self.set_list.setCurrentRow(0)
        else:
            self._show_preview("")

    def _selected(self) -> str | None:
        item = self.set_list.currentItem()
        return item.text() if item else None

    def _show_preview(self, name: str):
        self.preview.clear()
        has = bool(name)
        for btn in (self.restore_btn, self.rename_btn, self.delete_btn):
            btn.setEnabled(has)
        if not has:
            return
        for tab in tabsets.load(name):
            item = QTreeWidgetItem(
                self.preview,
                [
                    tab.get("name") or "(default)",
                    tab.get("profile", ""),
                    tab.get("directory", ""),
                ],
            )
            color = tab.get("color")
            if color:
                item.setForeground(0, QBrush(QColor(color)))

    def _save_current(self):
        tabs = tabsets.capture()
        if not tabs:
            QMessageBox.warning(
                self, "No tabs", "No running Konsole session was found."
            )
            return
        name, ok = QInputDialog.getText(self, "Save tab set", "Name:")
        name = name.strip()
        if not ok or not name:
            return
        if name in tabsets.list_sets():
            if QMessageBox.question(
                self, "Overwrite", f"Set '{name}' exists. Overwrite?"
            ) != QMessageBox.StandardButton.Yes:
                return
        tabsets.save(name, tabs)
        self._reload()

    def _restore(self):
        name = self._selected()
        if name:
            tabsets.restore(name)

    def _rename(self):
        name = self._selected()
        if not name:
            return
        new, ok = QInputDialog.getText(
            self, "Rename set", "New name:", text=name
        )
        new = new.strip()
        if ok and new and new != name:
            tabsets.rename(name, new)
            self._reload()

    def _delete(self):
        name = self._selected()
        if not name:
            return
        if QMessageBox.question(
            self, "Delete", f"Delete set '{name}'?"
        ) == QMessageBox.StandardButton.Yes:
            tabsets.delete(name)
            self._reload()


def main() -> int:
    app = QApplication(sys.argv)
    window = ManagerWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
