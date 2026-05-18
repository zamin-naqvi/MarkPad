"""
Find & Replace dialog for MarkPad.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QTextEdit,
)
from PyQt6.QtGui import QTextCharFormat, QTextCursor, QColor

from markpad.themes.stylesheet import build_stylesheet


class FindDialog(QDialog):
    """Find & Replace dialog with match highlighting."""

    def __init__(self, parent, editor: QTextEdit, T: dict):
        super().__init__(parent)
        self.editor = editor
        self.T = T
        self.setWindowTitle("Find & Replace")
        self.setFixedSize(460, 200)
        self.setStyleSheet(build_stylesheet(T))
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(10)

        title = QLabel("Find & Replace")
        title.setStyleSheet("font-size:15px; font-weight:bold;")
        lay.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color:{self.T['border']};")
        lay.addWidget(line)

        for label, attr in [("Find", "find_edit"), ("Replace", "rep_edit")]:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setFixedWidth(70)
            e = QLineEdit()
            e.setPlaceholderText(label + "…")
            setattr(self, attr, e)
            row.addWidget(lbl)
            row.addWidget(e)
            lay.addLayout(row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        for text, slot, is_accent in [
            ("Find", self._find, False),
            ("Replace", self._replace, False),
            ("Replace All", self._replace_all, True),
        ]:
            b = QPushButton(text)
            if is_accent:
                b.setObjectName("accent")
            b.clicked.connect(slot)
            btn_row.addWidget(b)
        btn_row.addStretch()
        lay.addLayout(btn_row)

        self.status = QLabel("")
        self.status.setStyleSheet(f"color:{self.T['status_fg']}; font-size:12px;")
        lay.addWidget(self.status)

    def _find(self):
        q = self.find_edit.text()
        if not q:
            return
        doc = self.editor.document()
        cursor = doc.find(q)
        count = 0
        fmt = QTextCharFormat()
        fmt.setBackground(QColor(self.T["accent"]))
        fmt.setForeground(QColor(self.T["accent_fg"]))
        # Clear old highlights
        self.editor.selectAll()
        self.editor.setCurrentCharFormat(QTextCharFormat())
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)
        while not cursor.isNull():
            cursor.mergeCharFormat(fmt)
            count += 1
            cursor = doc.find(q, cursor)
        self.status.setText(f"{count} match(es) found")

    def _replace(self):
        q, r = self.find_edit.text(), self.rep_edit.text()
        if not q:
            return
        cursor = self.editor.textCursor()
        if cursor.selectedText() == q:
            cursor.insertText(r)
        else:
            c = self.editor.document().find(q, self.editor.textCursor())
            if not c.isNull():
                c.insertText(r)
                self.editor.setTextCursor(c)

    def _replace_all(self):
        q, r = self.find_edit.text(), self.rep_edit.text()
        if not q:
            return
        text = self.editor.toPlainText()
        n = text.count(q)
        self.editor.setPlainText(text.replace(q, r))
        self.status.setText(f"Replaced {n} occurrence(s)")
