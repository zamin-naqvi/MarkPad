"""
About dialog for MarkPad.
"""

from PyQt6.QtWidgets import QMessageBox

from markpad import __version__


def show_about(parent):
    """Show the About dialog."""
    QMessageBox.about(
        parent,
        "About MarkPad",
        f"<h3>MarkPad v{__version__}</h3>"
        "<p>A blazing-fast, beautiful Markdown editor with instant live preview.</p>"
        "<p><b>License:</b> MIT — free to use, modify, and distribute.</p>"
        "<p><b>Built with:</b> Python + PyQt6</p>"
        "<p><b>GitHub:</b> <a href='https://github.com/zamin-naqvi/MarkPad'>github.com/zamin-naqvi/MarkPad</a></p>"
        "<hr>"
        "<p style='color: #888; font-size: 11px;'>"
        "Features: Instant preview • Syntax highlighting • Graph view • "
        "Focus/Zen modes • Autosave • Emoji • PDF export</p>"
    )
