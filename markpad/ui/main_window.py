"""MarkPad Main Window."""
import sys, os, re

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter, QTextEdit, QToolBar,
    QStatusBar, QFileDialog, QMessageBox, QInputDialog, QDialog,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame,
    QSizePolicy, QTreeView, QListWidget, QListWidgetItem, QMenu, QTabBar
)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal, QPropertyAnimation
from PyQt6.QtGui import (
    QFileSystemModel, QIcon, QFont, QKeySequence, QAction, QColor,
)
from PyQt6.QtWidgets import QGraphicsOpacityEffect

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False

from markpad.themes.theme_data import LIGHT, DARK, SAMPLE_DOCUMENT
from markpad.themes.stylesheet import build_stylesheet
from markpad.utils.icons import load_icon, load_app_icon
from markpad.utils.helpers import word_count, char_count, reading_time, SNIPPET_TEMPLATES
from markpad.core.engine import build_preview_html, get_engine
from markpad.core.document import Document, RecentFiles
from markpad.core.settings import Settings
from markpad.ui.editor import EditorPanel
from markpad.ui.preview import PreviewPanel
from markpad.dialogs.find_replace import FindDialog
from markpad.dialogs.image_insert import ImageDialog
from markpad.dialogs.pdf_export import PDFExportDialog
from markpad.dialogs.command_palette import CommandPalette
from markpad.dialogs.about import show_about
from markpad.dialogs.how_to_use import show_how_to_use


class MarkPad(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MarkPad")
        self.resize(1280, 820)
        self.setMinimumSize(860, 600)
        self.setWindowIcon(load_app_icon())

        self.settings = Settings()
        self.is_dark = self.settings.get("theme") == "dark"
        self.T = DARK if self.is_dark else LIGHT
        self.current_file = None
        self.modified = False
        self.view_mode = "split"
        self.font_size = self.settings.get("font_size", 15)
        
        # Multi-tab state
        # A tab is: {"path": str/None, "text": str, "modified": bool, "cursor": int, "scroll": int}
        self.tabs_data = []
        self.current_tab_idx = -1
        
        self._focus_mode = False
        self._zen_mode = False
        self._engine = get_engine()
        self._recent = RecentFiles(os.path.join(self.settings.config_dir, "recent.json"))

        # Preview timer - ultra-fast (10ms debounce for typing bursts)
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(10)
        self._preview_timer.timeout.connect(self._update_preview)

        # Autosave timer
        self._autosave_timer = QTimer(self)
        self._autosave_timer.setInterval(30000)
        self._autosave_timer.timeout.connect(self._autosave)
        if self.settings.get("autosave_enabled", True):
            self._autosave_timer.start()

        self._build()
        self._add_tab(SAMPLE_DOCUMENT, None)
        self._update_status()

    def _build(self):
        T = self.T
        self.setStyleSheet(build_stylesheet(T))
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._title_bar = self._make_titlebar()
        root.addWidget(self._title_bar)
        self._toolbar = self._make_toolbar()
        root.addWidget(self._toolbar)

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(self.main_splitter, 1)

        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setStyleSheet(f"background:{T['toolbar_bg']};")
        sb_lay = QVBoxLayout(self.sidebar)
        sb_lay.setContentsMargins(0, 0, 0, 0)
        sb_lay.setSpacing(0)
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("")
        self.file_model.setNameFilters(["*.md", "*.txt", "*.markdown"])
        self.file_model.setNameFilterDisables(False)
        self.tree = QTreeView()
        self.tree.setModel(self.file_model)
        self.tree.setRootIndex(self.file_model.index(os.getcwd()))
        self.tree.setHeaderHidden(True)
        self.tree.setStyleSheet(
            f"QTreeView{{background:transparent;border:none;color:{T['editor_fg']};}}"
            f"QTreeView::item{{padding:4px;}}"
            f"QTreeView::item:selected{{background:{T['accent']};color:{T['accent_fg']};}}"
        )
        for i in range(1, 4):
            self.tree.hideColumn(i)
        self.tree.doubleClicked.connect(self._open_from_tree)
        lbl = QLabel("VAULT")
        lbl.setObjectName("section_label")
        sb_lay.addWidget(lbl)
        sb_lay.addWidget(self.tree)
        self.main_splitter.addWidget(self.sidebar)

        # Content area
        self._content_widget = QWidget()
        self._content_lay = QVBoxLayout(self._content_widget)
        self._content_lay.setContentsMargins(0, 0, 0, 0)
        self._content_lay.setSpacing(0)
        self.main_splitter.addWidget(self._content_widget)
        self.main_splitter.setSizes([200, 1000])
        self.sidebar.hide()
        
        # Setup opacity effect for tab transition animations
        self._content_opacity = QGraphicsOpacityEffect(self._content_widget)
        self._content_widget.setGraphicsEffect(self._content_opacity)
        self._anim = QPropertyAnimation(self._content_opacity, b"opacity")
        self._anim.setDuration(150)

        self._build_content()

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._stat_left = QLabel("")
        self._stat_right = QLabel("")
        self.status_bar.addWidget(self._stat_left)
        self.status_bar.addPermanentWidget(self._stat_right)
        self._setup_menus()

    # ── PLACEHOLDER METHODS (filled in via append) ──
    def _make_titlebar(self):
        """Build title bar with tabs and dark mode toggle."""
        T = self.T
        bar = QWidget()
        bar.setObjectName("titlebar")
        bar.setFixedHeight(52)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self._fname_lbl = QLabel("Untitled.md")
        self._fname_lbl.setObjectName("filename_label")
        lay.addWidget(self._fname_lbl)
        lay.addStretch()

        tab_container = QWidget()
        tab_container.setObjectName("tab_container")
        tab_container.setFixedHeight(42)
        tab_lay = QHBoxLayout(tab_container)
        tab_lay.setContentsMargins(5, 5, 5, 5)
        tab_lay.setSpacing(3)
        self._tab_btns = {}
        for key, label in [("edit", "Edit"), ("split", "Split"), ("preview", "Preview"), ("mind_map", "Mind Map"), ("mm_editor", "Mind Map Editor")]:
            btn = QPushButton(label)
            btn.setObjectName("tab_btn")
            btn.setProperty("active", "false")
            btn.clicked.connect(lambda c, k=key: self._switch_view(k))
            tab_lay.addWidget(btn)
            self._tab_btns[key] = btn
        lay.addWidget(tab_container)
        lay.addStretch()

        # Focus mode button
        self._focus_btn = QPushButton("◎")
        self._focus_btn.setToolTip("Focus Mode (Ctrl+/)")
        self._focus_btn.setFixedSize(38, 38)
        self._focus_btn.setStyleSheet(
            f"QPushButton{{padding:0;border-radius:19px;background:{T['btn_bg']};"
            f"border:1px solid {T['btn_border']};font-size:16px;color:{T['btn_fg']};}}"
            f"QPushButton:hover{{background:{T['btn_hover']};}}"
        )
        self._focus_btn.clicked.connect(self._toggle_focus)
        lay.addWidget(self._focus_btn)

        # Tab Switcher button
        self._tab_switch_btn = QPushButton("1")
        self._tab_switch_btn.setToolTip("Switch Tabs")
        self._tab_switch_btn.setFixedSize(38, 38)
        self._tab_switch_btn.setStyleSheet(
            f"QPushButton{{padding:0;border-radius:8px;background:{T['btn_bg']};"
            f"border:1px solid {T['btn_border']};font-size:14px;font-weight:bold;color:{T['btn_fg']};}}"
            f"QPushButton:hover{{background:{T['btn_hover']};}}"
        )
        self._tab_switch_btn.clicked.connect(self._show_tab_switcher)
        lay.addWidget(self._tab_switch_btn)

        # Dark mode button
        self._dark_btn = QPushButton()
        self._dark_btn.setFixedSize(38, 38)
        self._dark_btn.setStyleSheet(
            f"QPushButton{{padding:0;border-radius:19px;background:{T['btn_bg']};"
            f"border:1px solid {T['btn_border']};}}"
            f"QPushButton:hover{{background:{T['btn_hover']};}}"
        )
        self._dark_btn.setIcon(load_icon("dark", T["icon_color"], 20))
        self._dark_btn.setIconSize(QSize(20, 20))
        self._dark_btn.clicked.connect(self._toggle_dark)
        lay.addWidget(self._dark_btn)

        self._update_tab_style()
        return bar

    def _show_tab_switcher(self):
        from markpad.dialogs.tab_switcher import TabSwitcherDialog
        # Animate content out
        dlg = TabSwitcherDialog(self, self.tabs_data, self.current_tab_idx, self.T)
        dlg.exec()
        # Content animates back in _on_tab_changed if changed

    def _make_toolbar(self):
        T = self.T
        tb = QToolBar()
        tb.setMovable(False)
        tb.setIconSize(QSize(18, 18))
        tb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)

        def act(icon, tip, slot):
            a = QAction(load_icon(icon, T["icon_color"], 18), tip, self)
            a.setToolTip(tip)
            a.triggered.connect(slot)
            tb.addAction(a)
            return a

        def txt(label, tip, slot, bold=False):
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
        act("new", "New (Ctrl+N)", self._new)
        act("open", "Open (Ctrl+O)", self._open)
        act("save", "Save (Ctrl+S)", self._save)
        tb.addSeparator()
        act("bold", "Bold (Ctrl+B)", self._bold)
        act("italic", "Italic (Ctrl+I)", self._italic)
        act("strike", "Strikethrough", self._strike)
        act("code", "Inline Code", self._code_inline)
        tb.addSeparator()
        txt("H1", "Heading 1", self._h1, bold=True)
        txt("H2", "Heading 2", self._h2)
        txt("H3", "Heading 3", self._h3)
        tb.addSeparator()
        act("bullet", "Bullet List", self._bullet)
        act("numbered", "Numbered List", self._numbered)
        act("quote", "Blockquote", self._quote)
        tb.addSeparator()
        act("table", "Insert Table", self._ins_table)
        act("hr", "Horizontal Rule", self._ins_hr)
        act("link", "Insert Link", self._ins_link)
        act("image", "Insert Image", self._ins_image)
        tb.addSeparator()
        act("find", "Find & Replace (Ctrl+F)", self._find_replace)
        act("info", "About MarkPad", lambda: show_about(self))
        tb.addSeparator()

        # Font size controls
        a_down = QAction("−", self)
        a_down.setToolTip("Smaller (Ctrl+-)")
        a_down.triggered.connect(self._font_down)
        tb.addAction(a_down)
        wd = tb.widgetForAction(a_down)
        if wd:
            wd.setFixedSize(28, 28)
            wd.setStyleSheet(
                f"QToolButton{{font-size:16px;font-weight:bold;border-radius:6px;"
                f"background:{T['btn_bg']};color:{T['btn_fg']};"
                f"border:1px solid {T['btn_border']};padding:0;}}"
                f"QToolButton:hover{{background:{T['btn_hover']};}}"
            )
        self._size_lbl = QLabel(str(self.font_size))
        self._size_lbl.setFixedWidth(26)
        self._size_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._size_lbl.setStyleSheet(
            f"color:{T['editor_fg']};font-weight:bold;font-size:13px;background:transparent;"
        )
        tb.addWidget(self._size_lbl)
        a_up = QAction("+", self)
        a_up.setToolTip("Larger (Ctrl+=)")
        a_up.triggered.connect(self._font_up)
        tb.addAction(a_up)
        wu = tb.widgetForAction(a_up)
        if wu:
            wu.setFixedSize(28, 28)
            wu.setStyleSheet(
                f"QToolButton{{font-size:16px;font-weight:bold;border-radius:6px;"
                f"background:{T['btn_bg']};color:{T['btn_fg']};"
                f"border:1px solid {T['btn_border']};padding:0;}}"
                f"QToolButton:hover{{background:{T['btn_hover']};}}"
            )
        return tb

    def _build_content(self):
        while self._content_lay.count():
            item = self._content_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        T = self.T
        show_label = self.view_mode == "split"
        if self.view_mode == "split":
            splitter = QSplitter(Qt.Orientation.Horizontal)
            splitter.setHandleWidth(1)
            self._editor_panel = EditorPanel(T, self.font_size, show_label)
            self._editor_panel.textChanged.connect(self._on_text_changed)
            self._preview_panel = PreviewPanel(T, show_label)
            self._mind_map_panel = None
            splitter.addWidget(self._editor_panel)
            splitter.addWidget(self._preview_panel)
            splitter.setSizes([600, 600])
            self._content_lay.addWidget(splitter)
        elif self.view_mode == "edit":
            self._editor_panel = EditorPanel(T, self.font_size, False)
            self._editor_panel.textChanged.connect(self._on_text_changed)
            self._preview_panel = None
            self._mind_map_panel = None
            self._content_lay.addWidget(self._editor_panel)
        elif self.view_mode == "preview":
            self._editor_panel = None
            self._preview_panel = PreviewPanel(T, False)
            self._mind_map_panel = None
            self._content_lay.addWidget(self._preview_panel)
        elif self.view_mode == "mind_map":
            from markpad.ui.mind_map_view import MindMapPanel
            self._editor_panel = None
            self._preview_panel = None
            self._mind_map_panel = MindMapPanel(T, False)
            self._content_lay.addWidget(self._mind_map_panel)
        elif self.view_mode == "mm_editor":
            from markpad.ui.mind_map_editor import MindMapEditorPanel
            self._editor_panel = None
            self._preview_panel = None
            self._mind_map_panel = MindMapEditorPanel(T)
            self._content_lay.addWidget(self._mind_map_panel)

    # ── Menus ──
    def _setup_menus(self):
        mb = self.menuBar()
        fm = mb.addMenu("File")
        self._add_action(fm, "New", self._new, "Ctrl+N")
        self._add_action(fm, "Open…", self._open, "Ctrl+O")
        fm.addSeparator()
        self._add_action(fm, "Save", self._save, "Ctrl+S")
        self._add_action(fm, "Save As…", self._save_as, "Ctrl+Shift+S")
        fm.addSeparator()
        # Recent files submenu
        self._recent_menu = fm.addMenu("Recent Files")
        self._rebuild_recent_menu()
        fm.addSeparator()
        self._add_action(fm, "Export HTML…", self._export_html)
        self._add_action(fm, "Export PDF…", self._export_pdf)

        em = mb.addMenu("Edit")
        self._add_action(em, "Undo", lambda: self._editor_panel and self._editor_panel.undo(), "Ctrl+Z")
        self._add_action(em, "Redo", lambda: self._editor_panel and self._editor_panel.redo(), "Ctrl+Y")
        em.addSeparator()
        self._add_action(em, "Find & Replace…", self._find_replace, "Ctrl+F")
        em.addSeparator()
        self._add_action(em, "Bold", self._bold, "Ctrl+B")
        self._add_action(em, "Italic", self._italic, "Ctrl+I")
        em.addSeparator()
        # Snippets submenu
        snippets_menu = em.addMenu("Insert Snippet")
        for name in SNIPPET_TEMPLATES:
            self._add_action(snippets_menu, name, lambda n=name: self._ins_snippet(n))

        vm = mb.addMenu("View")
        self._add_action(vm, "Command Palette", self._show_palette, "Ctrl+P")
        vm.addSeparator()
        self._add_action(vm, "Edit Only", lambda: self._switch_view("edit"))
        self._add_action(vm, "Split View", lambda: self._switch_view("split"))
        self._add_action(vm, "Preview Only", lambda: self._switch_view("preview"))
        self._add_action(vm, "Mind Map", lambda: self._switch_view("mind_map"))
        vm.addSeparator()
        self._add_action(vm, "Toggle Dark Mode", self._toggle_dark)
        self._add_action(vm, "Focus Mode", self._toggle_focus, "Ctrl+/")
        self._add_action(vm, "Typewriter Mode", self._toggle_typewriter, "Ctrl+T")
        self._add_action(vm, "Zen Mode", self._toggle_zen, "F11")
        vm.addSeparator()
        self._add_action(vm, "Larger Text", self._font_up, "Ctrl+=")
        self._add_action(vm, "Smaller Text", self._font_down, "Ctrl+-")

        gm = mb.addMenu("Graph")
        self._add_action(gm, "Show Graph View", self._show_graph_view, "Ctrl+G")
        self._add_action(gm, "Mind Map View", self._show_mind_map, "Ctrl+M")

        hm = mb.addMenu("Help")
        self._add_action(hm, "How to Use MarkPad", lambda: show_how_to_use(self, self.T))
        self._add_action(hm, "About MarkPad", lambda: show_about(self))

    def _add_action(self, menu, label, slot, shortcut=None):
        a = QAction(label, self)
        if shortcut:
            a.setShortcut(QKeySequence(shortcut))
        a.triggered.connect(slot)
        menu.addAction(a)
        return a

    def _rebuild_recent_menu(self):
        self._recent_menu.clear()
        for path in self._recent.files:
            name = os.path.basename(path)
            self._add_action(self._recent_menu, name, lambda p=path: self._load_file(p))
        if not self._recent.files:
            a = QAction("(no recent files)", self)
            a.setEnabled(False)
            self._recent_menu.addAction(a)

    # ── View switching ──
    def _switch_view(self, mode):
        self._preview_timer.stop()
        content = self._get_document_text()
        self.view_mode = mode
        self._update_tab_style()
        self._build_content()
        if self._editor_panel and content is not None:
            self._editor_panel.editor.blockSignals(True)
            self._editor_panel.setPlainText(content)
            self._editor_panel.editor.blockSignals(False)
        if getattr(self, "_preview_panel", None):
            self._update_preview()
        if getattr(self, "_mind_map_panel", None) and self.view_mode == "mind_map":
            self._mind_map_panel.update_map(content or "")
            
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()

    def _update_tab_style(self):
        for key, btn in self._tab_btns.items():
            btn.setProperty("active", "true" if key == self.view_mode else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    # ── Text & Tab handling ──
    def _add_tab(self, text: str, path: str = None):
        self.tabs_data.append({
            "path": path,
            "text": text,
            "modified": False,
            "cursor": 0,
            "scroll": 0
        })
        self._update_tab_switch_btn()
        self._on_tab_changed(len(self.tabs_data) - 1)

    def _update_tab_switch_btn(self):
        if hasattr(self, "_tab_switch_btn"):
            self._tab_switch_btn.setText(str(len(self.tabs_data)))

    def _save_current_tab_state(self):
        if self.current_tab_idx >= 0 and self.current_tab_idx < len(self.tabs_data) and self._editor_panel:
            tab = self.tabs_data[self.current_tab_idx]
            try:
                tab["text"] = self._editor_panel.toPlainText()
                tab["cursor"] = self._editor_panel.textCursor().position()
                tab["scroll"] = self._editor_panel.editor.verticalScrollBar().value()
            except RuntimeError:
                pass

    def _on_tab_changed(self, idx):
        if idx < 0 or idx >= len(self.tabs_data):
            return
            
        # Start fade out animation
        if hasattr(self, "_anim"):
            self._anim.stop()
            self._content_opacity.setOpacity(0.5)
            
        # Save old
        self._save_current_tab_state()
        self.current_tab_idx = idx
        
        # Load new
        tab = self.tabs_data[idx]
        self.current_file = tab["path"]
        self.modified = tab["modified"]
        
        if self._editor_panel:
            self._editor_panel.editor.blockSignals(True)
            self._editor_panel.setPlainText(tab["text"])
            cursor = self._editor_panel.textCursor()
            cursor.setPosition(min(tab["cursor"], len(tab["text"])))
            self._editor_panel.setTextCursor(cursor)
            self._editor_panel.editor.verticalScrollBar().setValue(tab["scroll"])
            self._editor_panel.editor.blockSignals(False)
        
        if getattr(self, "_preview_panel", None):
            self._update_preview()
        if getattr(self, "_mind_map_panel", None) and self.view_mode == "mind_map":
            self._mind_map_panel.update_map(tab["text"])
            
        self._update_status()
        
        # Fade back in
        if hasattr(self, "_anim"):
            self._anim.setStartValue(0.3)
            self._anim.setEndValue(1.0)
            self._anim.start()

    def _on_tab_closed(self, idx):
        if idx < 0 or idx >= len(self.tabs_data):
            return
        tab = self.tabs_data[idx]
        if tab["modified"]:
            r = QMessageBox.question(self, "Unsaved Changes", f"Save changes to {os.path.basename(tab['path']) if tab['path'] else 'Untitled'}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            if r == QMessageBox.StandardButton.Cancel:
                return
            if r == QMessageBox.StandardButton.Yes:
                self.current_tab_idx = idx # temporarily switch to save
                self._save()
        
        self.tabs_data.pop(idx)
        self._update_tab_switch_btn()
        
        if len(self.tabs_data) == 0:
            self._add_tab("", None)
        elif self.current_tab_idx == idx or self.current_tab_idx >= len(self.tabs_data):
            new_idx = max(0, idx - 1)
            self._on_tab_changed(new_idx)

    def _get_document_text(self):
        if self.current_tab_idx >= 0 and self.current_tab_idx < len(self.tabs_data):
            if self._editor_panel:
                try:
                    return self._editor_panel.toPlainText()
                except RuntimeError:
                    pass
            return self.tabs_data[self.current_tab_idx]["text"]
        return ""

    def _on_text_changed(self):
        if self.current_tab_idx >= 0 and self.current_tab_idx < len(self.tabs_data):
            self.tabs_data[self.current_tab_idx]["modified"] = True
            self.modified = True
            try:
                self.tabs_data[self.current_tab_idx]["text"] = self._editor_panel.toPlainText()
            except RuntimeError:
                pass
        self._update_status()
        self._preview_timer.start()

    def _update_status(self):
        try:
            txt = self._get_document_text() or ""
            words = word_count(txt)
            chars = char_count(txt)
            rt = reading_time(txt)
            mod = " •" if self.modified else ""
            fname = os.path.basename(self.current_file) if self.current_file else "Untitled.md"
            self._stat_left.setText(f"{fname}{mod}")
            if self._editor_panel:
                c = self._editor_panel.textCursor()
                ln = c.blockNumber() + 1
                col = c.columnNumber() + 1
                self._stat_right.setText(f"{words} words · {chars} chars · {rt} · Ln {ln} Col {col}")
            self._fname_lbl.setText(f"{fname}{mod}")
        except (RuntimeError, AttributeError):
            pass

    def _update_preview(self):
        text = self._get_document_text() or ""
        base_url = os.path.dirname(self.current_file) + "/" if self.current_file else ""
        if getattr(self, "_preview_panel", None):
            try:
                self._preview_panel.update_preview(text, self.font_size, base_url)
            except RuntimeError:
                pass
        if getattr(self, "_mind_map_panel", None) and self.view_mode == "mind_map":
            try:
                self._mind_map_panel.update_map(text)
            except RuntimeError:
                pass

    # ── Dark mode ──
    def _toggle_dark(self):
        content = self._get_document_text()
        self.is_dark = not self.is_dark
        self.T = DARK if self.is_dark else LIGHT
        self.settings.set("theme", "dark" if self.is_dark else "light")
        self.settings.save()
        self.setStyleSheet(build_stylesheet(self.T))

        old_title = self._title_bar
        old_tb = self._toolbar
        self._title_bar = self._make_titlebar()
        self._toolbar = self._make_toolbar()
        root = self.centralWidget().layout()
        root.insertWidget(0, self._title_bar)
        root.insertWidget(1, self._toolbar)
        old_title.deleteLater()
        old_tb.deleteLater()

        self._build_content()
        if self._editor_panel and content:
            self._editor_panel.setPlainText(content)
        if self._preview_panel:
            base_url = os.path.dirname(self.current_file) + "/" if self.current_file else ""
            self._preview_panel.force_full_reload(content or "", self.font_size)
            self._preview_panel.update_preview(content or "", self.font_size, base_url)
        self._update_status()

    # ── Sidebar ──
    def _toggle_sidebar(self):
        self.sidebar.setVisible(not self.sidebar.isVisible())

    def _open_from_tree(self, index):
        if not self.file_model.isDir(index):
            self._load_file(self.file_model.filePath(index))

    # ── Focus & Zen ──
    def _toggle_focus(self):
        self._focus_mode = not self._focus_mode
        if self._editor_panel:
            opacity = "0.4" if self._focus_mode else "1.0"
            self._editor_panel.setStyleSheet(
                f"background:{self.T['editor_bg']};"
                + (f"QTextEdit#editor{{color:rgba(255,255,255,0.4);}}" if self._focus_mode and self.is_dark else "")
            )

    def _toggle_typewriter(self):
        if self._editor_panel and hasattr(self._editor_panel, "editor"):
            mode = not self._editor_panel.editor.typewriter_mode
            self._editor_panel.editor.typewriter_mode = mode
            if mode:
                self._editor_panel.editor.centerCursor()

    def _toggle_zen(self):
        self._zen_mode = not self._zen_mode
        if self._zen_mode:
            self._toolbar.hide()
            self._title_bar.hide()
            self.sidebar.hide()
            self.status_bar.hide()
            self.showFullScreen()
        else:
            self._toolbar.show()
            self._title_bar.show()
            self.status_bar.show()
            self.showNormal()

    # ── Command Palette ──
    def _show_palette(self):
        commands = [
            ("New File", self._new), ("Open File", self._open), ("Save File", self._save),
            ("Toggle Dark Mode", self._toggle_dark), ("Toggle Sidebar", self._toggle_sidebar),
            ("Find & Replace", self._find_replace), ("Insert Table", lambda: self._ins_snippet("Table")),
            ("Insert Image", self._ins_image), ("Export PDF", self._export_pdf),
            ("Export HTML", self._export_html), ("Focus Mode", self._toggle_focus),
            ("Zen Mode", self._toggle_zen), ("Graph View", self._show_graph_view),
            ("Mind Map View", self._show_mind_map),
            ("View: Split", lambda: self._switch_view("split")),
            ("View: Edit", lambda: self._switch_view("edit")),
            ("View: Preview", lambda: self._switch_view("preview")),
            ("About MarkPad", lambda: show_about(self)),
        ]
        for name in SNIPPET_TEMPLATES:
            commands.append((f"Snippet: {name}", lambda n=name: self._ins_snippet(n)))
        CommandPalette(self, self.T, commands).exec()

    # ── File operations ──
    def _load_file(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Cannot open file:\n{e}")
            return
        self._add_tab(content, path)
        self._recent.add(path)
        self._rebuild_recent_menu()

    def _new(self):
        self._add_tab("", None)

    def _open(self):
        p, _ = QFileDialog.getOpenFileName(self, "Open", "",
            "Markdown (*.md *.markdown *.txt);;All Files (*)")
        if p:
            self._load_file(p)

    def _save(self):
        if self.current_tab_idx >= 0 and self.current_tab_idx < len(self.tabs_data):
            tab = self.tabs_data[self.current_tab_idx]
            if tab["path"]:
                with open(tab["path"], "w", encoding="utf-8") as f:
                    f.write(self._get_document_text())
                tab["modified"] = False
                self.modified = False
                self._update_status()
            else:
                self._save_as()

    def _save_as(self):
        p, _ = QFileDialog.getSaveFileName(self, "Save As", "", "Markdown (*.md);;All (*)")
        if p and self.current_tab_idx >= 0:
            tab = self.tabs_data[self.current_tab_idx]
            tab["path"] = p
            self.current_file = p
            self._save()
            self._recent.add(p)
            self._rebuild_recent_menu()

    def _export_html(self):
        text = self._get_document_text()
        html = build_preview_html(text, self.T, self.font_size, self._engine)
        p, _ = QFileDialog.getSaveFileName(self, "Export HTML", "", "HTML (*.html)")
        if p:
            with open(p, "w", encoding="utf-8") as f:
                f.write(html)
            QMessageBox.information(self, "Exported", f"Saved to:\n{p}")

    def _export_pdf(self):
        dlg = PDFExportDialog(self, self.T)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        style = dlg.result_style
        path = dlg.result_path
        md_text = self._get_document_text()
        theme = LIGHT if style != "ace" else DARK
        html = build_preview_html(md_text, theme, self.font_size, self._engine)
        try:
            from PyQt6.QtPrintSupport import QPrinter
            from PyQt6.QtCore import QEventLoop
            from PyQt6.QtGui import QPageSize
            web = QWebEngineView()
            web.setHtml(html)
            loop = QEventLoop()
            def on_load(ok):
                if ok:
                    web.page().printToPdf(path)
                    web.page().pdfPrintingFinished.connect(lambda fp, s: loop.quit())
                else:
                    loop.quit()
            web.loadFinished.connect(on_load)
            loop.exec()
            QMessageBox.information(self, "Success", f"PDF exported:\n{path}")
        except Exception:
            html_path = path.replace('.pdf', '.html')
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html)
            QMessageBox.information(self, "PDF Export",
                f"Saved as HTML instead:\n{html_path}\nOpen in browser to print as PDF.")

    def _find_replace(self):
        if self._editor_panel:
            FindDialog(self, self._editor_panel.editor, self.T).exec()

    def _show_graph_view(self):
        from markpad.ui.graph_view import show_graph_view
        text = self._get_document_text() or ""
        vault = os.path.dirname(self.current_file) if self.current_file else None
        show_graph_view(self, self.current_file, text, self.T, vault)

    def _show_mind_map(self):
        from markpad.ui.mind_map_view import show_mind_map
        text = self._get_document_text() or ""
        show_mind_map(self, text, self.T)

    def _autosave(self):
        if self.modified and self.current_file:
            self._save()

    # ── Formatting ──
    def _wrap(self, before, after=None):
        if not self._editor_panel:
            return
        after = after or before
        cursor = self._editor_panel.textCursor()
        if cursor.hasSelection():
            sel = cursor.selectedText()
            cursor.insertText(f"{before}{sel}{after}")
        else:
            pos = cursor.position()
            cursor.insertText(f"{before}{after}")
            cursor.setPosition(pos + len(before))
            self._editor_panel.setTextCursor(cursor)

    def _prefix(self, pre):
        if not self._editor_panel:
            return
        cursor = self._editor_panel.textCursor()
        cursor.beginEditBlock()
        if cursor.hasSelection():
            start, end = cursor.selectionStart(), cursor.selectionEnd()
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
        self._ins_snippet("Table")

    def _ins_hr(self):
        if self._editor_panel:
            self._editor_panel.insertPlainText("\n\n---\n\n")

    def _ins_link(self):
        if not self._editor_panel:
            return
        cursor = self._editor_panel.textCursor()
        sel = cursor.selectedText() or "Link Text"
        url, ok = QInputDialog.getText(self, "Insert Link", "URL:", text="https://")
        if ok and url:
            cursor.insertText(f"[{sel}]({url})")

    def _ins_image(self):
        dlg = ImageDialog(self, self.T)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.result_text:
            if self._editor_panel:
                self._editor_panel.insertPlainText("\n" + dlg.result_text + "\n")

    def _ins_snippet(self, name=None):
        if not self._editor_panel or not name:
            return
        text = SNIPPET_TEMPLATES.get(name, "")
        if text:
            self._editor_panel.insertPlainText("\n" + text + "\n")

    # ── Font size ──
    def _font_up(self):
        if self.font_size < 30:
            self.font_size += 1
            self._apply_font()

    def _font_down(self):
        if self.font_size > 8:
            self.font_size -= 1
            self._apply_font()

    def _apply_font(self):
        if self._editor_panel:
            self._editor_panel.set_font_size(self.font_size)
        self._size_lbl.setText(str(self.font_size))
        self.settings.set("font_size", self.font_size)
        self._update_preview()
