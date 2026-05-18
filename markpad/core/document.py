"""
Document model for MarkPad — manages document state, autosave, and recent files.
"""

import json
import os
import time
from typing import Optional


class Document:
    """Represents a single Markdown document with metadata."""

    def __init__(self, path: Optional[str] = None, content: str = ""):
        self.path = path
        self.content = content
        self.modified = False
        self.created_at = time.time()
        self.last_saved_at: Optional[float] = None
        self._original_content = content

    @property
    def filename(self) -> str:
        if self.path:
            return os.path.basename(self.path)
        return "Untitled.md"

    @property
    def directory(self) -> Optional[str]:
        if self.path:
            return os.path.dirname(self.path)
        return None

    @property
    def display_name(self) -> str:
        mod = " •" if self.modified else ""
        return f"{self.filename}{mod}"

    def update_content(self, text: str):
        """Update document content and mark as modified if changed."""
        if text != self.content:
            self.content = text
            self.modified = text != self._original_content

    def save(self, path: Optional[str] = None):
        """Save document to disk."""
        save_path = path or self.path
        if not save_path:
            raise ValueError("No file path specified")
        
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(self.content)
        
        self.path = save_path
        self.modified = False
        self._original_content = self.content
        self.last_saved_at = time.time()

    @classmethod
    def from_file(cls, path: str) -> "Document":
        """Load a document from a file."""
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        doc = cls(path=path, content=content)
        doc._original_content = content
        doc.last_saved_at = os.path.getmtime(path)
        return doc


class RecentFiles:
    """Manages the list of recently opened files."""

    MAX_RECENT = 10

    def __init__(self, config_path: str):
        self._path = config_path
        self._files: list[str] = []
        self._load()

    def _load(self):
        if os.path.exists(self._path):
            try:
                with open(self._path, "r") as f:
                    data = json.load(f)
                self._files = [p for p in data.get("recent", []) if os.path.exists(p)]
            except (json.JSONDecodeError, KeyError):
                self._files = []

    def _save(self):
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, "w") as f:
            json.dump({"recent": self._files}, f, indent=2)

    def add(self, path: str):
        """Add a file to the recent list."""
        path = os.path.abspath(path)
        if path in self._files:
            self._files.remove(path)
        self._files.insert(0, path)
        self._files = self._files[:self.MAX_RECENT]
        self._save()

    @property
    def files(self) -> list[str]:
        return list(self._files)

    def clear(self):
        self._files = []
        self._save()
