#!/usr/bin/env python3
"""
MarkPad — Markdown Editor & Previewer  (PyQt6)
Run: python main.py
"""

import sys, os, re, subprocess

# ── Auto-install deps ──────────────────────────────────────────────────────
for _pkg, _imp in [("markdown", "markdown"), ("PyQt6", "PyQt6")]:
    try:
        __import__(_imp)
    except ImportError:
        print(f"Installing {_pkg}…")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", _pkg])

import markdown as _md

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter, QTextEdit,
    QToolBar, QStatusBar, QFileDialog, QMessageBox, QInputDialog,
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QRadioButton, QButtonGroup, QFrame, QSizePolicy,
    QScrollArea, QTreeView, QListWidget, QListWidgetItem
)
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False
    print("Note: PyQt6-WebEngine not available, using plain text preview.")
from PyQt6.QtCore import Qt, QTimer, QSize, QUrl, pyqtSignal
from PyQt6.QtGui import (
    QFileSystemModel,
    QIcon, QPixmap, QImage, QFont, QKeySequence, QAction,
    QColor, QPainter, QPainterPath, QBrush, QPen,
)

# ── Icon directory ─────────────────────────────────────────────────────────
ICONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")

def load_icon(name: str, color: str = "#1D1D1F", size: int = 20) -> QIcon:
    """Load a PNG icon from icons/ and recolor it."""
    h = color.lstrip("#")
    lum = 0.299*int(h[0:2],16) + 0.587*int(h[2:4],16) + 0.114*int(h[4:6],16)
    variant = "ffffff" if lum < 128 else "000000"
    path = os.path.join(ICONS_DIR, f"{name}_{variant}.png")
    if not os.path.exists(path):
        return QIcon()
    img = QImage(path).convertToFormat(QImage.Format.Format_ARGB32)
    # Recolor: replace all non-transparent pixels with target color
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    for y in range(img.height()):
        for x in range(img.width()):
            px = img.pixel(x, y)
            a  = (px >> 24) & 0xFF
            if a > 0:
                img.setPixel(x, y, (a << 24) | (r << 16) | (g << 8) | b)
    pix = QPixmap.fromImage(img).scaled(
        size, size, Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation)
    return QIcon(pix)


# ── Themes ─────────────────────────────────────────────────────────────────
LIGHT = {
    "bg":           "#F5F5F7",
    "toolbar_bg":   "#EBEBF0",
    "editor_bg":    "#FFFFFF",
    "editor_fg":    "#1D1D1F",
    "preview_bg":   "#FAFAFA",
    "border":       "#D1D1D6",
    "accent":       "#0071E3",
    "accent_fg":    "#FFFFFF",
    "btn_bg":       "#FFFFFF",
    "btn_fg":       "#1D1D1F",
    "btn_hover":    "#E5E5EA",
    "btn_border":   "#D1D1D6",
    "tab_active":   "#0071E3",
    "tab_active_fg":"#FFFFFF",
    "tab_bg":       "#DCDCE0",
    "tab_fg":       "#3A3A3C",
    "status_bg":    "#E8E8ED",
    "status_fg":    "#6E6E73",
    "lnum_bg":      "#F2F2F7",
    "lnum_fg":      "#AEAEB2",
    "scrollbar":    "#C7C7CC",
    "icon_color":   "#1D1D1F",
}
DARK = {
    "bg":           "#1C1C1E",
    "toolbar_bg":   "#2C2C2E",
    "editor_bg":    "#1C1C1E",
    "editor_fg":    "#F5F5F7",
    "preview_bg":   "#242426",
    "border":       "#3A3A3C",
    "accent":       "#0A84FF",
    "accent_fg":    "#FFFFFF",
    "btn_bg":       "#3A3A3C",
    "btn_fg":       "#F5F5F7",
    "btn_hover":    "#48484A",
    "btn_border":   "#48484A",
    "tab_active":   "#0A84FF",
    "tab_active_fg":"#FFFFFF",
    "tab_bg":       "#3A3A3C",
    "tab_fg":       "#EBEBF0",
    "status_bg":    "#2C2C2E",
    "status_fg":    "#8E8E93",
    "lnum_bg":      "#2C2C2E",
    "lnum_fg":      "#48484A",
    "scrollbar":    "#48484A",
    "icon_color":   "#F5F5F7",
}

SAMPLE = """\
# Welcome to MarkPad

A clean macOS-style Markdown editor built in Python + PyQt6.

## Formatting

**bold**, *italic*, ~~strikethrough~~, `inline code`

## Lists

- Item one
- Item two
  - Nested

1. First
2. Second

## Blockquote

> "Simplicity is the ultimate sophistication." — da Vinci

## Code

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

## Math & Diagrams

**MathJax** supports beautiful LaTeX equations:
$$ E = mc^2 $$

$$ \int_{a}^{b} x^2 \,dx = \frac{b^3 - a^3}{3} $$

**Mermaid.js** allows you to create flowcharts directly from text:

```mermaid
graph TD;
    A[Markdown] --> B(Live Preview);
    B --> C{Render};
    C -->|Success| D[HTML & Diagrams];
    C -->|Export| E[PDF Document];
```

## Table

| Feature   | Shortcut | Status |
|-----------|----------|--------|
| Bold      | Ctrl+B   | Yes    |
| Italic    | Ctrl+I   | Yes    |
| PDF Export| Menu     | Yes    |

---

Edit here — preview updates live!
"""


# ── Stylesheet builder ─────────────────────────────────────────────────────
def build_stylesheet(T: dict) -> str:
    a  = T["accent"]
    af = T["accent_fg"]
    bg = T["bg"]
    tb = T["toolbar_bg"]
    bb = T["btn_bg"]
    bf = T["btn_fg"]
    bh = T["btn_hover"]
    bd = T["btn_border"]
    sb = T["status_bg"]
    sf = T["status_fg"]
    br = T["border"]

    return f"""
    QMainWindow, QWidget#central {{
        background: {bg};
    }}
    /* ── Toolbar ── */
    QToolBar {{
        background: {tb};
        border: none;
        border-bottom: 1px solid {br};
        spacing: 4px;
        padding: 4px 8px;
    }}
    QToolBar::separator {{
        background: {br};
        width: 1px;
        margin: 6px 4px;
    }}
    /* ── Toolbar buttons ── */
    QToolButton {{
        background: {bb};
        color: {bf};
        border: 1px solid {bd};
        border-radius: 8px;
        padding: 5px 10px;
        font-family: "Helvetica Neue", Arial;
        font-size: 13px;
        min-width: 28px;
        min-height: 28px;
    }}
    QToolButton:hover {{
        background: {bh};
    }}
    QToolButton:pressed {{
        background: {bh};
        border-color: {a};
    }}
    /* ── Generic QPushButton ── */
    QPushButton {{
        background: {bb};
        color: {bf};
        border: 1px solid {bd};
        border-radius: 10px;
        padding: 7px 18px;
        font-family: "Helvetica Neue", Arial;
        font-size: 13px;
        min-height: 32px;
    }}
    QPushButton:hover  {{ background: {bh}; }}
    QPushButton:pressed {{ background: {bh}; border-color: {a}; }}
    QPushButton#accent {{
        background: {a};
        color: {af};
        border: none;
    }}
    QPushButton#accent:hover  {{ background: {a}; opacity: 0.9; }}
    /* ── Editor ── */
    QTextEdit#editor {{
        background: {T["editor_bg"]};
        color: {T["editor_fg"]};
        border: none;
        font-family: "Menlo", "Consolas", monospace;
        font-size: 14px;
        selection-background-color: {a};
        selection-color: {af};
    }}
    QTextEdit#editor QScrollBar:vertical {{
        background: transparent;
        width: 8px;
        margin: 0;
    }}
    QTextEdit#editor QScrollBar::handle:vertical {{
        background: {T["scrollbar"]};
        border-radius: 4px;
        min-height: 30px;
    }}
    QTextEdit#editor QScrollBar::add-line:vertical,
    QTextEdit#editor QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QTextEdit#editor QScrollBar::add-page:vertical,
    QTextEdit#editor QScrollBar::sub-page:vertical {{
        background: transparent;
    }}
    /* ── Line numbers ── */
    QTextEdit#lnums {{
        background: {T["lnum_bg"]};
        color: {T["lnum_fg"]};
        border: none;
        font-family: "Menlo", "Consolas", monospace;
        font-size: 12px;
    }}
    /* ── Status bar ── */
    QStatusBar {{
        background: {T["status_bg"]};
        color: {T["status_fg"]};
        border-top: 1px solid {br};
        font-size: 12px;
        padding: 0 8px;
    }}
    /* ── Dialogs ── */
    QDialog {{
        background: {bg};
    }}
    QLabel {{
        color: {T["editor_fg"]};
        background: transparent;
    }}
    QLineEdit {{
        background: {T["editor_bg"]};
        color: {T["editor_fg"]};
        border: 1px solid {bd};
        border-radius: 8px;
        padding: 6px 10px;
        font-size: 13px;
        selection-background-color: {a};
    }}
    QLineEdit:focus {{
        border-color: {a};
    }}
    QRadioButton {{
        color: {T["editor_fg"]};
        font-size: 13px;
        spacing: 6px;
    }}
    QRadioButton::indicator {{
        width: 16px; height: 16px;
        border-radius: 8px;
        border: 2px solid {bd};
        background: {T["editor_bg"]};
    }}
    QRadioButton::indicator:checked {{
        background: {a};
        border-color: {a};
    }}
    /* ── Scrollbars (global) ── */
    QScrollBar:vertical {{
        background: transparent;
        width: 8px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {T["scrollbar"]};
        border-radius: 4px;
        min-height: 30px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
    QScrollBar:horizontal {{
        background: transparent;
        height: 8px;
        margin: 0;
    }}
    QScrollBar::handle:horizontal {{
        background: {T["scrollbar"]};
        border-radius: 4px;
        min-width: 30px;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
    /* ── WebEngineView scrollbar ── */
    QWebEngineView QScrollBar:vertical {{
        background: transparent;
        width: 8px;
        margin: 0;
    }}
    QWebEngineView QScrollBar::handle:vertical {{
        background: {T["scrollbar"]};
        border-radius: 4px;
        min-height: 30px;
    }}
    QWebEngineView QScrollBar::add-line:vertical,
    QWebEngineView QScrollBar::sub-line:vertical {{ height: 0; }}
    QWebEngineView QScrollBar::add-page:vertical,
    QWebEngineView QScrollBar::sub-page:vertical {{ background: transparent; }}
    /* ── Splitter ── */
    QSplitter::handle {{
        background: {br};
        width: 1px;
    }}
    /* ── Section labels ── */
    QLabel#section_label {{
        background: {tb};
        color: {T["status_fg"]};
        font-size: 10px;
        font-weight: bold;
        padding: 3px 12px;
        border-bottom: 1px solid {br};
        letter-spacing: 1px;
    }}
    /* ── Title bar ── */
    QWidget#titlebar {{
        background: {tb};
        border-bottom: 1px solid {br};
    }}
    QLabel#filename_label {{
        color: {T["status_fg"]};
        font-size: 12px;
        background: transparent;
    }}
    /* ── Tab container ── */
    QWidget#tab_container {{
        background: {T["tab_bg"]};
        border-radius: 10px;
        min-height: 42px;
        max-height: 42px;
    }}
    /* ── Tab segment buttons ── */
    QPushButton#tab_btn {{
        background: transparent;
        color: {T["tab_fg"]};
        border: none;
        border-radius: 8px;
        padding: 0px 20px;
        font-size: 13px;
        min-height: 32px;
        max-height: 32px;
    }}
    QPushButton#tab_btn:hover {{ background: {bh}; }}
    QPushButton#tab_btn[active="true"] {{
        background: {T["tab_active"]};
        color: {T["tab_active_fg"]};
    }}"""


# ── Preview HTML wrapper ───────────────────────────────────────────────────
def build_preview_html(md_text: str, T: dict, font_size: int = 15) -> str:
    try:
        body = _md.markdown(md_text, extensions=["fenced_code","tables","nl2br","sane_lists","toc"])
    except Exception:
        body = _md.markdown(md_text, extensions=["fenced_code","tables"])

    is_dark = T["bg"] == DARK["bg"]
    bg      = T["preview_bg"]
    fg      = T["editor_fg"]
    accent  = T["accent"]
    code_bg = T["lnum_bg"]
    border  = T["border"]
    quote   = T["status_fg"]
    scrollbar = T["scrollbar"]
    even_row = "rgba(0,0,0,0.04)" if not is_dark else "rgba(255,255,255,0.04)"

    css = f"""
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
        font-family: -apple-system, "Helvetica Neue", Arial, sans-serif;
        font-size: {font_size}px; line-height: 1.75;
        color: {fg}; background: {bg};
        padding: 28px 36px; max-width: 100%;
    }}
    /* Custom scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: transparent;
    }}
    ::-webkit-scrollbar-thumb {{
        background: {scrollbar};
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: {scrollbar};
        opacity: 0.8;
    }}
    h1 {{ font-size: {font_size+14}px; font-weight: 700;
          border-bottom: 2px solid {border}; padding-bottom: .3em; margin: 1.4em 0 .6em; }}
    h2 {{ font-size: {font_size+9}px; font-weight: 700;
          border-bottom: 1px solid {border}; padding-bottom: .2em; margin: 1.2em 0 .5em; }}
    h3 {{ font-size: {font_size+5}px; font-weight: 600; margin: 1em 0 .4em; }}
    h4 {{ font-size: {font_size+2}px; font-weight: 600; margin: .8em 0 .3em; }}
    p  {{ margin: .6em 0; }}
    a  {{ color: {accent}; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    strong {{ font-weight: 700; }} em {{ font-style: italic; }}
    del {{ text-decoration: line-through; opacity: .7; }}
    code {{
        font-family: "Menlo","Consolas",monospace; font-size: .88em;
        background: {code_bg}; padding: 2px 6px; border-radius: 5px;
    }}
    pre {{
        background: {code_bg}; border-radius: 10px;
        padding: 16px 20px; overflow-x: auto; margin: 1em 0;
    }}
    pre code {{ background: none; padding: 0; font-size: .9em; }}
    blockquote {{
        border-left: 4px solid {accent}; margin: 1em 0;
        padding: 6px 0 6px 20px; color: {quote}; font-style: italic;
    }}
    ul, ol {{ padding-left: 1.8em; margin: .6em 0; }}
    li {{ margin: .25em 0; }}
    hr {{ border: none; border-top: 1px solid {border}; margin: 2em 0; }}
    img {{ max-width: 100%; border-radius: 8px; display: block; margin: .8em 0; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1em 0; font-size: .95em; }}
    th, td {{ border: 1px solid {border}; padding: 9px 14px; text-align: left; }}
    th {{ background: {code_bg}; font-weight: 600; }}
    tr:nth-child(even) td {{ background: {even_row}; }}
    """
    scripts = f"""
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <script type="module">
      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
      mermaid.initialize({{ startOnLoad: true, theme: '{'dark' if is_dark else 'default'}' }});
      document.addEventListener("DOMContentLoaded", () => {{
        const blocks = document.querySelectorAll("code.language-mermaid, code.mermaid");
        blocks.forEach(block => {{
            const div = document.createElement("div");
            div.className = "mermaid";
            div.textContent = block.textContent;
            block.parentNode.replaceWith(div);
        }});
      }});
    </script>
    """
    return f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{css}</style>{scripts}</head><body>{body}</body></html>"


# ── Find & Replace Dialog ──────────────────────────────────────────────────
class FindDialog(QDialog):
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

        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color:{self.T['border']};")
        lay.addWidget(line)

        for label, attr in [("Find", "find_edit"), ("Replace", "rep_edit")]:
            row = QHBoxLayout()
            lbl = QLabel(label); lbl.setFixedWidth(70)
            e   = QLineEdit(); e.setPlaceholderText(label + "…")
            setattr(self, attr, e)
            row.addWidget(lbl); row.addWidget(e)
            lay.addLayout(row)

        btn_row = QHBoxLayout(); btn_row.setSpacing(8)
        for text, slot, is_accent in [
            ("Find", self._find, False),
            ("Replace", self._replace, False),
            ("Replace All", self._replace_all, True),
        ]:
            b = QPushButton(text)
            if is_accent: b.setObjectName("accent")
            b.clicked.connect(slot)
            btn_row.addWidget(b)
        btn_row.addStretch()
        lay.addLayout(btn_row)

        self.status = QLabel("")
        self.status.setStyleSheet(f"color:{self.T['status_fg']}; font-size:12px;")
        lay.addWidget(self.status)

    def _find(self):
        from PyQt6.QtGui import QTextCharFormat, QTextCursor
        q = self.find_edit.text()
        if not q: return
        doc = self.editor.document()
        cursor = doc.find(q)
        count = 0
        fmt = QTextCharFormat()
        fmt.setBackground(QColor(self.T["accent"]))
        fmt.setForeground(QColor(self.T["accent_fg"]))
        # clear old highlights
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
        if not q: return
        cursor = self.editor.textCursor()
        if cursor.selectedText() == q:
            cursor.insertText(r)
        else:
            from PyQt6.QtGui import QTextCursor
            c = self.editor.document().find(q, self.editor.textCursor())
            if not c.isNull():
                c.insertText(r)
                self.editor.setTextCursor(c)

    def _replace_all(self):
        q, r = self.find_edit.text(), self.rep_edit.text()
        if not q: return
        text = self.editor.toPlainText()
        n = text.count(q)
        self.editor.setPlainText(text.replace(q, r))
        self.status.setText(f"Replaced {n} occurrence(s)")


# ── Image Insert Dialog ────────────────────────────────────────────────────
class ImageDialog(QDialog):
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

        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color:{self.T['border']};")
        lay.addWidget(line)

        # File row
        file_row = QHBoxLayout()
        self.path_edit = QLineEdit(); self.path_edit.setPlaceholderText("Image path…")
        browse_btn = QPushButton("Browse"); browse_btn.setObjectName("accent")
        browse_btn.setFixedWidth(90)
        browse_btn.clicked.connect(self._browse)
        file_row.addWidget(self.path_edit); file_row.addWidget(browse_btn)
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
        for i, (val, lbl) in enumerate([("original","Original"),("percent","Percent %"),("pixels","Pixels px")]):
            rb = QRadioButton(lbl)
            rb.setProperty("mode_val", val)
            if i == 0: rb.setChecked(True)
            self.mode_group.addButton(rb, i)
            size_row.addWidget(rb)
        size_row.addStretch()
        lay.addLayout(size_row)

        # Width input (hidden initially)
        self.width_row = QHBoxLayout()
        self.width_row.addWidget(QLabel("Width:"))
        self.width_edit = QLineEdit("400"); self.width_edit.setFixedWidth(80)
        self.unit_lbl = QLabel("px")
        self.width_row.addWidget(self.width_edit)
        self.width_row.addWidget(self.unit_lbl)
        self.width_row.addStretch()
        lay.addLayout(self.width_row)
        self.width_edit.hide(); self.unit_lbl.hide()
        self.mode_group.idClicked.connect(self._mode_changed)

        lay.addStretch()

        # Buttons
        line2 = QFrame(); line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet(f"color:{self.T['border']};")
        lay.addWidget(line2)
        btn_row = QHBoxLayout(); btn_row.addStretch()
        cancel = QPushButton("Cancel"); cancel.clicked.connect(self.reject)
        insert = QPushButton("Insert"); insert.setObjectName("accent")
        insert.clicked.connect(self._confirm)
        btn_row.addWidget(cancel); btn_row.addWidget(insert)
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
            self.unit_lbl.setText("%"); self.width_edit.setText("50")
        else:
            self.unit_lbl.setText("px"); self.width_edit.setText("400")

    def _confirm(self):
        path = self.path_edit.text().strip()
        if not path:
            QMessageBox.warning(self, "Error", "Please select an image.")
            return
        alt  = self.alt_edit.text().strip() or "Image"
        btn  = self.mode_group.checkedButton()
        mode = btn.property("mode_val") if btn else "original"
        if mode == "original":
            self.result_text = f"![{alt}]({path})"
        elif mode == "percent":
            self.result_text = f'<img src="{path}" alt="{alt}" style="width:{self.width_edit.text()}%">'
        else:
            self.result_text = f'<img src="{path}" alt="{alt}" width="{self.width_edit.text()}">'
        self.accept()


# ── Command Palette ────────────────────────────────────────────────────────
class CommandPalette(QDialog):
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

# ── PDF Export Dialog ──────────────────────────────────────────────────────
class PDFExportDialog(QDialog):
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

        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color:{self.T['border']};")
        lay.addWidget(line)

        # Style selection
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
            if i == 0: rb.setChecked(True)
            self.style_group.addButton(rb, i)
            style_lay.addWidget(rb)

            # Style preview box
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
            
            # Mini preview content
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

            # Text info
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

        # File path
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

        # Buttons
        line2 = QFrame(); line2.setFrameShape(QFrame.Shape.HLine)
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
            self, "Export PDF", "",
            "PDF Files (*.pdf);;All Files (*)")
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


# ── Main Window ────────────────────────────────────────────────────────────
class MarkPad(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MarkPad")
        self.resize(1280, 820)
        self.setMinimumSize(860, 600)
        
        # Set window icon
        icon_path = os.path.join(ICONS_DIR, "app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.is_dark       = False
        self.T             = LIGHT
        self.current_file  = None
        self.modified      = False
        self.view_mode     = "split"   # "edit" | "split" | "preview"
        self.font_size     = 15
        self._document_text = SAMPLE
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.timeout.connect(self._update_preview)

        self._build()
        self.editor.setPlainText(SAMPLE)
        self._update_preview()
        self._update_status()

    # ── Build ──────────────────────────────────────────────────────────
    def _build(self):
        T = self.T
        self.setStyleSheet(build_stylesheet(T))

        central = QWidget(); central.setObjectName("central")
        self.setCentralWidget(central)
        root_lay = QVBoxLayout(central)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.setSpacing(0)

        # Title bar
        self._title_bar = self._make_titlebar()
        root_lay.addWidget(self._title_bar)

        # Toolbar
        self._toolbar = self._make_toolbar()
        root_lay.addWidget(self._toolbar)

        # Content area
        self._content_widget = QWidget()
        self._content_lay    = QVBoxLayout(self._content_widget)
        self._content_lay.setContentsMargins(0, 0, 0, 0)
        self._content_lay.setSpacing(0)

        # Splitter for sidebar and content
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        root_lay.addWidget(self.main_splitter, 1)

        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setStyleSheet(f"background: {T['toolbar_bg']};")
        sidebar_lay = QVBoxLayout(self.sidebar)
        sidebar_lay.setContentsMargins(0, 0, 0, 0)
        sidebar_lay.setSpacing(0)
        
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("")
        self.file_model.setNameFilters(["*.md", "*.txt", "*.markdown"])
        self.file_model.setNameFilterDisables(False)
        
        self.tree = QTreeView()
        self.tree.setModel(self.file_model)
        self.tree.setRootIndex(self.file_model.index(os.getcwd()))
        self.tree.setHeaderHidden(True)
        self.tree.setStyleSheet(f"QTreeView {{ background: transparent; border: none; color: {T['editor_fg']}; }} QTreeView::item {{ padding: 4px; }} QTreeView::item:selected {{ background: {T['accent']}; color: {T['accent_fg']}; }}")
        for i in range(1, 4):
            self.tree.hideColumn(i)
        self.tree.doubleClicked.connect(self._open_from_tree)
        
        sidebar_lbl = QLabel("VAULT"); sidebar_lbl.setObjectName("section_label")
        sidebar_lay.addWidget(sidebar_lbl)
        sidebar_lay.addWidget(self.tree)
        
        self.main_splitter.addWidget(self.sidebar)
        self.main_splitter.addWidget(self._content_widget)
        self.main_splitter.setSizes([200, 1000])
        self.sidebar.hide() # Hidden by default

        self._make_content()

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._stat_left  = QLabel("")
        self._stat_right = QLabel("")
        self.status_bar.addWidget(self._stat_left)
        self.status_bar.addPermanentWidget(self._stat_right)

        self._setup_menus()

    def _make_titlebar(self):
        T = self.T
        bar = QWidget(); bar.setObjectName("titlebar")
        bar.setFixedHeight(52)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self._fname_lbl = QLabel("Untitled.md")
        self._fname_lbl.setObjectName("filename_label")
        lay.addWidget(self._fname_lbl)

        lay.addStretch()

        # Segmented tab switcher
        tab_container = QWidget(); tab_container.setObjectName("tab_container")
        tab_container.setFixedHeight(42)
        tab_lay = QHBoxLayout(tab_container)
        tab_lay.setContentsMargins(5, 5, 5, 5)
        tab_lay.setSpacing(3)

        self._tab_btns = {}
        for key, label in [("edit","Edit"), ("split","Split"), ("preview","Preview")]:
            btn = QPushButton(label)
            btn.setObjectName("tab_btn")
            btn.setCheckable(False)
            btn.setProperty("active", "false")
            btn.clicked.connect(lambda checked, k=key: self._switch_view(k))
            tab_lay.addWidget(btn)
            self._tab_btns[key] = btn

        lay.addWidget(tab_container)
        lay.addStretch()

        # Dark mode button
        self._dark_btn = QPushButton()
        self._dark_btn.setObjectName("dark_btn")
        self._dark_btn.setFixedSize(38, 38)
        self._dark_btn.setStyleSheet(f"QPushButton {{ padding: 0px; border-radius: 19px; background: {T['btn_bg']}; border: 1px solid {T['btn_border']}; }} QPushButton:hover {{ background: {T['btn_hover']}; }}")
        self._dark_btn.setIcon(load_icon("dark", T["icon_color"], 20))
        self._dark_btn.setIconSize(QSize(20, 20))
        self._dark_btn.clicked.connect(self._toggle_dark)
        lay.addWidget(self._dark_btn, alignment=Qt.AlignmentFlag.AlignVCenter)

        self._update_tab_style()
        return bar

    def _make_toolbar(self):
        T = self.T
        tb = QToolBar()
        tb.setMovable(False)
        tb.setIconSize(QSize(18, 18))
        tb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)

        def act(icon_name, tip, slot, text=None):
            ico = load_icon(icon_name, T["icon_color"], 18)
            if text:
                a = QAction(ico, text, self)
                tb.addAction(a)
                w = tb.widgetForAction(a)
                if w: w.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            else:
                a = QAction(ico, tip, self)
                tb.addAction(a)
            a.setToolTip(tip)
            a.triggered.connect(slot)
            return a

        def text_act(label, tip, slot, bold=False):
            a = QAction(label, self)
            a.setToolTip(tip)
            a.triggered.connect(slot)
            tb.addAction(a)
            w = tb.widgetForAction(a)
            if w and bold:
                f = w.font(); f.setBold(True); w.setFont(f)
            return a

        act("sidebar", "Toggle Sidebar (Ctrl+\\)", self._toggle_sidebar)
        tb.addSeparator()
        act("new",  "New (Ctrl+N)",  self._new)
        act("open", "Open (Ctrl+O)", self._open)
        act("save", "Save (Ctrl+S)", self._save)
        tb.addSeparator()
        act("bold",   "Bold (Ctrl+B)",   self._bold)
        act("italic", "Italic (Ctrl+I)", self._italic)
        act("strike", "Strikethrough",   self._strike)
        act("code",   "Inline Code",     self._code_inline)
        tb.addSeparator()
        text_act("H1", "Heading 1", self._h1, bold=True)
        text_act("H2", "Heading 2", self._h2)
        text_act("H3", "Heading 3", self._h3)
        tb.addSeparator()
        act("bullet",   "Bullet List",   self._bullet)
        act("numbered", "Numbered List", self._numbered)
        act("quote",    "Blockquote",    self._quote)
        tb.addSeparator()
        act("table", "Insert Table", self._ins_table)
        act("hr",    "Horizontal Rule", self._ins_hr)
        act("link",  "Insert Link",  self._ins_link)
        act("image", "Insert Image", self._ins_image)
        tb.addSeparator()
        act("find",  "Find & Replace (Ctrl+F)", self._find_replace)
        tb.addSeparator()

        # About button
        act("info", "About MarkPad", self._about)
        tb.addSeparator()

        # Font size — use QActions so they sit inline with the toolbar
        a_down = QAction("−", self)
        a_down.setToolTip("Smaller Text (Ctrl+-)")
        a_down.triggered.connect(self._font_down)
        tb.addAction(a_down)
        wd = tb.widgetForAction(a_down)
        if wd:
            wd.setFixedSize(28, 28)
            wd.setStyleSheet(f"QToolButton {{ font-size:16px; font-weight:bold; border-radius:6px; background:{T['btn_bg']}; color:{T['btn_fg']}; border:1px solid {T['btn_border']}; padding:0px; }} QToolButton:hover {{ background:{T['btn_hover']}; }}")

        self._size_lbl = QLabel(str(self.font_size))
        self._size_lbl.setFixedWidth(26)
        self._size_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._size_lbl.setStyleSheet(f"color:{T['editor_fg']}; font-weight:bold; font-size:13px; background:transparent;")
        tb.addWidget(self._size_lbl)

        a_up = QAction("+", self)
        a_up.setToolTip("Larger Text (Ctrl+=)")
        a_up.triggered.connect(self._font_up)
        tb.addAction(a_up)
        wu = tb.widgetForAction(a_up)
        if wu:
            wu.setFixedSize(28, 28)
            wu.setStyleSheet(f"QToolButton {{ font-size:16px; font-weight:bold; border-radius:6px; background:{T['btn_bg']}; color:{T['btn_fg']}; border:1px solid {T['btn_border']}; padding:0px; }} QToolButton:hover {{ background:{T['btn_hover']}; }}")

        return tb


    def _make_content(self):
        # Clear existing content
        while self._content_lay.count():
            item = self._content_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        T = self.T

        if self.view_mode == "split":
            splitter = QSplitter(Qt.Orientation.Horizontal)
            splitter.setHandleWidth(1)

            left  = self._make_editor_panel()
            right = self._make_preview_panel()
            splitter.addWidget(left)
            splitter.addWidget(right)
            splitter.setSizes([600, 600])
            self._content_lay.addWidget(splitter)

        elif self.view_mode == "edit":
            self._content_lay.addWidget(self._make_editor_panel())

        else:  # preview
            self._content_lay.addWidget(self._make_preview_panel())

    def _make_editor_panel(self):
        T = self.T
        panel = QWidget()
        panel.setStyleSheet(f"background:{T['editor_bg']};")
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        if self.view_mode == "split":
            lbl = QLabel("EDITOR"); lbl.setObjectName("section_label")
            lay.addWidget(lbl)

        # Editor + line numbers side by side
        edit_row = QHBoxLayout()
        edit_row.setContentsMargins(0, 0, 0, 0)
        edit_row.setSpacing(0)

        self.lnums = QTextEdit()
        self.lnums.setObjectName("lnums")
        self.lnums.setReadOnly(True)
        self.lnums.setFixedWidth(52)
        self.lnums.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.lnums.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.lnums.setFont(QFont("Menlo", self.font_size - 2))
        self.lnums.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.editor = QTextEdit()
        self.editor.setObjectName("editor")
        self.editor.setFont(QFont("Menlo", self.font_size))
        self.editor.setAcceptRichText(False)
        self.editor.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.editor.textChanged.connect(self._on_text_changed)
        self.editor.verticalScrollBar().valueChanged.connect(self._sync_lnums)

        edit_row.addWidget(self.lnums)
        edit_row.addWidget(self.editor, 1)
        lay.addLayout(edit_row, 1)
        return panel

    def _make_preview_panel(self):
        T = self.T
        panel = QWidget()
        panel.setStyleSheet(f"background:{T['preview_bg']};")
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        if self.view_mode == "split":
            lbl = QLabel("PREVIEW"); lbl.setObjectName("section_label")
            lay.addWidget(lbl)

        if HAS_WEBENGINE:
            self.preview = QWebEngineView()
            self.preview.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        else:
            # Fallback: plain QTextEdit in read-only mode
            self.preview = QTextEdit()
            self.preview.setReadOnly(True)
            self.preview.setObjectName("editor")
            self.preview.setStyleSheet(f"background:{T['preview_bg']}; color:{T['editor_fg']}; border:none; padding:28px 36px;")
        lay.addWidget(self.preview, 1)
        return panel

    # ── Menus ──────────────────────────────────────────────────────────
    def _setup_menus(self):
        mb = self.menuBar()

        fm = mb.addMenu("File")
        self._add_action(fm, "New",          self._new,         "Ctrl+N")
        self._add_action(fm, "Open…",        self._open,        "Ctrl+O")
        fm.addSeparator()
        self._add_action(fm, "Save",         self._save,        "Ctrl+S")
        self._add_action(fm, "Save As…",     self._save_as,     "Ctrl+Shift+S")
        fm.addSeparator()
        self._add_action(fm, "Export HTML…", self._export_html)
        self._add_action(fm, "Export PDF…",  self._export_pdf)

        em = mb.addMenu("Edit")
        self._add_action(em, "Undo",         self.editor.undo,  "Ctrl+Z")
        self._add_action(em, "Redo",         self.editor.redo,  "Ctrl+Y")
        em.addSeparator()
        self._add_action(em, "Find & Replace…", self._find_replace, "Ctrl+F")
        em.addSeparator()
        self._add_action(em, "Bold",         self._bold,        "Ctrl+B")
        self._add_action(em, "Italic",       self._italic,      "Ctrl+I")

        vm = mb.addMenu("View")
        self._add_action(vm, "Command Palette", self._show_palette, "Ctrl+P")
        vm.addSeparator()
        self._add_action(vm, "Edit Only",    lambda: self._switch_view("edit"))
        self._add_action(vm, "Split View",   lambda: self._switch_view("split"))
        self._add_action(vm, "Preview Only", lambda: self._switch_view("preview"))
        vm.addSeparator()
        self._add_action(vm, "Toggle Dark Mode", self._toggle_dark)
        vm.addSeparator()
        self._add_action(vm, "Larger Text",  self._font_up,   "Ctrl+=")
        self._add_action(vm, "Smaller Text", self._font_down, "Ctrl+-")
        
        hm = mb.addMenu("Help")
        self._add_action(hm, "About MarkPad", self._about)

        gm = mb.addMenu("Graph")
        self._add_action(gm, "Show Local Graph View", self._show_graph_view, "Ctrl+G")

    def _add_action(self, menu, label, slot, shortcut=None):
        a = QAction(label, self)
        if shortcut:
            a.setShortcut(QKeySequence(shortcut))
        a.triggered.connect(slot)
        menu.addAction(a)
        return a

    # ── Tab switching ──────────────────────────────────────────────────
    def _switch_view(self, mode: str):
        # Cancel any pending preview update before destroying widgets
        self._preview_timer.stop()

        content = self._get_document_text()
        # Delete old widget refs so hasattr checks work cleanly
        for attr in ('editor', 'lnums', 'preview'):
            if hasattr(self, attr):
                delattr(self, attr)

        self.view_mode = mode
        self._update_tab_style()
        self._make_content()

        if hasattr(self, 'editor') and content is not None:
            self.editor.blockSignals(True)
            self.editor.setPlainText(content)
            self.editor.blockSignals(False)
            self._update_lnums()
        if hasattr(self, 'preview'):
            self._update_preview()

    def _update_tab_style(self):
        for key, btn in self._tab_btns.items():
            active = "true" if key == self.view_mode else "false"
            btn.setProperty("active", active)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _get_document_text(self):
        if hasattr(self, 'editor'):
            try:
                return self.editor.toPlainText()
            except RuntimeError:
                pass
        return self._document_text

    def _on_text_changed(self):
        self.modified = True
        try:
            self._document_text = self.editor.toPlainText()
        except RuntimeError:
            pass
        self._update_lnums()
        self._update_status()
        self._preview_timer.start(300)

    def _update_lnums(self):
        if not hasattr(self, 'lnums') or not hasattr(self, 'editor'):
            return
        try:
            n = self.editor.document().blockCount()
            self.lnums.setPlainText("\n".join(str(i) for i in range(1, n + 1)))
            self._sync_lnums()
        except RuntimeError:
            pass

    def _sync_lnums(self):
        if not hasattr(self, 'lnums') or not hasattr(self, 'editor'):
            return
        try:
            val = self.editor.verticalScrollBar().value()
            self.lnums.verticalScrollBar().setValue(val)
        except RuntimeError:
            pass

    def _update_status(self):
        if not hasattr(self, '_stat_left'):
            return
        try:
            txt   = self.editor.toPlainText() if hasattr(self, 'editor') else ""
            words = len(txt.split()) if txt.strip() else 0
            chars = len(txt)
            mod   = " •" if self.modified else ""
            fname = os.path.basename(self.current_file) if self.current_file else "Untitled.md"
            self._stat_left.setText(f"{fname}{mod}")
            if hasattr(self, 'editor'):
                cursor = self.editor.textCursor()
                ln  = cursor.blockNumber() + 1
                col = cursor.columnNumber() + 1
                self._stat_right.setText(f"{words} words · {chars} chars · Ln {ln} Col {col}")
            if hasattr(self, '_fname_lbl'):
                self._fname_lbl.setText(f"{fname}{mod}")
        except RuntimeError:
            pass

    def _update_preview(self):
        if not hasattr(self, 'preview'):
            return
        text = self._get_document_text() or ""
        html = build_preview_html(text, self.T, self.font_size)
        try:
            self.preview.setHtml(html)
        except RuntimeError:
            pass


    # ── Formatting helpers ─────────────────────────────────────────────
    def _wrap(self, before, after=None):
        after = after or before
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            sel = cursor.selectedText()
            cursor.insertText(f"{before}{sel}{after}")
        else:
            pos = cursor.position()
            cursor.insertText(f"{before}{after}")
            cursor.setPosition(pos + len(before))
            self.editor.setTextCursor(cursor)

    def _prefix(self, pre):
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        if cursor.hasSelection():
            start = cursor.selectionStart()
            end   = cursor.selectionEnd()
            cursor.setPosition(start)
            cursor.movePosition(cursor.MoveOperation.StartOfBlock)
            while cursor.position() <= end:
                cursor.insertText(pre)
                end += len(pre)
                if not cursor.movePosition(cursor.MoveOperation.NextBlock):
                    break
        else:
            cursor.movePosition(cursor.MoveOperation.StartOfBlock)
            cursor.insertText(pre)
        cursor.endEditBlock()

    def _bold(self):        self._wrap("**")
    def _italic(self):      self._wrap("*")
    def _strike(self):      self._wrap("~~")
    def _code_inline(self): self._wrap("`")
    def _h1(self):          self._prefix("# ")
    def _h2(self):          self._prefix("## ")
    def _h3(self):          self._prefix("### ")
    def _bullet(self):      self._prefix("- ")
    def _numbered(self):    self._prefix("1. ")
    def _quote(self):       self._prefix("> ")

    def _ins_table(self):
        self.editor.insertPlainText(
            "\n| Column 1 | Column 2 | Column 3 |\n"
            "|----------|----------|----------|\n"
            "| Data     | Data     | Data     |\n"
            "| Data     | Data     | Data     |\n\n")

    def _ins_hr(self):
        self.editor.insertPlainText("\n\n---\n\n")

    def _ins_link(self):
        cursor = self.editor.textCursor()
        sel    = cursor.selectedText() or "Link Text"
        url, ok = QInputDialog.getText(self, "Insert Link", "URL:", text="https://")
        if ok and url:
            cursor.insertText(f"[{sel}]({url})")

    def _ins_image(self):
        dlg = ImageDialog(self, self.T)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.result_text:
            self.editor.insertPlainText("\n" + dlg.result_text + "\n")

    # ── Font size ──────────────────────────────────────────────────────
    def _font_up(self):
        if self.font_size < 30:
            self.font_size += 1
            self._apply_font()

    def _font_down(self):
        if self.font_size > 8:
            self.font_size -= 1
            self._apply_font()

    def _apply_font(self):
        if hasattr(self, 'editor'):
            self.editor.setFont(QFont("Menlo", self.font_size))
        if hasattr(self, 'lnums'):
            self.lnums.setFont(QFont("Menlo", self.font_size - 2))
        if hasattr(self, '_size_lbl'):
            self._size_lbl.setText(str(self.font_size))
        self._update_preview()

    # ── Sidebar & Command Palette ──────────────────────────────────────
    def _toggle_sidebar(self):
        self.sidebar.setVisible(not self.sidebar.isVisible())

    def _open_from_tree(self, index):
        if not self.file_model.isDir(index):
            path = self.file_model.filePath(index)
            self._load_file(path)

    def _show_palette(self):
        commands = [
            ("New File", self._new),
            ("Open File", self._open),
            ("Save File", self._save),
            ("Toggle Dark Mode", self._toggle_dark),
            ("Toggle Sidebar", self._toggle_sidebar),
            ("Find & Replace", self._find_replace),
            ("Insert Table", self._ins_table),
            ("Insert Image", self._ins_image),
            ("Export to PDF", self._export_pdf),
            ("Export to HTML", self._export_html),
            ("View: Split", lambda: self._switch_view("split")),
            ("View: Edit", lambda: self._switch_view("edit")),
            ("View: Preview", lambda: self._switch_view("preview")),
            ("Local Graph View", self._show_graph_view),
            ("About MarkPad", self._about),
        ]
        dlg = CommandPalette(self, self.T, commands)
        dlg.exec()

    # ── File ops ───────────────────────────────────────────────────────
    def _load_file(self, path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.editor.setPlainText(content)
        self.current_file = path
        self.modified = False
        self._update_lnums()
        self._update_status()
        self._update_preview()

    def _new(self):
        if self.modified:
            r = QMessageBox.question(self, "Unsaved Changes",
                "Discard changes and start new file?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if r != QMessageBox.StandardButton.Yes:
                return
        self.editor.setPlainText("")
        self.current_file = None
        self.modified = False
        self._update_status()
        self._update_preview()

    def _open(self):
        p, _ = QFileDialog.getOpenFileName(
            self, "Open Markdown File", "",
            "Markdown (*.md *.markdown *.txt);;All Files (*)")
        if p:
            self._load_file(p)

    def _save(self):
        if self.current_file:
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(self.editor.toPlainText())
            self.modified = False
            self._update_status()
        else:
            self._save_as()

    def _save_as(self):
        p, _ = QFileDialog.getSaveFileName(
            self, "Save As", "", "Markdown (*.md);;All Files (*)")
        if p:
            self.current_file = p
            self._save()

    def _export_html(self):
        html = build_preview_html(self.editor.toPlainText(), self.T, self.font_size)
        p, _ = QFileDialog.getSaveFileName(
            self, "Export as HTML", "", "HTML (*.html)")
        if p:
            with open(p, "w", encoding="utf-8") as f:
                f.write(html)
            QMessageBox.information(self, "Exported", f"Saved to:\n{p}")

    def _export_pdf(self):
        if not hasattr(self, 'editor'):
            return
        
        dlg = PDFExportDialog(self, self.T)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        
        style = dlg.result_style
        path = dlg.result_path
        
        # Show loading message
        loading = QMessageBox(self)
        loading.setWindowTitle("Exporting PDF")
        loading.setText("Generating PDF, please wait...")
        loading.setStandardButtons(QMessageBox.StandardButton.NoButton)
        loading.setModal(True)
        loading.show()
        QApplication.processEvents()
        
        # Generate HTML with selected style
        md_text = self.editor.toPlainText()
        if style == "github":
            html = build_preview_html(md_text, LIGHT, self.font_size)
        elif style == "ace":
            html = build_preview_html(md_text, DARK, self.font_size)
        else:  # libre
            html = build_preview_html(md_text, LIGHT, self.font_size)
        
        # Try to use QPrinter for PDF export
        try:
            from PyQt6.QtPrintSupport import QPrinter
            from PyQt6.QtWebEngineWidgets import QWebEngineView
            from PyQt6.QtCore import QUrl, QEventLoop
            from PyQt6.QtGui import QPageSize
            
            # Create temporary web view for printing
            web = QWebEngineView()
            web.setHtml(html)
            
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(path)
            printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            
            def on_pdf_finished(file_path, success):
                loading.close()
                if not success:
                    QMessageBox.warning(self, "Error", "Failed to generate PDF")
                else:
                    QMessageBox.information(self, "Success", f"PDF exported to:\n{file_path}")
                loop.quit()

            def on_load_finished(ok):
                if ok:
                    web.page().pdfPrintingFinished.connect(on_pdf_finished)
                    web.page().printToPdf(path)
                else:
                    loading.close()
                    QMessageBox.warning(self, "Error", "Failed to load HTML for PDF")
                    loop.quit()
            
            loop = QEventLoop()
            web.loadFinished.connect(on_load_finished)
            loop.exec()
            
        except (ImportError, AttributeError) as e:
            loading.close()
            # Fallback: save as HTML and inform user
            html_path = path.replace('.pdf', '.html')
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html)
            QMessageBox.information(
                self, "PDF Export", 
                f"PyQt6-WebEngine not available for PDF export.\n\n"
                f"Saved as HTML instead:\n{html_path}\n\n"
                f"You can open this in a browser and print to PDF."
            )

    # ── Find & Replace ─────────────────────────────────────────────────
    def _find_replace(self):
        if hasattr(self, 'editor'):
            dlg = FindDialog(self, self.editor, self.T)
            dlg.exec()

    # ── Local Graph View ───────────────────────────────────────────────
    def _show_graph_view(self):
        if not HAS_WEBENGINE:
            QMessageBox.warning(self, "Graph View", "Graph View requires PyQt6-WebEngine.")
            return
            
        import tempfile
        import re
        
        # Build node network
        nodes = []
        edges = []
        
        current_name = os.path.basename(self.current_file) if self.current_file else "Untitled"
        nodes.append({"id": current_name, "label": current_name, "group": "current"})
        
        # Parse links: [label](url) or [[wiki-link]]
        text = self.editor.toPlainText() if hasattr(self, 'editor') else ""
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', text)
        wiki_links = re.findall(r'\[\[(.*?)\]\]', text)
        
        connected = set()
        for label, url in links:
            if not url.startswith("http"):
                fname = os.path.basename(url)
                if fname not in connected:
                    nodes.append({"id": fname, "label": fname, "group": "linked"})
                    edges.append({"from": current_name, "to": fname})
                    connected.add(fname)
                    
        for wlink in wiki_links:
            if wlink not in connected:
                nodes.append({"id": wlink, "label": wlink, "group": "linked"})
                edges.append({"from": current_name, "to": wlink})
                connected.add(wlink)
        
        import json
        nodes_js = json.dumps(nodes)
        edges_js = json.dumps(edges)
        
        html = f"""
        <html>
        <head>
            <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
            <style>
                body {{ margin: 0; padding: 0; background: {self.T['bg']}; color: {self.T['editor_fg']}; }}
                #mynetwork {{ width: 100vw; height: 100vh; }}
            </style>
        </head>
        <body>
            <div id="mynetwork"></div>
            <script type="text/javascript">
                var nodes = new vis.DataSet({nodes_js});
                var edges = new vis.DataSet({edges_js});
                var container = document.getElementById('mynetwork');
                var data = {{ nodes: nodes, edges: edges }};
                var options = {{
                    nodes: {{
                        shape: 'dot',
                        size: 20,
                        font: {{ size: 14, color: '{self.T['editor_fg']}' }}
                    }},
                    edges: {{
                        color: '{self.T['border']}',
                        arrows: 'to'
                    }},
                    groups: {{
                        current: {{ color: '{self.T['accent']}' }},
                        linked: {{ color: '#888888' }}
                    }},
                    physics: {{ stabilization: false, barnesHut: {{ springLength: 150 }} }}
                }};
                var network = new vis.Network(container, data, options);
            </script>
        </body>
        </html>
        """
        
        dlg = QDialog(self)
        dlg.setWindowTitle("Local Graph View")
        dlg.setFixedSize(800, 600)
        dlg_lay = QVBoxLayout(dlg)
        dlg_lay.setContentsMargins(0, 0, 0, 0)
        web = QWebEngineView()
        web.setHtml(html)
        dlg_lay.addWidget(web)
        dlg.exec()

    # ── About ──────────────────────────────────────────────────────────
    def _about(self):
        QMessageBox.about(
            self,
            "About MarkPad",
            "<h3>MarkPad Markdown Editor</h3>"
            "<p>A clean, macOS-style Markdown editor.</p>"
            "<p><b>Developed by:</b> This Person</p>"
            "<p><b>GitHub:</b> <a href='https://github.com/thisperson'>https://github.com/thisperson</a></p>"
        )

    # ── Dark mode ──────────────────────────────────────────────────────
    def _toggle_dark(self):
        content = self.editor.toPlainText() if hasattr(self, 'editor') else ""
        self.is_dark = not self.is_dark
        self.T = DARK if self.is_dark else LIGHT
        self.setStyleSheet(build_stylesheet(self.T))

        # Rebuild title bar and toolbar for new icon colors
        old_title = self._title_bar
        old_tb    = self._toolbar

        self._title_bar = self._make_titlebar()
        self._toolbar   = self._make_toolbar()

        root_lay = self.centralWidget().layout()
        root_lay.insertWidget(0, self._title_bar)
        root_lay.insertWidget(1, self._toolbar)
        old_title.deleteLater()
        old_tb.deleteLater()

        self._make_content()
        if hasattr(self, 'editor'):
            self.editor.setPlainText(content)
            self._update_lnums()
        if hasattr(self, 'preview'):
            self._update_preview()
        self._update_status()


# ── Entry ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("MarkPad")
    app.setStyle("Fusion")
    window = MarkPad()
    window.show()
    sys.exit(app.exec())
