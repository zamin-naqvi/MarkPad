"""
Icon loading utilities for MarkPad.
"""

import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QImage

# Icon directory — relative to the project root
_ICONS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "icons")


def get_icons_dir() -> str:
    """Return the absolute path to the icons directory."""
    return _ICONS_DIR


def load_icon(name: str, color: str = "#1D1D1F", size: int = 20) -> QIcon:
    """Load a PNG icon from icons/ and recolor it to match the current theme."""
    h = color.lstrip("#")
    lum = 0.299 * int(h[0:2], 16) + 0.587 * int(h[2:4], 16) + 0.114 * int(h[4:6], 16)
    variant = "ffffff" if lum < 128 else "000000"
    path = os.path.join(_ICONS_DIR, f"{name}_{variant}.png")

    if not os.path.exists(path):
        return QIcon()

    img = QImage(path).convertToFormat(QImage.Format.Format_ARGB32)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    for y in range(img.height()):
        for x in range(img.width()):
            px = img.pixel(x, y)
            a = (px >> 24) & 0xFF
            if a > 0:
                img.setPixel(x, y, (a << 24) | (r << 16) | (g << 8) | b)

    pix = QPixmap.fromImage(img).scaled(
        size, size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    return QIcon(pix)


def load_app_icon() -> QIcon:
    """Load the application icon."""
    path = os.path.join(_ICONS_DIR, "app_icon.png")
    if os.path.exists(path):
        return QIcon(path)
    return QIcon()
