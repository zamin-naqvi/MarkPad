"""
Miscellaneous helper utilities.
"""

import os
import re
from typing import Optional


def word_count(text: str) -> int:
    """Count words in text."""
    return len(text.split()) if text.strip() else 0


def char_count(text: str) -> int:
    """Count characters in text."""
    return len(text)


def reading_time(text: str, wpm: int = 200) -> str:
    """Estimate reading time based on average words per minute."""
    words = word_count(text)
    minutes = max(1, round(words / wpm))
    if minutes == 1:
        return "1 min read"
    return f"{minutes} min read"


def extract_links(text: str) -> list[dict]:
    """Extract all Markdown links from text."""
    results = []
    # Standard links: [label](url)
    for m in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', text):
        results.append({"label": m.group(1), "url": m.group(2), "type": "standard"})
    # Wiki links: [[page]]
    for m in re.finditer(r'\[\[([^\]]+)\]\]', text):
        results.append({"label": m.group(1), "url": m.group(1), "type": "wiki"})
    return results


def find_md_files(directory: str) -> list[str]:
    """Recursively find all Markdown files in a directory."""
    md_files = []
    try:
        for root, dirs, files in os.walk(directory):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for f in files:
                if f.lower().endswith(('.md', '.markdown', '.txt')):
                    md_files.append(os.path.join(root, f))
    except PermissionError:
        pass
    return md_files


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[\s]+', '-', text).strip('-')


SNIPPET_TEMPLATES = {
    "Table": (
        "| Column 1 | Column 2 | Column 3 |\n"
        "|----------|----------|----------|\n"
        "| Data     | Data     | Data     |\n"
        "| Data     | Data     | Data     |\n"
    ),
    "Code Block (Python)": "```python\n# Your code here\n\n```\n",
    "Code Block (JavaScript)": "```javascript\n// Your code here\n\n```\n",
    "Code Block (Bash)": "```bash\n# Your command here\n\n```\n",
    "Mermaid Flowchart": (
        "```mermaid\ngraph TD;\n"
        "    A[Start] --> B{Decision};\n"
        "    B -->|Yes| C[Action 1];\n"
        "    B -->|No| D[Action 2];\n```\n"
    ),
    "Mermaid Sequence": (
        "```mermaid\nsequenceDiagram\n"
        "    Alice->>Bob: Hello Bob\n"
        "    Bob-->>Alice: Hi Alice\n```\n"
    ),
    "Math Equation": "$$ f(x) = \\frac{1}{\\sqrt{2\\pi}} e^{-\\frac{x^2}{2}} $$\n",
    "Task List": "- [ ] Task 1\n- [ ] Task 2\n- [x] Completed task\n",
    "Footnote": "Text with a footnote[^1]\n\n[^1]: Footnote content here.\n",
    "Details/Collapse": "<details>\n<summary>Click to expand</summary>\n\nHidden content here.\n\n</details>\n",
    "Image with Caption": "![Alt text](image.png)\n*Caption: Image description*\n",
    "Horizontal Rule": "\n---\n",
    "Blockquote": "> Your quote here\n>\n> — Author\n",
    "Definition List": "Term\n:   Definition goes here\n",
}
