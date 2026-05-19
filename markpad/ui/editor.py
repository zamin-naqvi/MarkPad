"""Editor widget with line numbers and scroll sync."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from markpad.utils.helpers import SNIPPET_TEMPLATES

class MarkPadTextEdit(QTextEdit):
    """Custom editor with slash command support and typewriter mode."""
    def __init__(self, theme: dict, parent=None):
        super().__init__(parent)
        self.T = theme
        self.typewriter_mode = False
        self._slash_menu = None
        self.cursorPositionChanged.connect(self._on_cursor_change)

    def _on_cursor_change(self):
        if self.typewriter_mode:
            self.centerCursor()

    def centerCursor(self):
        # QTextEdit does not have centerCursor by default
        cursor_rect = self.cursorRect()
        viewport_rect = self.viewport().rect()
        vbar = self.verticalScrollBar()
        # Calculate how much to scroll to put cursor in the vertical center
        offset = cursor_rect.center().y() - viewport_rect.center().y()
        vbar.setValue(vbar.value() + offset)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Slash and not e.modifiers() & Qt.KeyboardModifier.ControlModifier:
            super().keyPressEvent(e)
            self._show_slash_menu()
            return
        super().keyPressEvent(e)

    def _show_slash_menu(self):
        from markpad.dialogs.slash_menu import SlashCommandPopup
        
        popup = SlashCommandPopup(self, self, self.T)
        rect = self.cursorRect()
        global_pos = self.viewport().mapToGlobal(rect.bottomLeft())
        global_pos.setY(global_pos.y() + 5)
        popup.move(global_pos)
        popup.exec()


class EditorPanel(QWidget):
    """Editor panel with line numbers."""
    
    textChanged = pyqtSignal()

    def __init__(self, theme: dict, font_size: int = 15, show_label: bool = True):
        super().__init__()
        self.T = theme
        self.font_size = font_size
        self.setStyleSheet(f"background:{theme['editor_bg']};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        if show_label:
            lbl = QLabel("EDITOR")
            lbl.setObjectName("section_label")
            lay.addWidget(lbl)

        edit_row = QHBoxLayout()
        edit_row.setContentsMargins(0, 0, 0, 0)
        edit_row.setSpacing(0)

        self.lnums = QTextEdit()
        self.lnums.setObjectName("lnums")
        self.lnums.setReadOnly(True)
        self.lnums.setFixedWidth(52)
        self.lnums.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.lnums.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.lnums.setFont(QFont("Consolas", font_size - 2))
        self.lnums.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.editor = MarkPadTextEdit(theme)
        self.editor.setObjectName("editor")
        self.editor.setFont(QFont("Consolas", font_size))
        self.editor.setAcceptRichText(False)
        self.editor.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.editor.textChanged.connect(self._on_change)
        self.editor.verticalScrollBar().valueChanged.connect(self._sync_scroll)

        edit_row.addWidget(self.lnums)
        edit_row.addWidget(self.editor, 1)
        lay.addLayout(edit_row, 1)

    def _on_change(self):
        self._update_lnums()
        self.textChanged.emit()

    def _update_lnums(self):
        try:
            n = self.editor.document().blockCount()
            self.lnums.setPlainText("\n".join(str(i) for i in range(1, n + 1)))
            self._sync_scroll()
        except RuntimeError:
            pass

    def _sync_scroll(self):
        try:
            self.lnums.verticalScrollBar().setValue(
                self.editor.verticalScrollBar().value()
            )
        except RuntimeError:
            pass

    def set_font_size(self, size: int):
        self.font_size = size
        self.editor.setFont(QFont("Consolas", size))
        self.lnums.setFont(QFont("Consolas", size - 2))

    def toPlainText(self) -> str:
        return self.editor.toPlainText()

    def setPlainText(self, text: str):
        self.editor.setPlainText(text)
        self._update_lnums()

    def textCursor(self):
        return self.editor.textCursor()

    def setTextCursor(self, cursor):
        self.editor.setTextCursor(cursor)

    def insertPlainText(self, text: str):
        self.editor.insertPlainText(text)

    def document(self):
        return self.editor.document()

    def selectAll(self):
        self.editor.selectAll()

    def undo(self):
        self.editor.undo()

    def redo(self):
        self.editor.redo()
