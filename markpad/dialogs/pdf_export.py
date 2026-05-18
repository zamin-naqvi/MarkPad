"""
PDF export dialog for MarkPad.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QRadioButton, QButtonGroup, QFrame, QWidget,
    QFileDialog, QMessageBox,
)

from markpad.themes.stylesheet import build_stylesheet


class PDFExportDialog(QDialog):
    """PDF export dialog with style selection."""

    def __init__(self, parent, T: dict):
        super().__init__(parent)
        self.T = T
        self.result_style = "github"
        self.result_path = None
        self.setWindowTitle("Export PDF")
        self.setFixedSize(520, 380)
        self.setStyleSheet(build_stylesheet(T))
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(12)

        title = QLabel("Export to PDF")
        title.setStyleSheet("font-size:15px; font-weight:bold;")
        lay.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color:{self.T['border']};")
        lay.addWidget(line)

        style_lbl = QLabel("Choose Style:")
        style_lbl.setStyleSheet("font-weight:bold; font-size:13px;")
        lay.addWidget(style_lbl)

        self.style_group = QButtonGroup(self)
        styles = [
            ("github", "GitHub Style", "#FFFFFF", "#1D1D1F", "Clean, minimal design"),
            ("ace", "Ace Editor", "#1C1C1E", "#F5F5F7", "Dark theme for code"),
            ("libre", "LibreOffice", "#FAFAFA", "#2C2C2E", "Professional docs"),
        ]

        for i, (val, name, bg, fg, desc) in enumerate(styles):
            style_widget = QWidget()
            style_widget.setStyleSheet(f"""
                QWidget {{
                    background: {self.T['btn_bg']};
                    border: 2px solid {self.T['btn_border']};
                    border-radius: 10px;
                    padding: 0;
                }}
                QWidget:hover {{
                    background: {self.T['btn_hover']};
                    border-color: {self.T['accent']};
                }}
            """)
            style_lay = QHBoxLayout(style_widget)
            style_lay.setContentsMargins(12, 12, 12, 12)
            style_lay.setSpacing(12)

            rb = QRadioButton()
            rb.setProperty("style_val", val)
            if i == 0:
                rb.setChecked(True)
            self.style_group.addButton(rb, i)
            style_lay.addWidget(rb)

            preview = QWidget()
            preview.setFixedSize(60, 50)
            preview.setStyleSheet(f"""
                QWidget {{
                    background: {bg};
                    border: 1px solid {self.T['border']};
                    border-radius: 6px;
                }}
            """)
            preview_lay = QVBoxLayout(preview)
            preview_lay.setContentsMargins(6, 6, 6, 6)
            preview_lay.setSpacing(2)

            for j in range(3):
                line_widget = QWidget()
                line_widget.setFixedHeight(4)
                line_widget.setStyleSheet(f"background: {fg}; border-radius: 2px;")
                if j == 0:
                    line_widget.setFixedWidth(40)
                elif j == 1:
                    line_widget.setFixedWidth(35)
                else:
                    line_widget.setFixedWidth(30)
                preview_lay.addWidget(line_widget)

            style_lay.addWidget(preview)

            text_lay = QVBoxLayout()
            text_lay.setSpacing(2)
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet("font-weight:bold; font-size:13px;")
            desc_lbl = QLabel(desc)
            desc_lbl.setStyleSheet(f"color:{self.T['status_fg']}; font-size:11px;")
            text_lay.addWidget(name_lbl)
            text_lay.addWidget(desc_lbl)
            style_lay.addLayout(text_lay)
            style_lay.addStretch()

            lay.addWidget(style_widget)

        lay.addSpacing(8)

        path_lbl = QLabel("Save to:")
        path_lbl.setStyleSheet("font-weight:bold; font-size:13px;")
        lay.addWidget(path_lbl)

        file_row = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Choose destination…")
        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("accent")
        browse_btn.setFixedWidth(90)
        browse_btn.clicked.connect(self._browse)
        file_row.addWidget(self.path_edit)
        file_row.addWidget(browse_btn)
        lay.addLayout(file_row)

        lay.addStretch()

        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet(f"color:{self.T['border']};")
        lay.addWidget(line2)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        export = QPushButton("Export PDF")
        export.setObjectName("accent")
        export.clicked.connect(self._confirm)
        btn_row.addWidget(cancel)
        btn_row.addWidget(export)
        lay.addLayout(btn_row)

    def _browse(self):
        p, _ = QFileDialog.getSaveFileName(
            self, "Export PDF", "", "PDF Files (*.pdf);;All Files (*)")
        if p:
            if not p.lower().endswith('.pdf'):
                p += '.pdf'
            self.path_edit.setText(p)

    def _confirm(self):
        path = self.path_edit.text().strip()
        if not path:
            QMessageBox.warning(self, "Error", "Please choose a destination file.")
            return
        btn = self.style_group.checkedButton()
        self.result_style = btn.property("style_val") if btn else "github"
        self.result_path = path
        self.accept()
