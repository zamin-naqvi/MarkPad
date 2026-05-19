"""
How to Use MarkPad dialog.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QStackedWidget, QWidget, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap
import os

class HowToUseDialog(QDialog):
    """Interactive guide on how to use MarkPad."""
    
    def __init__(self, parent, theme):
        super().__init__(parent)
        self.T = theme
        self.setWindowTitle("How to Use MarkPad")
        self.setFixedSize(800, 600)
        self.setStyleSheet(f"""
            QDialog {{ background: {theme['bg']}; color: {theme['editor_fg']}; }}
            QLabel {{ color: {theme['editor_fg']}; }}
            QPushButton {{ 
                background: {theme['btn_bg']}; color: {theme['btn_fg']};
                border: 1px solid {theme['btn_border']}; border-radius: 6px; padding: 6px 12px;
            }}
            QPushButton:hover {{ background: {theme['btn_hover']}; }}
            QPushButton:disabled {{ opacity: 0.5; }}
        """)

        self.pages = [
            {
                "title": "Welcome to MarkPad ✍️",
                "content": "MarkPad is a blazing-fast Markdown editor with an instant live preview.<br><br><b>Key Features:</b><ul><li>Zero-delay live preview</li><li>Syntax highlighting</li><li>Interactive graph view</li><li>Focus & Zen modes</li></ul>",
                "image": "icons/app_icon.png"
            },
            {
                "title": "Editing Modes 👁️",
                "content": "You can switch between different viewing modes using the tab bar at the top or the <b>View</b> menu.<br><br><ul><li><b>Split View:</b> Edit side-by-side with preview.</li><li><b>Edit Only:</b> Focus only on your Markdown.</li><li><b>Preview Only:</b> View the rendered document.</li><li><b>Mind Map:</b> Visualize your headings as a mind map.</li></ul>",
                "image": "split.png"
            },
            {
                "title": "Command Palette ⌨️",
                "content": "Press <b>Ctrl+P</b> to open the Command Palette.<br><br>It provides quick access to all actions, such as saving, finding text, changing themes, and inserting snippets without needing to touch the mouse.",
                "image": "command_palette.png"
            },
            {
                "title": "Mind Map Editor 🧠",
                "content": "Switch to the <b>Mind Map Editor</b> tab to visually brainstorm.<br><br>Double-click a node to edit its text. Hover over a node to reveal add/delete buttons. Drag nodes to rearrange them. You can save your mind map as a Markdown document when you're done!",
                "image": "mindmap_editor.png"
            },
            {
                "title": "Focus & Zen Modes 🧘",
                "content": "Minimize distractions while writing:<br><br><ul><li><b>Focus Mode (Ctrl+/):</b> Dims all paragraphs except the one you are actively editing.</li><li><b>Zen Mode (F11):</b> Hides all toolbars and sidebars, putting the editor in full screen.</li><li><b>Typewriter Mode (Ctrl+T):</b> Keeps the cursor vertically centered on the screen.</li></ul>",
                "image": ""
            }
        ]
        
        self.current_page = 0
        
        self._build_ui()
        self._update_page()
        
    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Content Area
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack, 1)
        
        for page_data in self.pages:
            page_widget = QWidget()
            page_layout = QVBoxLayout(page_widget)
            
            title = QLabel(page_data["title"])
            title_font = QFont("Segoe UI", 24, QFont.Weight.Bold)
            title.setFont(title_font)
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            page_layout.addWidget(title)
            
            if page_data["image"]:
                img_lbl = QLabel()
                img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                pixmap = QPixmap(page_data["image"])
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(500, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    img_lbl.setPixmap(scaled_pixmap)
                page_layout.addWidget(img_lbl)
            else:
                page_layout.addSpacing(100)
            
            content = QLabel(page_data["content"])
            content.setWordWrap(True)
            content_font = QFont("Segoe UI", 12)
            content.setFont(content_font)
            content.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            page_layout.addWidget(content, 1)
            
            self.stack.addWidget(page_widget)
            
        # Navigation Footer
        nav_layout = QHBoxLayout()
        
        self.btn_prev = QPushButton("Previous")
        self.btn_prev.clicked.connect(self._prev_page)
        nav_layout.addWidget(self.btn_prev)
        
        nav_layout.addStretch()
        
        self.lbl_progress = QLabel()
        nav_layout.addWidget(self.lbl_progress)
        
        nav_layout.addStretch()
        
        self.btn_next = QPushButton("Next")
        self.btn_next.clicked.connect(self._next_page)
        nav_layout.addWidget(self.btn_next)
        
        self.btn_close = QPushButton("Get Started")
        self.btn_close.clicked.connect(self.accept)
        self.btn_close.hide()
        nav_layout.addWidget(self.btn_close)
        
        main_layout.addLayout(nav_layout)
        
    def _update_page(self):
        self.stack.setCurrentIndex(self.current_page)
        self.lbl_progress.setText(f"{self.current_page + 1} / {len(self.pages)}")
        
        self.btn_prev.setEnabled(self.current_page > 0)
        
        if self.current_page == len(self.pages) - 1:
            self.btn_next.hide()
            self.btn_close.show()
        else:
            self.btn_next.show()
            self.btn_close.hide()
            
    def _next_page(self):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self._update_page()
            
    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._update_page()

def show_how_to_use(parent, theme):
    dialog = HowToUseDialog(parent, theme)
    dialog.exec()
