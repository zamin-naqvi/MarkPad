import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, QSize
from markpad.utils.icons import load_icon

class TabSwitcherDialog(QDialog):
    """A gorgeous multi-tab switcher interface."""
    
    def __init__(self, parent, tabs_data, current_idx, T):
        super().__init__(parent)
        self.main_window = parent
        self.tabs_data = tabs_data
        self.current_idx = current_idx
        self.T = T
        
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(300, 380)
        
        self.setStyleSheet(f"""
            QDialog {{ background: {T['bg']}; border: 1px solid {T['border']}; border-radius: 8px; }}
            QScrollArea {{ border: none; background: transparent; }}
            QWidget#scroll_content {{ background: transparent; }}
        """)
        
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(8, 8, 8, 8)
        self.lay.setSpacing(6)
        
        title_lay = QHBoxLayout()
        lbl = QLabel("OPEN TABS")
        lbl.setStyleSheet(f"color: {T['status_fg']}; font-weight: bold; font-size: 11px; padding: 4px;")
        title_lay.addWidget(lbl)
        
        new_btn = QPushButton("+ New Note")
        new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_btn.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {T['accent']}; font-weight: bold; font-size: 11px; border: none; }}
            QPushButton:hover {{ text-decoration: underline; }}
        """)
        new_btn.clicked.connect(self._on_new_tab)
        title_lay.addWidget(new_btn, 0, Qt.AlignmentFlag.AlignRight)
        
        self.lay.addLayout(title_lay)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scroll_content")
        self.scroll_lay = QVBoxLayout(self.scroll_content)
        self.scroll_lay.setContentsMargins(0, 0, 0, 0)
        self.scroll_lay.setSpacing(4)
        self.scroll_lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        self.lay.addWidget(self.scroll)
        
        self._build_list()
        
        # Position below the button
        if hasattr(self.main_window, "_tab_switch_btn"):
            btn = self.main_window._tab_switch_btn
            pos = btn.mapToGlobal(btn.rect().bottomLeft())
            # Align right edge of popup with right edge of button roughly
            self.move(pos.x() - 250, pos.y() + 8)

    def _build_list(self):
        # Clear layout
        while self.scroll_lay.count():
            item = self.scroll_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        for i, tab in enumerate(self.tabs_data):
            self._add_tab_item(i, tab)
            
    def _add_tab_item(self, idx, tab):
        item_w = QWidget()
        item_w.setCursor(Qt.CursorShape.PointingHandCursor)
        
        bg_color = self.T['accent'] if idx == self.current_idx else "transparent"
        fg_color = self.T['accent_fg'] if idx == self.current_idx else self.T['editor_fg']
        hover_bg = self.T['accent'] if idx == self.current_idx else self.T['btn_hover']
        
        item_w.setStyleSheet(f"""
            QWidget {{ background: {bg_color}; border-radius: 6px; }}
            QWidget:hover {{ background: {hover_bg}; }}
        """)
        
        lay = QHBoxLayout(item_w)
        lay.setContentsMargins(12, 8, 8, 8)
        
        name = os.path.basename(tab["path"]) if tab["path"] else "Untitled.md"
        if tab["modified"]:
            name += " *"
            
        lbl = QLabel(name)
        lbl.setStyleSheet(f"color: {fg_color}; font-size: 13px; font-weight: {'bold' if idx == self.current_idx else 'normal'}; background: transparent;")
        lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        lay.addWidget(lbl, 1)
        
        # Close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: none; font-weight: bold; font-size: 16px; color: {fg_color}; padding-bottom: 2px; }}
            QPushButton:hover {{ color: #ef4444; }}
        """)
        close_btn.clicked.connect(lambda checked, i=idx: self._on_close_clicked(i))
        lay.addWidget(close_btn)
        
        # Click event for the row
        item_w.mousePressEvent = lambda e, i=idx: self._on_row_clicked(i)
        
        self.scroll_lay.addWidget(item_w)

    def _on_row_clicked(self, idx):
        if idx != self.current_idx:
            # We can animate here if we want by calling a method on main_window
            self.main_window._on_tab_changed(idx)
        self.accept()

    def _on_close_clicked(self, idx):
        self.main_window._on_tab_closed(idx)
        if len(self.tabs_data) == 0:
            self.accept()
        else:
            self.current_idx = self.main_window.current_tab_idx
            self._build_list()
            
    def _on_new_tab(self):
        self.main_window._new()
        self.accept()
