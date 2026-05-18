"""
QSS stylesheet builder for MarkPad UI.
"""


def build_stylesheet(T: dict) -> str:
    """Build a complete Qt stylesheet from a theme dictionary."""
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
        font-family: "Segoe UI", "Helvetica Neue", Arial;
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
        font-family: "Segoe UI", "Helvetica Neue", Arial;
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
        font-family: "Cascadia Code", "Consolas", monospace;
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
        font-family: "Cascadia Code", "Consolas", monospace;
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
    }}
    /* ── TOC panel ── */
    QListWidget#toc_list {{
        background: transparent;
        border: none;
        color: {T["editor_fg"]};
        font-size: 13px;
        outline: none;
    }}
    QListWidget#toc_list::item {{
        padding: 4px 8px;
        border-radius: 4px;
    }}
    QListWidget#toc_list::item:hover {{
        background: {bh};
    }}
    QListWidget#toc_list::item:selected {{
        background: {a};
        color: {af};
    }}
    /* ── Focus mode overlay ── */
    QWidget#focus_overlay {{
        background: transparent;
    }}"""
