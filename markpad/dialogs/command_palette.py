"""
Command Palette dialog for MarkPad.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem,
)
from PyQt6.QtCore import Qt

from markpad.themes.stylesheet import build_stylesheet


class CommandPalette(QDialog):
    """Quick-access command palette with fuzzy search."""

    def __init__(self, parent, T: dict, commands: list):
        super().__init__(parent)
        self.T = T
        self.commands = commands
        self.setWindowTitle("Command Palette")
        self.setFixedSize(500, 350)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.setStyleSheet(build_stylesheet(T) + f"""
            QDialog {{ border: 1px solid {T['border']}; border-radius: 12px; background: {T['bg']}; }}
            QListWidget {{ border: none; background: transparent; font-size: 14px; outline: none; }}
            QListWidget::item {{ padding: 10px; border-radius: 6px; color: {T['editor_fg']}; }}
            QListWidget::item:selected {{ background: {T['accent']}; color: {T['accent_fg']}; }}
            QLineEdit {{ border: none; border-bottom: 1px solid {T['border']}; border-radius: 0; padding: 12px; font-size: 15px; background: transparent; }}
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 10, 10, 10)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search commands (Ctrl+P)...")
        self.search.textChanged.connect(self._filter)
        lay.addWidget(self.search)

        self.list_widget = QListWidget()
        lay.addWidget(self.list_widget)

        self._filter("")

        self.list_widget.itemActivated.connect(self._execute)
        self.search.returnPressed.connect(self._execute_first)

    def _filter(self, text):
        self.list_widget.clear()
        query = text.lower()
        for name, cb in self.commands:
            if query in name.lower():
                item = QListWidgetItem(name)
                item.setData(Qt.ItemDataRole.UserRole, cb)
                self.list_widget.addItem(item)
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def _execute(self, item):
        cb = item.data(Qt.ItemDataRole.UserRole)
        self.accept()
        cb()

    def _execute_first(self):
        if self.list_widget.count() > 0:
            self._execute(self.list_widget.item(0))
