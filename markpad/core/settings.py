"""
Application settings and preferences manager.
"""

import json
import os
from typing import Any


DEFAULT_SETTINGS = {
    "theme": "light",
    "font_size": 15,
    "autosave_enabled": True,
    "autosave_interval_sec": 30,
    "last_view_mode": "split",
    "window_width": 1280,
    "window_height": 820,
    "sidebar_visible": False,
    "sidebar_width": 200,
    "word_count_goal": 0,
    "focus_mode": False,
    "scroll_sync": True,
    "show_line_numbers": True,
    "editor_font_family": "Consolas",
    "preview_font_family": "-apple-system, Segoe UI, Helvetica Neue, Arial, sans-serif",
}


class Settings:
    """Persistent settings manager with JSON storage."""

    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            config_dir = os.path.join(os.path.expanduser("~"), ".markpad")
        self._dir = config_dir
        self._path = os.path.join(config_dir, "settings.json")
        self._data: dict[str, Any] = dict(DEFAULT_SETTINGS)
        self._load()

    def _load(self):
        if os.path.exists(self._path):
            try:
                with open(self._path, "r") as f:
                    saved = json.load(f)
                self._data.update(saved)
            except (json.JSONDecodeError, IOError):
                pass

    def save(self):
        """Persist settings to disk."""
        os.makedirs(self._dir, exist_ok=True)
        with open(self._path, "w") as f:
            json.dump(self._data, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any):
        self._data[key] = value

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any):
        self._data[key] = value

    @property
    def config_dir(self) -> str:
        return self._dir


# Fix: need Optional import
from typing import Optional
