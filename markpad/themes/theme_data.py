"""
Theme color definitions for MarkPad.
"""

LIGHT = {
    "bg":           "#F5F5F7",
    "toolbar_bg":   "#EBEBF0",
    "editor_bg":    "#FFFFFF",
    "editor_fg":    "#1D1D1F",
    "preview_bg":   "#FAFAFA",
    "border":       "#D1D1D6",
    "accent":       "#0071E3",
    "accent_fg":    "#FFFFFF",
    "btn_bg":       "#FFFFFF",
    "btn_fg":       "#1D1D1F",
    "btn_hover":    "#E5E5EA",
    "btn_border":   "#D1D1D6",
    "tab_active":   "#0071E3",
    "tab_active_fg":"#FFFFFF",
    "tab_bg":       "#DCDCE0",
    "tab_fg":       "#3A3A3C",
    "status_bg":    "#E8E8ED",
    "status_fg":    "#6E6E73",
    "lnum_bg":      "#F2F2F7",
    "lnum_fg":      "#AEAEB2",
    "scrollbar":    "#C7C7CC",
    "icon_color":   "#1D1D1F",
}

DARK = {
    "bg":           "#1C1C1E",
    "toolbar_bg":   "#2C2C2E",
    "editor_bg":    "#1C1C1E",
    "editor_fg":    "#F5F5F7",
    "preview_bg":   "#242426",
    "border":       "#3A3A3C",
    "accent":       "#0A84FF",
    "accent_fg":    "#FFFFFF",
    "btn_bg":       "#3A3A3C",
    "btn_fg":       "#F5F5F7",
    "btn_hover":    "#48484A",
    "btn_border":   "#48484A",
    "tab_active":   "#0A84FF",
    "tab_active_fg":"#FFFFFF",
    "tab_bg":       "#3A3A3C",
    "tab_fg":       "#EBEBF0",
    "status_bg":    "#2C2C2E",
    "status_fg":    "#8E8E93",
    "lnum_bg":      "#2C2C2E",
    "lnum_fg":      "#48484A",
    "scrollbar":    "#48484A",
    "icon_color":   "#F5F5F7",
}

THEMES = {"light": LIGHT, "dark": DARK}

SAMPLE_DOCUMENT = """\
# Welcome to MarkPad

A blazing-fast Markdown editor with instant live preview, built in Python + PyQt6.

## ✨ Features

- ⚡ **Instant live preview** — zero-delay rendering
- 🎨 **Syntax highlighting** — Pygments-powered code blocks
- 🕸️ **Interactive graph view** — drag, zoom, and navigate
- 📜 **Table of Contents** — auto-generated from headings
- 🧘 **Focus & Zen modes** — distraction-free writing
- 💾 **Autosave** — never lose your work
- 😀 **Emoji support** — `:smile:` → 😄

## Formatting

**bold**, *italic*, ~~strikethrough~~, `inline code`

## Lists

- Item one
- Item two
  - Nested item

1. First
2. Second

## Blockquote

> "Simplicity is the ultimate sophistication." — da Vinci

## Code

```python
def greet(name: str) -> str:
    \"\"\"Say hello with style.\"\"\"
    return f"Hello, {name}! 🚀"

print(greet("World"))
```

## Math & Diagrams

**MathJax** renders beautiful LaTeX equations:
$$ E = mc^2 $$

$$ \\int_{a}^{b} x^2 \\,dx = \\frac{b^3 - a^3}{3} $$

**Mermaid.js** creates flowcharts from text:

```mermaid
graph TD;
    A[Markdown] --> B(Live Preview);
    B --> C{Render};
    C -->|Success| D[HTML & Diagrams];
    C -->|Export| E[PDF Document];
```

## Table

| Feature        | Shortcut | Status |
|----------------|----------|--------|
| Bold           | Ctrl+B   | ✅     |
| Italic         | Ctrl+I   | ✅     |
| Focus Mode     | Ctrl+/   | ✅     |
| Graph View     | Ctrl+G   | ✅     |
| Zen Mode       | F11      | ✅     |
| PDF Export     | Menu     | ✅     |

## Wiki Links

Link to other notes with `[[page name]]` syntax: [[my-notes]]

## Emoji

:rocket: :heart: :star: :fire: :sparkles:

---

Edit here — preview updates **instantly**!
"""
