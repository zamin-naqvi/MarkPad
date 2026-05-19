"""
Searchable Slash Command Menu for MarkPad.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QLineEdit
)
from PyQt6.QtCore import Qt
from markpad.themes.stylesheet import build_stylesheet
from markpad.utils.helpers import SNIPPET_TEMPLATES


class SlashCommandPopup(QDialog):
    """Floating searchable slash command menu."""

    def __init__(self, parent, editor, T: dict):
        super().__init__(parent)
        self.editor = editor
        self.T = T
        self.setFixedSize(260, 320)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.setStyleSheet(build_stylesheet(T) + f"""
            QDialog {{ border: 1px solid {T['border']}; border-radius: 8px; background: {T['bg']}; }}
            QListWidget {{ border: none; background: transparent; font-size: 13px; outline: none; }}
            QListWidget::item {{ padding: 8px 12px; border-radius: 6px; color: {T['editor_fg']}; }}
            QListWidget::item:selected {{ background: {T['accent']}; color: {T['accent_fg']}; font-weight: bold; }}
            QLineEdit {{ border: none; border-bottom: 1px solid {T['border']}; border-radius: 0; padding: 8px 12px; font-size: 13px; background: transparent; color: {T['editor_fg']}; }}
        """)
        
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        lay.setSpacing(4)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Type to filter...")
        self.search.textChanged.connect(self._filter)
        lay.addWidget(self.search)

        self.list_widget = QListWidget()
        lay.addWidget(self.list_widget)

        self.commands = [
            ("H1 Heading", "# "), ("H2 Heading", "## "), ("H3 Heading", "### "),
            ("Quote", "> "), ("Bullet List", "- "), ("Numbered List", "1. "),
            ("Code Block", "```\n\n```"), ("Table", SNIPPET_TEMPLATES.get("Table", "")),
            ("Note (Admonition)", "!!! note\n    "),
            ("Warning (Admonition)", "!!! warning\n    "),
            ("Math Block", "$$\n\n$$"),
            ("Mermaid Graph", "```mermaid\ngraph TD\n    A-->B;\n```"),
        ]

        self._filter("")
        self.list_widget.itemActivated.connect(self._execute)
        
        # Override Enter and Up/Down keys in the line edit to navigate the list
        self.search.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.search and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Up:
                row = self.list_widget.currentRow()
                if row > 0:
                    self.list_widget.setCurrentRow(row - 1)
                return True
            elif event.key() == Qt.Key.Key_Down:
                row = self.list_widget.currentRow()
                if row < self.list_widget.count() - 1:
                    self.list_widget.setCurrentRow(row + 1)
                return True
            elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                if self.list_widget.currentItem():
                    self._execute(self.list_widget.currentItem())
                return True
        return super().eventFilter(obj, event)

    def _filter(self, text):
        self.list_widget.clear()
        query = text.lower()
        for name, snippet in self.commands:
            if query in name.lower():
                item = QListWidgetItem(name)
                item.setData(Qt.ItemDataRole.UserRole, snippet)
                self.list_widget.addItem(item)
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def _execute(self, item):
        snippet = item.data(Qt.ItemDataRole.UserRole)
        self.accept()
        
        cursor = self.editor.textCursor()
        # Remove the slash
        cursor.movePosition(cursor.MoveOperation.Left, cursor.MoveMode.KeepAnchor, 1)
        if cursor.selectedText() == "/":
            cursor.removeSelectedText()
        cursor.insertText(snippet)
        
        if "```\n\n```" in snippet or "$$\n\n$$" in snippet:
            cursor.movePosition(cursor.MoveOperation.Up, cursor.MoveMode.MoveAnchor, 1)
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()
