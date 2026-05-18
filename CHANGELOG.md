# Changelog

All notable changes to MarkPad will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-05-18

### Added
- ⚡ **Instant live preview** — zero-delay incremental rendering via JavaScript DOM diffing
- 🔥 **Blazing-fast rendering engine** — Pygments syntax highlighting, emoji support, smart caching
- 🕸️ **Interactive graph view** — D3.js force-directed graph with drag, zoom, and click-to-navigate
- 📜 **Table of Contents panel** — Auto-generated from headings with click-to-scroll
- 🎯 **Focus mode** — Dims all paragraphs except the one you're editing
- 🧘 **Zen mode** — Full-screen distraction-free writing
- 💾 **Autosave** — Automatic save every 30 seconds with crash recovery
- 📂 **Recent files** — Quick access to recently opened documents
- 📝 **Snippet templates** — Quick-insert for tables, code blocks, diagrams, and more
- 🔄 **Scroll sync** — Synchronized scrolling between editor and preview
- 🔗 **Wiki links** — `[[page]]` style linking support
- 😀 **Emoji support** — `:emoji_name:` rendering in preview
- 🎨 **Syntax highlighting** — Pygments-powered code block coloring
- 📦 **Modular architecture** — Clean package structure for easy contribution
- 📄 **MIT License** — Fully open source
- 📋 **GitHub-ready** — README, CONTRIBUTING, CI workflows

### Changed
- Restructured from monolithic `main.py` to modular `markpad/` package
- Preview engine now uses incremental DOM updates instead of full page reloads
- Graph view now uses D3.js with full interactivity (was static vis.js)
- Improved theme system with cleaner separation

### Fixed
- Preview no longer has 300ms delay — updates are instant
- Graph nodes are now fully draggable and zoomable
- Scroll position maintained during preview updates

## [1.0.0] - 2026-05-18

### Added
- Initial release with basic Markdown editing
- Split/Edit/Preview view modes
- Dark/Light theme toggle
- Find & Replace
- Image insertion dialog
- PDF export with style selection
- Command palette (Ctrl+P)
- File explorer sidebar
- Basic graph view
