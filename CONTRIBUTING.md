# Contributing to MarkPad

Thank you for your interest in contributing to MarkPad! We welcome contributions of all kinds — whether it's bug reports, feature requests, documentation improvements, or code contributions.

> **Note:** By contributing to MarkPad, you agree that your contributions will be licensed under the [PolyForm Noncommercial License 1.0.0](LICENSE).

---

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Getting Started](#-getting-started)
- [Development Setup](#-development-setup)
- [Making Changes](#-making-changes)
- [Pull Request Process](#-pull-request-process)
- [Coding Standards](#-coding-standards)
- [Commit Convention](#-commit-convention)
- [Project Architecture](#-project-architecture)
- [Testing](#-testing)
- [Documentation](#-documentation)
- [Recognition](#-recognition)

---

## 📜 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [zamin-naqvi@example.com](mailto:zamin-naqvi@example.com).

---

## 🚀 Getting Started

### Prerequisites

| Requirement | Minimum Version | Recommended |
|-------------|----------------|-------------|
| Python | 3.9+ | 3.11+ |
| Git | 2.30+ | Latest |
| pip | 21.0+ | Latest |

### Types of Contributions

| Type | Description | Difficulty |
|------|-------------|------------|
| 🐛 **Bug Fixes** | Fix broken functionality | Easy–Medium |
| 📝 **Documentation** | Improve docs, comments, README | Easy |
| ✨ **New Features** | Add new functionality | Medium–Hard |
| 🧪 **Tests** | Add or improve test coverage | Easy–Medium |
| 🎨 **UI/UX** | Improve design and user experience | Medium |
| ♻️ **Refactoring** | Clean up code, improve architecture | Medium–Hard |
| 🌐 **Translations** | Add i18n support | Medium |

---

## 🛠️ Development Setup

### 1. Fork & Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/MarkPad.git
cd MarkPad

# Add upstream remote
git remote add upstream https://github.com/zamin-naqvi/MarkPad.git
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install runtime + dev dependencies
pip install -e ".[dev]"

# Or install just runtime dependencies
pip install -r requirements.txt
```

### 4. Verify Setup

```bash
# Run the app
python main.py

# Run tests
pytest

# Check code style
black --check markpad/
flake8 markpad/
```

---

## ✏️ Making Changes

### 1. Create a Branch

```bash
# Sync with upstream first
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

### Branch Naming Convention

| Prefix | Use Case | Example |
|--------|----------|---------|
| `feature/` | New functionality | `feature/spell-check` |
| `fix/` | Bug fixes | `fix/preview-scroll-reset` |
| `docs/` | Documentation changes | `docs/api-reference` |
| `refactor/` | Code restructuring | `refactor/engine-caching` |
| `test/` | Test additions | `test/pdf-export` |
| `ci/` | CI/CD changes | `ci/add-macos-build` |

### 2. Make Your Changes

- Keep changes focused — one feature/fix per PR
- Follow the [coding standards](#-coding-standards) below
- Add or update tests for your changes
- Update documentation if needed

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_engine.py

# Check code formatting
black --check markpad/
```

---

## 🔄 Pull Request Process

### Before Submitting

- [ ] Code follows the project's [coding standards](#-coding-standards)
- [ ] Tests pass locally (`pytest`)
- [ ] Code is formatted with Black (`black markpad/`)
- [ ] No lint warnings (`flake8 markpad/`)
- [ ] New features include tests
- [ ] Documentation is updated if needed
- [ ] Commit messages follow [conventional commits](#-commit-convention)

### Submitting

1. **Push** your branch to your fork
2. **Open a Pull Request** against `main` on the upstream repository
3. **Fill out** the PR template completely
4. **Wait** for CI checks to pass
5. **Address** any review feedback

### PR Title Format

```
<type>(<scope>): <short description>

# Examples:
feat(editor): add vim keybinding mode
fix(preview): resolve scroll position reset on theme toggle
docs(readme): update installation instructions
```

### Review Process

- All PRs require at least **1 approving review** before merge
- Maintainers may request changes — this is normal and collaborative
- CI checks must pass before merge
- PRs are squash-merged to keep history clean

---

## 📐 Coding Standards

### Python Style

| Rule | Standard |
|------|----------|
| **Formatter** | [Black](https://black.readthedocs.io/) (line length: 100) |
| **Linter** | [Flake8](https://flake8.pycqa.org/) |
| **Python Version** | 3.9+ compatible |
| **Type Hints** | Encouraged for all public APIs |
| **Docstrings** | Google-style for public classes and functions |

### Example

```python
def render_markdown(text: str, theme: str = "light") -> str:
    """Render Markdown text to styled HTML.

    Args:
        text: Raw Markdown text to render.
        theme: Color theme name ("light" or "dark").

    Returns:
        Complete HTML document as a string.

    Raises:
        ValueError: If theme name is not recognized.
    """
    if theme not in ("light", "dark"):
        raise ValueError(f"Unknown theme: {theme}")
    # Implementation...
```

### File Organization

```python
"""Module docstring explaining purpose."""

# Standard library imports
import os
import re
from typing import Optional

# Third-party imports
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt

# Local imports
from markpad.core.engine import RenderEngine
from markpad.themes.theme_data import DARK, LIGHT
```

---

## 📝 Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

```
<type>(<optional scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat: add spell check integration` |
| `fix` | Bug fix | `fix: preview scroll not syncing` |
| `docs` | Documentation only | `docs: add API reference` |
| `style` | Code formatting (no logic change) | `style: run black on codebase` |
| `refactor` | Code restructuring (no feature/fix) | `refactor: extract preview panel class` |
| `perf` | Performance improvement | `perf: cache rendered HTML blocks` |
| `test` | Adding or updating tests | `test: add engine rendering tests` |
| `build` | Build system changes | `build: update PyInstaller spec` |
| `ci` | CI/CD changes | `ci: add macOS build workflow` |
| `chore` | Maintenance tasks | `chore: update dependencies` |

---

## 🏗️ Project Architecture

```
markpad/
├── core/           # Business logic layer
│   ├── engine.py   # Markdown → HTML rendering (caching, incremental)
│   ├── document.py # Document model & recent files
│   └── settings.py # Persistent settings (JSON-based)
│
├── ui/             # Presentation layer (Qt widgets)
│   ├── main_window.py     # Main window, menus, toolbar, tabs
│   ├── editor.py          # Text editor with line numbers
│   ├── preview.py         # WebEngine preview panel
│   ├── graph_view.py      # D3.js knowledge graph
│   ├── mind_map_view.py   # Auto-generated mind map
│   └── mind_map_editor.py # Interactive mind map editor
│
├── dialogs/        # Modal/popup dialogs
│   ├── command_palette.py # Fuzzy command search
│   ├── find_replace.py    # Find & replace
│   ├── image_insert.py    # Image insertion
│   ├── pdf_export.py      # PDF export wizard
│   ├── slash_menu.py      # Slash command popup
│   ├── tab_switcher.py    # Multi-tab navigator
│   └── how_to_use.py      # Interactive usage guide
│
├── themes/         # Theming system
│   ├── theme_data.py  # Color palettes (LIGHT, DARK)
│   └── stylesheet.py  # Qt stylesheet generator
│
└── utils/          # Shared utilities
    ├── helpers.py  # Text analysis, snippets
    └── icons.py    # SVG icon loader
```

### Key Design Decisions

1. **Incremental rendering**: Only changed blocks are re-rendered and patched via JavaScript DOM diffing — no full page reloads
2. **Lazy loading**: MathJax, Mermaid, and Chart.js CDN scripts are only loaded when the document uses them
3. **Block caching**: Each paragraph/heading is hashed (MD5) and cached to avoid redundant conversion
4. **Singleton engine**: A single `RenderEngine` instance is shared across the app for cache coherence

---

## 🧪 Testing

### Running Tests

```bash
# All tests
pytest

# With coverage report
pytest --cov=markpad --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=markpad --cov-report=html
open htmlcov/index.html
```

### Writing Tests

- Place tests in the `tests/` directory
- Mirror the source structure: `markpad/core/engine.py` → `tests/test_engine.py`
- Use `pytest` fixtures for common setup
- Mock Qt widgets when testing non-UI logic

```python
# tests/test_engine.py
import pytest
from markpad.core.engine import RenderEngine


class TestRenderEngine:
    def setup_method(self):
        self.engine = RenderEngine()

    def test_render_heading(self):
        html = self.engine.render_full("# Hello World")
        assert "<h1>" in html
        assert "Hello World" in html

    def test_render_empty(self):
        assert self.engine.render_full("") == ""
        assert self.engine.render_full("   ") == ""
```

---

## 📚 Documentation

### Where to Document

| What | Where |
|------|-------|
| User-facing features | `README.md` |
| API / internals | Docstrings in source code |
| Version changes | `CHANGELOG.md` |
| Architecture decisions | `CONTRIBUTING.md` (this file) |

### Docstring Style

We use Google-style docstrings:

```python
def process(text: str, options: dict | None = None) -> str:
    """Process Markdown text with the given options.

    Args:
        text: The raw Markdown text.
        options: Optional processing options.
            Supported keys: "emoji" (bool), "wiki_links" (bool).

    Returns:
        The processed text with replacements applied.

    Example:
        >>> process(":rocket: Launch!", {"emoji": True})
        "🚀 Launch!"
    """
```

---

## 🏆 Recognition

All contributors are recognized in the project! Your name/username will be added to the contributors list when your first PR is merged.

We especially value:
- 🐛 Bug reports with clear reproduction steps
- 📝 Documentation improvements
- 🧪 Test additions
- ♿ Accessibility improvements
- 🌐 Internationalization help

---

## ❓ Questions?

- 💬 Open a [Discussion](https://github.com/zamin-naqvi/MarkPad/discussions) for questions
- 🐛 Open an [Issue](https://github.com/zamin-naqvi/MarkPad/issues) for bugs
- 💡 Open a [Feature Request](https://github.com/zamin-naqvi/MarkPad/issues/new?template=feature_request.md) for ideas
- 📧 Email the maintainer for sensitive matters

---

<p align="center">
  <strong>Thank you for making MarkPad better! 🎉</strong>
</p>
