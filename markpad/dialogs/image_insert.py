"""
Image insert dialog for MarkPad.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QRadioButton, QButtonGroup, QFrame,
    QFileDialog, QMessageBox,
)

from markpad.themes.stylesheet import build_stylesheet


class ImageDialog(QDialog):
    """Dialog for inserting images with size options."""

    def __init__(self, parent, T: dict):
        super().__init__(parent)
        self.T = T
        self.result_text = None
        self.setWindowTitle("Insert Image")
        self.setFixedSize(500, 320)
        self.setStyleSheet(build_stylesheet(T))
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(10)

        title = QLabel("Insert Image")
        title.setStyleSheet("font-size:15px; font-weight:bold;")
        lay.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color:{self.T['border']};")
        lay.addWidget(line)

        # File row
        file_row = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Image path…")
        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("accent")
        browse_btn.setFixedWidth(90)
        browse_btn.clicked.connect(self._browse)
        file_row.addWidget(self.path_edit)
        file_row.addWidget(browse_btn)
        lay.addLayout(file_row)

        # Alt text
        alt_row = QHBoxLayout()
        alt_row.addWidget(QLabel("Alt text:"))
        self.alt_edit = QLineEdit("Image")
        alt_row.addWidget(self.alt_edit)
        lay.addLayout(alt_row)

        # Size mode
        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Size:"))
        self.mode_group = QButtonGroup(self)
        for i, (val, lbl) in enumerate([
            ("original", "Original"),
            ("percent", "Percent %"),
            ("pixels", "Pixels px"),
        ]):
            rb = QRadioButton(lbl)
            rb.setProperty("mode_val", val)
            if i == 0:
                rb.setChecked(True)
            self.mode_group.addButton(rb, i)
            size_row.addWidget(rb)
        size_row.addStretch()
        lay.addLayout(size_row)

        # Width input
        self.width_row = QHBoxLayout()
        self.width_row.addWidget(QLabel("Width:"))
        self.width_edit = QLineEdit("400")
        self.width_edit.setFixedWidth(80)
        self.unit_lbl = QLabel("px")
        self.width_row.addWidget(self.width_edit)
        self.width_row.addWidget(self.unit_lbl)
        self.width_row.addStretch()
        lay.addLayout(self.width_row)
        self.width_edit.hide()
        self.unit_lbl.hide()
        self.mode_group.idClicked.connect(self._mode_changed)

        lay.addStretch()

        # Buttons
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet(f"color:{self.T['border']};")
        lay.addWidget(line2)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        insert = QPushButton("Insert")
        insert.setObjectName("accent")
        insert.clicked.connect(self._confirm)
        btn_row.addWidget(cancel)
        btn_row.addWidget(insert)
        lay.addLayout(btn_row)

    def _browse(self):
        p, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;All Files (*)")
        if p:
            self.path_edit.setText(p)

    def _mode_changed(self, idx):
        btn = self.mode_group.button(idx)
        mode = btn.property("mode_val")
        show = mode != "original"
        self.width_edit.setVisible(show)
        self.unit_lbl.setVisible(show)
        if mode == "percent":
            self.unit_lbl.setText("%")
            self.width_edit.setText("50")
        else:
            self.unit_lbl.setText("px")
            self.width_edit.setText("400")

    def _confirm(self):
        path = self.path_edit.text().strip()
        if not path:
            QMessageBox.warning(self, "Error", "Please select an image.")
            return
        alt = self.alt_edit.text().strip() or "Image"
        btn = self.mode_group.checkedButton()
        mode = btn.property("mode_val") if btn else "original"
        if mode == "original":
            self.result_text = f"![{alt}]({path})"
        elif mode == "percent":
            self.result_text = f'<img src="{path}" alt="{alt}" style="width:{self.width_edit.text()}%">'
        else:
            self.result_text = f'<img src="{path}" alt="{alt}" width="{self.width_edit.text()}">'
        self.accept()
