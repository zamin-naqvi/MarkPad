import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False

class MindMapPanel(QWidget):
    """Panel displaying a beautiful Mind Map generated from Markdown using Markmap."""

    def __init__(self, theme: dict, show_label: bool = True):
        super().__init__()
        self.T = theme
        self.setStyleSheet(f"background:{theme['preview_bg']};")
        
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        if show_label:
            lbl = QLabel("MIND MAP")
            lbl.setObjectName("section_label")
            lay.addWidget(lbl)

        if HAS_WEBENGINE:
            self.web = QWebEngineView()
            self.web.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
            lay.addWidget(self.web, 1)
        else:
            lbl = QLabel("QWebEngineView is required for the Mind Map.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lay.addWidget(lbl, 1)

    def update_map(self, md_text: str):
        if not HAS_WEBENGINE:
            return
            
        dot_color = "#48484a" if self.T == "dark" else "#d1d1d6"
        bg_color = self.T["preview_bg"]
        
        # Escape markdown properly for JS template literal
        safe_md = md_text.replace('`', '\\`').replace('$', '\\$').replace('\\', '\\\\')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body, html {{ 
                    margin: 0; padding: 0; width: 100%; height: 100%; 
                    background-color: {bg_color};
                    background-image: radial-gradient({dot_color} 1px, transparent 1px);
                    background-size: 20px 20px;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                }}
                .markmap-container {{ width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; }}
                .markmap {{ width: 100%; height: 100%; }}
            </style>
        </head>
        <body>
            <div class="markmap-container">
                <div class="markmap">
                    <script type="text/template">
{md_text}
                    </script>
                </div>
            </div>
            <script src="https://cdn.jsdelivr.net/npm/markmap-autoloader@0.17"></script>
        </body>
        </html>
        """
        self.web.setHtml(html)
