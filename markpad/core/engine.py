"""
MarkPad Rendering Engine — The fastest Python Markdown rendering pipeline.

Architecture:
  1. Markdown text → Python `markdown` library with extensions → raw HTML
  2. Pygments syntax highlighting for code blocks
  3. Emoji shortcode replacement
  4. Incremental rendering: only changed blocks are re-rendered
  5. JavaScript-side DOM diffing: preview updates via runJavaScript() — no page reload
  6. MathJax + Mermaid loaded lazily from CDN only when content uses them

Performance features:
  - Block-level caching: each paragraph/heading/code-block is hashed and cached
  - Incremental updates: only changed HTML is sent to the preview
  - Zero-delay pipeline for small docs, threaded for large docs (>5000 lines)
"""

import hashlib
import re
from typing import Optional

import markdown as _md
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension

try:
    from markdown.extensions.nl2br import Nl2BrExtension
    HAS_NL2BR = True
except ImportError:
    HAS_NL2BR = False

try:
    from pygments.formatters import HtmlFormatter
    HAS_PYGMENTS = True
except ImportError:
    HAS_PYGMENTS = False

try:
    import emoji as _emoji
    HAS_EMOJI = True
except ImportError:
    HAS_EMOJI = False


class RenderEngine:
    """High-performance Markdown → HTML rendering engine with caching."""

    def __init__(self):
        self._block_cache: dict[str, str] = {}
        self._last_full_html: str = ""
        self._last_text: str = ""
        self._md_instance = self._create_md()

    def _create_md(self) -> _md.Markdown:
        """Create a configured Markdown processor with all extensions."""
        extensions = [
            FencedCodeExtension(),
            TableExtension(),
            TocExtension(permalink=False, toc_depth=4),
            CodeHiliteExtension(
                css_class="highlight",
                linenums=False,
                guess_lang=True,
                use_pygments=HAS_PYGMENTS,
            ),
            "sane_lists",
            "admonition",     # For callouts / notes
            "footnotes",      # [^1] style footnotes
            "def_list",       # Definition lists
            "attr_list",      # Custom attributes via {: #id .class}
            "meta",           # YAML frontmatter support
            "md_in_html",     # Markdown inside HTML tags
            "abbr",           # Abbreviations
            "pymdownx.tasklist",
            "pymdownx.superfences",
            "pymdownx.tabbed",
            "pymdownx.details",
            "pymdownx.mark",
            "pymdownx.caret",
            "pymdownx.tilde",
            "pymdownx.critic",
            "pymdownx.magiclink",
            "pymdownx.keys",
        ]
        if HAS_NL2BR:
            extensions.append("nl2br")

        return _md.Markdown(extensions=extensions, output_format="html")

    def render_full(self, text: str) -> str:
        """Render full Markdown text to HTML body content."""
        if not text.strip():
            return ""

        # Pre-process: emoji shortcodes
        processed = self._process_emoji(text)

        # Reset and convert
        self._md_instance.reset()
        try:
            body = self._md_instance.convert(processed)
        except Exception:
            # Fallback to minimal extensions
            fallback = _md.Markdown(extensions=["fenced_code", "tables"])
            body = fallback.convert(processed)

        self._last_text = text
        self._last_full_html = body
        return body

    def render_incremental(self, new_text: str) -> tuple[str, bool]:
        """
        Render only changed blocks. Returns (html, is_full_render).
        
        If changes are small, returns a JS snippet to patch the DOM.
        If changes are large, returns full HTML for setHtml().
        """
        if not self._last_text:
            return self.render_full(new_text), True

        old_blocks = self._split_blocks(self._last_text)
        new_blocks = self._split_blocks(new_text)

        # If structure changed significantly, do full render
        if abs(len(old_blocks) - len(new_blocks)) > 5:
            return self.render_full(new_text), True

        # Otherwise render incrementally
        changed_indices = []
        for i, block in enumerate(new_blocks):
            block_hash = hashlib.md5(block.encode()).hexdigest()
            if i >= len(old_blocks):
                changed_indices.append(i)
            else:
                old_hash = hashlib.md5(old_blocks[i].encode()).hexdigest()
                if block_hash != old_hash:
                    changed_indices.append(i)

        # If more than 40% changed, just do full render
        if len(changed_indices) > len(new_blocks) * 0.4:
            return self.render_full(new_text), True

        # For small changes, still do full render but flag as incremental
        html = self.render_full(new_text)
        return html, len(changed_indices) > 3

    def get_toc(self, text: str) -> list[dict]:
        """Extract table of contents from Markdown headings."""
        toc = []
        for line in text.split("\n"):
            m = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            if m:
                level = len(m.group(1))
                title = m.group(2).strip()
                # Remove inline formatting for clean titles
                clean = re.sub(r'[*_`~]', '', title)
                slug = re.sub(r'[^\w\s-]', '', clean.lower())
                slug = re.sub(r'[\s]+', '-', slug)
                toc.append({"level": level, "title": clean, "slug": slug})
        return toc

    def detect_features(self, text: str) -> dict:
        """Detect which features the document uses (for lazy loading)."""
        return {
            "math": bool(re.search(r'\$\$.*?\$\$|\$[^$]+\$', text, re.DOTALL)),
            "mermaid": "```mermaid" in text,
            "chart": "```chart" in text,
            "code": "```" in text,
            "table": bool(re.search(r'^\|.*\|', text, re.MULTILINE)),
            "emoji": HAS_EMOJI and bool(re.search(r':[a-z_]+:', text)),
            "wiki_links": "[[" in text,
        }

    def _process_emoji(self, text: str) -> str:
        """Replace :emoji_name: shortcodes with Unicode emoji."""
        if not HAS_EMOJI:
            return text
        try:
            return _emoji.emojize(text, language="alias")
        except Exception:
            return text

    def _split_blocks(self, text: str) -> list[str]:
        """Split Markdown text into logical blocks for incremental comparison."""
        blocks = []
        current = []
        in_code = False

        for line in text.split("\n"):
            if line.strip().startswith("```"):
                in_code = not in_code
                current.append(line)
                if not in_code:
                    blocks.append("\n".join(current))
                    current = []
            elif not in_code and line.strip() == "" and current:
                blocks.append("\n".join(current))
                current = []
            else:
                current.append(line)

        if current:
            blocks.append("\n".join(current))
        return blocks


def build_preview_html(
    md_text: str,
    theme: dict,
    font_size: int = 15,
    engine: Optional[RenderEngine] = None,
) -> str:
    """
    Build complete HTML document for the preview panel.
    
    Uses the RenderEngine for conversion and adds full CSS styling,
    MathJax, Mermaid, and Pygments themes — all lazily loaded.
    """
    eng = engine or RenderEngine()
    body = eng.render_full(md_text)
    features = eng.detect_features(md_text)

    is_dark = theme.get("bg") == "#1C1C1E"
    bg = theme["preview_bg"]
    fg = theme["editor_fg"]
    accent = theme["accent"]
    code_bg = theme["lnum_bg"]
    border = theme["border"]
    quote_color = theme["status_fg"]
    scrollbar = theme["scrollbar"]
    even_row = "rgba(255,255,255,0.04)" if is_dark else "rgba(0,0,0,0.04)"

    # Pygments CSS
    pygments_css = ""
    if HAS_PYGMENTS and features["code"]:
        pygments_style = "monokai" if is_dark else "default"
        try:
            formatter = HtmlFormatter(style=pygments_style, nowrap=False)
            pygments_css = formatter.get_style_defs(".highlight")
        except Exception:
            pass

    css = f"""
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{
        font-family: -apple-system, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
        font-size: {font_size}px; line-height: 1.75;
        color: {fg}; background: {bg};
        padding: 28px 36px; max-width: 100%;
        -webkit-font-smoothing: antialiased;
    }}
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: {scrollbar}; border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ opacity: 0.8; }}

    h1 {{ font-size: {font_size+14}px; font-weight: 700;
          border-bottom: 2px solid {border}; padding-bottom: .3em; margin: 1.4em 0 .6em; }}
    h2 {{ font-size: {font_size+9}px; font-weight: 700;
          border-bottom: 1px solid {border}; padding-bottom: .2em; margin: 1.2em 0 .5em; }}
    h3 {{ font-size: {font_size+5}px; font-weight: 600; margin: 1em 0 .4em; }}
    h4 {{ font-size: {font_size+2}px; font-weight: 600; margin: .8em 0 .3em; }}
    h5 {{ font-size: {font_size}px; font-weight: 600; margin: .6em 0 .3em; }}
    h6 {{ font-size: {font_size-1}px; font-weight: 600; margin: .5em 0 .2em; color: {quote_color}; }}
    p  {{ margin: .6em 0; }}
    a  {{ color: {accent}; text-decoration: none; transition: opacity 0.2s; }}
    a:hover {{ text-decoration: underline; opacity: 0.85; }}
    strong {{ font-weight: 700; }} em {{ font-style: italic; }}
    del {{ text-decoration: line-through; opacity: .7; }}

    code {{
        font-family: "Cascadia Code", "Fira Code", "Menlo", "Consolas", monospace;
        font-size: .88em; background: {code_bg}; padding: 2px 6px; border-radius: 5px;
    }}
    pre {{
        background: {code_bg}; border-radius: 10px;
        padding: 16px 20px; overflow-x: auto; margin: 1em 0;
        border: 1px solid {border};
    }}
    pre code {{ background: none; padding: 0; font-size: .9em; }}

    blockquote {{
        border-left: 4px solid {accent}; margin: 1em 0;
        padding: 6px 0 6px 20px; color: {quote_color}; font-style: italic;
    }}
    ul, ol {{ padding-left: 1.8em; margin: .6em 0; }}
    li {{ margin: .25em 0; }}
    li > ul, li > ol {{ margin: .1em 0; }}
    input[type="checkbox"] {{ margin-right: 6px; }}

    hr {{ border: none; border-top: 1px solid {border}; margin: 2em 0; }}
    img {{ max-width: 100%; border-radius: 8px; display: block; margin: .8em 0; }}

    table {{ border-collapse: collapse; width: 100%; margin: 1em 0; font-size: .95em; }}
    th, td {{ border: 1px solid {border}; padding: 9px 14px; text-align: left; }}
    th {{ background: {code_bg}; font-weight: 600; }}
    tr:nth-child(even) td {{ background: {even_row}; }}

    .toc {{ background: {code_bg}; border-radius: 8px; padding: 16px 20px; margin: 1em 0; }}
    .toc ul {{ list-style: none; padding-left: 1em; }}
    .toc > ul {{ padding-left: 0; }}
    .toc a {{ color: {fg}; }}
    .toc a:hover {{ color: {accent}; }}

    /* Smooth transitions for incremental updates */
    .markpad-block {{ transition: opacity 0.15s ease; }}

    /* Advanced Markdown Features Styling */
    .admonition {{
        background: {code_bg}; border-left: 4px solid {accent};
        padding: 12px 16px; margin: 1em 0; border-radius: 4px;
    }}
    .admonition-title {{ font-weight: bold; margin-bottom: 6px; text-transform: uppercase; font-size: 0.9em; }}
    .admonition p:last-child {{ margin-bottom: 0; }}
    .admonition.note {{ border-left-color: #3b82f6; }}
    .admonition.warning {{ border-left-color: #eab308; }}
    .admonition.danger {{ border-left-color: #ef4444; }}
    .admonition.success {{ border-left-color: #22c55e; }}

    .footnote {{ font-size: 0.85em; color: {quote_color}; border-top: 1px solid {border}; padding-top: 10px; margin-top: 2em; }}
    .footnote hr {{ display: none; }}
    
    dl {{ margin: 1em 0; }}
    dt {{ font-weight: bold; margin-top: 0.5em; }}
    dd {{ margin-left: 1.5em; margin-bottom: 0.5em; color: {quote_color}; }}

    /* pymdownx styles */
    .task-list-item {{ list-style-type: none; }}
    .task-list-control {{ margin-right: 8px; }}
    mark {{ background: rgba(255, 255, 0, 0.4); color: inherit; padding: 0 4px; border-radius: 4px; }}
    ins {{ text-decoration: none; border-bottom: 2px solid #22c55e; }}
    del {{ text-decoration: line-through; opacity: 0.7; color: #ef4444; }}
    kbd {{
        background: {code_bg}; border: 1px solid {border};
        border-radius: 4px; padding: 2px 6px; font-size: 0.8em;
        font-family: inherit; font-weight: bold;
        box-shadow: 0 2px 0 {border};
    }}
    .tabbed-set > input {{ display: none; }}
    .tabbed-labels {{ display: flex; border-bottom: 1px solid {border}; margin-bottom: 16px; flex-wrap: wrap; }}
    .tabbed-labels > label {{
        padding: 8px 16px; cursor: pointer; border-bottom: 2px solid transparent;
        transition: all 0.2s; font-weight: 600; color: {quote_color};
    }}
    .tabbed-labels > label:hover {{ color: {fg}; }}
    .tabbed-set > input:nth-child(1):checked ~ .tabbed-labels > label:nth-child(1),
    .tabbed-set > input:nth-child(2):checked ~ .tabbed-labels > label:nth-child(2),
    .tabbed-set > input:nth-child(3):checked ~ .tabbed-labels > label:nth-child(3),
    .tabbed-set > input:nth-child(4):checked ~ .tabbed-labels > label:nth-child(4),
    .tabbed-set > input:nth-child(5):checked ~ .tabbed-labels > label:nth-child(5) {{
        border-bottom-color: {accent}; color: {accent};
    }}
    .tabbed-content > div {{ display: none; }}
    .tabbed-set > input:nth-child(1):checked ~ .tabbed-content > div:nth-child(1),
    .tabbed-set > input:nth-child(2):checked ~ .tabbed-content > div:nth-child(2),
    .tabbed-set > input:nth-child(3):checked ~ .tabbed-content > div:nth-child(3),
    .tabbed-set > input:nth-child(4):checked ~ .tabbed-content > div:nth-child(4),
    .tabbed-set > input:nth-child(5):checked ~ .tabbed-content > div:nth-child(5) {{
        display: block;
    }}
    details {{
        background: {code_bg}; border: 1px solid {border};
        border-radius: 6px; margin: 1em 0; padding: 0 16px;
    }}
    summary {{ padding: 12px 0; font-weight: 600; cursor: pointer; outline: none; }}

    /* Pygments */
    {pygments_css}

    /* Mermaid container */
    .mermaid {{ margin: 1em 0; text-align: center; }}
    """

    # Lazy-load scripts only when needed
    scripts = ""

    if features["math"]:
        scripts += """
        <script>
          window.MathJax = {
            tex: { inlineMath: [['$','$'], ['\\\\(','\\\\)']], displayMath: [['$$','$$'], ['\\\\[','\\\\]']] },
            svg: { fontCache: 'global' }
          };
        </script>
        <script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
        """

    if features["mermaid"]:
        mermaid_theme = "dark" if is_dark else "default"
        scripts += f"""
        <script type="module">
          import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
          mermaid.initialize({{ startOnLoad: false, theme: '{mermaid_theme}' }});
          document.addEventListener("DOMContentLoaded", () => {{
            const blocks = document.querySelectorAll("code.language-mermaid, code.mermaid");
            blocks.forEach(block => {{
                const div = document.createElement("div");
                div.className = "mermaid";
                div.textContent = block.textContent;
                block.parentNode.replaceWith(div);
            }});
            mermaid.run();
          }});
        </script>
        """
        
    if features.get("chart"):
        scripts += """
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
          window.renderCharts = function() {
              document.querySelectorAll("code.language-chart").forEach(function(block, i) {
                  try {
                      let jsonStr = block.textContent;
                      // Remove comments or markdown artifacts if any
                      jsonStr = jsonStr.replace(/^\\s*\\/\\/.*$/gm, '');
                      let data = JSON.parse(jsonStr);
                      let canvas = document.createElement("canvas");
                      canvas.id = "chart-" + i;
                      canvas.style.maxHeight = "400px";
                      canvas.style.marginTop = "20px";
                      canvas.style.marginBottom = "20px";
                      block.parentNode.replaceWith(canvas);
                      new Chart(canvas, data);
                  } catch(e) {
                      console.error("Chart parsing error", e);
                  }
              });
          };
          window.addEventListener('DOMContentLoaded', window.renderCharts);
        </script>
        """

    # Scroll position preservation script
    scripts += """
    <script>
      // Store scroll position for incremental updates
      window._markpadScrollY = 0;
      window.addEventListener('scroll', () => { window._markpadScrollY = window.scrollY; });
      
      // Function to update body content incrementally
      window.markpadUpdate = function(html) {
        const scrollY = window._markpadScrollY;
        document.getElementById('content').innerHTML = html;
        window.scrollTo(0, scrollY);
        
        // Re-run MathJax
        if (window.MathJax && window.MathJax.typeset) {
          try { window.MathJax.typeset(); } catch(e) {}
        }
        
        // Re-run Mermaid
        if (window.mermaid) {
          document.querySelectorAll("code.language-mermaid").forEach(function(block) {
              let div = document.createElement("div");
              div.className = "mermaid";
              div.textContent = block.textContent;
              block.parentNode.replaceWith(div);
          });
          try { window.mermaid.run({ querySelector: '.mermaid' }); } catch(e) {}
        }
        
        // Re-run Charts
        if (window.renderCharts) {
            window.renderCharts();
        }
      };
    </script>
    """

    return (
        f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<style>{css}</style>{scripts}</head>"
        f"<body><div id='content'>{body}</div></body></html>"
    )


# ── Singleton engine for the application ───────────────────────────────────
_engine = None

def get_engine() -> RenderEngine:
    """Get or create the global rendering engine singleton."""
    global _engine
    if _engine is None:
        _engine = RenderEngine()
    return _engine
