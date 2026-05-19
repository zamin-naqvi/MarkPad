"""Preview panel with instant rendering."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
from PyQt6.QtCore import Qt, QUrl

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEngineSettings
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False

from markpad.core.engine import build_preview_html, get_engine


class PreviewPanel(QWidget):
    """Preview panel using WebEngine or fallback QTextEdit."""

    def __init__(self, theme: dict, show_label: bool = True):
        super().__init__()
        self.T = theme
        self._engine = get_engine()
        self._last_html = ""
        self._last_base_url = ""
        self._use_incremental = True
        self.setStyleSheet(f"background:{theme['preview_bg']};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        if show_label:
            lbl = QLabel("PREVIEW")
            lbl.setObjectName("section_label")
            lay.addWidget(lbl)

        if HAS_WEBENGINE:
            self.web = QWebEngineView()
            self.web.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
            
            # Enable local file access for images
            settings = self.web.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
            
            lay.addWidget(self.web, 1)
        else:
            self.web = QTextEdit()
            self.web.setReadOnly(True)
            self.web.setObjectName("editor")
            self.web.setStyleSheet(
                f"background:{theme['preview_bg']}; color:{theme['editor_fg']}; "
                f"border:none; padding:28px 36px;"
            )
            lay.addWidget(self.web, 1)

    def update_preview(self, md_text: str, font_size: int = 15, base_url: str = ""):
        """Update preview - uses incremental JS update when possible."""
        import os
        if not base_url:
            base_url = os.getcwd() + "/"

        # Convert windows paths to file:// urls for base
        base_qurl = QUrl.fromLocalFile(base_url)

        html = build_preview_html(md_text, self.T, font_size, self._engine)

        if HAS_WEBENGINE:
            if self._use_incremental and self._last_html and self._last_base_url == base_url:
                # Use JavaScript DOM update to preserve scroll position
                body = self._engine.render_full(md_text)
                escaped = body.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
                js = f"if(window.markpadUpdate){{window.markpadUpdate(`{escaped}`);}}"
                try:
                    self.web.page().runJavaScript(js)
                    self._last_html = html
                    return
                except Exception:
                    pass
            # Full page load for first render or if base URL changed
            self.web.setHtml(html, base_qurl)
            self._last_html = html
            self._last_base_url = base_url
        else:
            try:
                self.web.setHtml(html)
            except (RuntimeError, AttributeError):
                pass

    def force_full_reload(self, md_text: str, font_size: int = 15):
        """Force a full page reload (used after theme change)."""
        self._last_html = ""
        self._use_incremental = False
        self.update_preview(md_text, font_size)
        self._use_incremental = True
