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

SAMPLE_DOCUMENT = r"""\
# 🖊 MarkPad — Complete Feature Showcase

> A **beautiful**, *feature-rich* Markdown editor with live preview, charts, math, diagrams and more.
> Edit on the left — see magic on the right. ✨

---

## 📝 Text Formatting

**Bold text** | *Italic text* | ***Bold + Italic*** | ~~Strikethrough~~ | `inline code`

You can combine them: ***bold italic*** and ~~**bold strikethrough**~~ and `code with *markdown*`.

Footnotes are supported too[^1] and so is <mark>highlighted text</mark> via HTML inline.

[^1]: This is a footnote at the bottom of the document.

---

## 📋 Lists & Nesting

### Unordered
- 🍎 Apples
  - Granny Smith
  - Fuji
    - Seedless variant
- 🍊 Oranges
- 🍇 Grapes

### Ordered
1. Install Python 3.12+
2. Install PyQt6 via pip
3. Run `markpad.py`
4. Enjoy ✅

### Task List
- [x] Add MathJax support
- [x] Add Mermaid diagrams
- [x] Add Chart.js integration
- [ ] Dark mode themes
- [ ] Vim keybindings

---

## 💬 Blockquotes

> "Simplicity is the ultimate sophistication." — *Leonardo da Vinci*

> **Nested quotes work too:**
>
> > "Any sufficiently advanced technology is indistinguishable from magic." — *Arthur C. Clarke*
> >
> > > And you can go three levels deep.

---

## 💻 Code Blocks

### Python

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"

class MarkdownParser:
    def __init__(self, text: str):
        self.text = text
        self.tokens = []

    def parse(self) -> list:
        for line in self.text.splitlines():
            if line.startswith("#"):
                self.tokens.append(("heading", line))
            elif line.startswith(">"):
                self.tokens.append(("blockquote", line))
            else:
                self.tokens.append(("paragraph", line))
        return self.tokens
```

### JavaScript

```javascript
const renderMarkdown = async (text) => {
  const response = await fetch('/api/render', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ markdown: text }),
  });
  const { html } = await response.json();
  document.getElementById('preview').innerHTML = html;
};
```

### SQL

```sql
SELECT
    u.name,
    COUNT(d.id) AS doc_count,
    MAX(d.updated_at) AS last_edited
FROM users u
LEFT JOIN documents d ON d.user_id = u.id
WHERE u.active = TRUE
GROUP BY u.name
ORDER BY doc_count DESC
LIMIT 10;
```

### Bash

```bash
#!/bin/bash
echo "Setting up MarkPad..."
pip install PyQt6 PyQt6-WebEngine markdown
python3 markpad.py &
echo "MarkPad is running on PID $!"
```

### JSON

```json
{
  "app": "MarkPad",
  "version": "2.0.0",
  "features": ["mathJax", "mermaid", "charts", "pdfExport"],
  "theme": {
    "font": "JetBrains Mono",
    "background": "#1e1e2e",
    "accent": "#cba6f7"
  }
}
```

---

## ∑ Math — MathJax / LaTeX

### Einstein's Mass-Energy Equivalence

$$ E = mc^2 $$

### Definite Integral

$$ \int_{a}^{b} x^2 \,dx = \frac{b^3 - a^3}{3} $$

### Euler's Identity

$$ e^{i\pi} + 1 = 0 $$

### Gaussian / Normal Distribution

$$ f(x) = \frac{1}{\sigma\sqrt{2\pi}} \, e^{-\frac{(x-\mu)^2}{2\sigma^2}} $$

### Fourier Transform

$$ \hat{f}(\xi) = \int_{-\infty}^{\infty} f(x)\, e^{-2\pi i x \xi} \, dx $$

### Matrix Multiplication

$$
A \cdot B = \begin{pmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{pmatrix}
\begin{pmatrix} b_{11} & b_{12} \\ b_{21} & b_{22} \end{pmatrix}
=
\begin{pmatrix}
a_{11}b_{11}+a_{12}b_{21} & a_{11}b_{12}+a_{12}b_{22} \\
a_{21}b_{11}+a_{22}b_{21} & a_{21}b_{12}+a_{22}b_{22}
\end{pmatrix}
$$

### Summation

$$ \sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6} $$

### Quadratic Formula

$$ x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a} $$

---

## 🔀 Diagrams — Mermaid.js

### Flowchart — Markdown Render Pipeline

```mermaid
graph TD
    A([📝 Raw Markdown]) --> B[Lexer / Tokeniser]
    B --> C[AST Builder]
    C --> D{Node Type?}
    D -->|Heading| E[H1–H6 Tag]
    D -->|Paragraph| F[P Tag]
    D -->|Code| G[Syntax Highlighter]
    D -->|Math| H[MathJax Renderer]
    D -->|Mermaid| I[Diagram Renderer]
    E & F & G & H & I --> J[HTML Assembly]
    J --> K([🌐 Live Preview])
```

### Sequence Diagram — API Call Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant E as ✏️ Editor
    participant P as 🔄 Parser
    participant R as 🖥 Renderer
    participant W as 🌐 WebView

    U->>E: Type Markdown
    E->>P: Debounce 300ms → parse()
    P->>P: Tokenise & build AST
    P-->>R: AST nodes
    R->>R: Convert to HTML + inject MathJax
    R-->>W: Rendered HTML
    W->>W: Re-run MathJax + Mermaid
    W-->>U: Live Preview ✅
```

### Gantt Chart — Development Timeline

```mermaid
gantt
    title MarkPad Development Roadmap
    dateFormat  YYYY-MM-DD
    section Core
    Editor & Preview        :done,    e1, 2024-01-01, 2024-01-14
    Syntax Highlighting     :done,    e2, 2024-01-10, 2024-01-20
    Toolbar & Shortcuts     :done,    e3, 2024-01-18, 2024-01-28
    section Rendering
    MathJax Integration     :done,    r1, 2024-01-20, 2024-02-05
    Mermaid Diagrams        :done,    r2, 2024-02-01, 2024-02-15
    Chart.js Support        :active,  r3, 2024-02-10, 2024-03-01
    section Export
    PDF Export              :         p1, 2024-02-25, 2024-03-10
    HTML Export             :         p2, 2024-03-05, 2024-03-20
    section v2.0
    Dark Themes             :         t1, 2024-03-15, 2024-04-01
    Plugin System           :         t2, 2024-03-25, 2024-04-20
```

### State Diagram — Document Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Untitled : Launch app

    Untitled --> Editing : User types
    Editing --> Editing : Keep typing
    Editing --> Saved : Ctrl+S
    Saved --> Editing : Modify file
    Saved --> Exported : File > Export PDF
    Exported --> Saved : Return to editor
    Editing --> Closed : Ctrl+Q (no changes)
    Saved --> Closed : Ctrl+Q
    Closed --> [*]
```

### Class Diagram — Editor Architecture

```mermaid
classDiagram
    class MarkPad {
        +String title
        +QMainWindow window
        +launch()
        +openFile()
        +saveFile()
        +exportPDF()
    }
    class Editor {
        +String content
        +QFont font
        +int fontSize
        +onTextChanged()
        +insertBold()
        +insertItalic()
        +insertTable()
    }
    class Preview {
        +QWebEngineView view
        +String html
        +render(markdown)
        +scrollSync()
        +injectMathJax()
    }
    class Parser {
        +String raw
        +parse() String
        +highlight() String
        +buildHTML() String
    }

    MarkPad --> Editor : contains
    MarkPad --> Preview : contains
    Editor --> Parser : triggers
    Parser --> Preview : feeds HTML
```

### ER Diagram — Document Database

```mermaid
erDiagram
    USER {
        int id PK
        string name
        string email
        datetime created_at
    }
    DOCUMENT {
        int id PK
        int user_id FK
        string title
        text content
        datetime updated_at
        bool is_starred
    }
    TAG {
        int id PK
        string label
        string color
    }
    DOCUMENT_TAG {
        int doc_id FK
        int tag_id FK
    }

    USER ||--o{ DOCUMENT : "owns"
    DOCUMENT }o--o{ TAG : "tagged with"
    DOCUMENT_TAG }|--|| DOCUMENT : "links"
    DOCUMENT_TAG }|--|| TAG : "links"
```

### Pie Chart — Feature Usage

```mermaid
pie title Most-Used MarkPad Features
    "Live Preview" : 38
    "Math / LaTeX" : 22
    "Mermaid Diagrams" : 18
    "Code Blocks" : 12
    "PDF Export" : 10
```

### Mind Map — Markdown Ecosystem

```mermaid
mindmap
  root((Markdown))
    Flavours
      CommonMark
      GitHub Flavoured
      MultiMarkdown
      Pandoc
    Tools
      MarkPad
      Obsidian
      Typora
      VS Code
    Output
      HTML
      PDF
      Slides
      eBook
    Extensions
      MathJax
      Mermaid
      Chart.js
      Highlight.js
```

### Git Graph — Version History

```mermaid
gitGraph
    commit id: "Initial commit"
    commit id: "Add editor pane"
    branch feature/preview
    checkout feature/preview
    commit id: "Add WebView"
    commit id: "Live render"
    checkout main
    merge feature/preview id: "Merge preview"
    branch feature/math
    checkout feature/math
    commit id: "Integrate MathJax"
    commit id: "LaTeX rendering"
    checkout main
    merge feature/math id: "Merge math"
    commit id: "v1.0 release 🎉"
    branch feature/charts
    checkout feature/charts
    commit id: "Chart.js bar"
    commit id: "Add pie + radar"
    checkout main
    merge feature/charts id: "v2.0 release 🚀"
```

---

## 📊 Charts — Chart.js

### Bar Chart — Monthly Active Users

```chartjs
{
  "type": "bar",
  "data": {
    "labels": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
    "datasets": [{
      "label": "Active Users",
      "data": [1200,1900,1500,2100,2400,2800,3100,2900,3400,3800,4100,4600],
      "backgroundColor": "rgba(99,102,241,0.7)",
      "borderColor": "rgb(99,102,241)",
      "borderWidth": 2,
      "borderRadius": 6
    }]
  },
  "options": {
    "plugins": {"title": {"display": true, "text": "Monthly Active Users 2024"}},
    "scales": {"y": {"beginAtZero": true}}
  }
}
```

### Line Chart — Revenue vs Expenses

```chartjs
{
  "type": "line",
  "data": {
    "labels": ["Q1","Q2","Q3","Q4"],
    "datasets": [
      {
        "label": "Revenue ($k)",
        "data": [42, 68, 91, 130],
        "borderColor": "rgb(16,185,129)",
        "backgroundColor": "rgba(16,185,129,0.1)",
        "tension": 0.4,
        "fill": true
      },
      {
        "label": "Expenses ($k)",
        "data": [38, 52, 61, 74],
        "borderColor": "rgb(239,68,68)",
        "backgroundColor": "rgba(239,68,68,0.1)",
        "tension": 0.4,
        "fill": true
      }
    ]
  },
  "options": {
    "plugins": {"title": {"display": true, "text": "Revenue vs Expenses by Quarter"}}
  }
}
```

### Pie Chart — Market Share

```chartjs
{
  "type": "pie",
  "data": {
    "labels": ["MarkPad","Obsidian","Typora","VS Code","Other"],
    "datasets": [{
      "data": [28, 35, 15, 12, 10],
      "backgroundColor": [
        "rgba(99,102,241,0.8)",
        "rgba(16,185,129,0.8)",
        "rgba(245,158,11,0.8)",
        "rgba(239,68,68,0.8)",
        "rgba(156,163,175,0.8)"
      ],
      "borderWidth": 2
    }]
  },
  "options": {
    "plugins": {"title": {"display": true, "text": "Markdown Editor Market Share"}}
  }
}
```

### Doughnut Chart — Feature Distribution

```chartjs
{
  "type": "doughnut",
  "data": {
    "labels": ["Editor","Preview","Export","Diagrams","Math","Themes"],
    "datasets": [{
      "data": [20, 25, 15, 18, 14, 8],
      "backgroundColor": [
        "#6366f1","#06b6d4","#10b981","#f59e0b","#ef4444","#8b5cf6"
      ],
      "hoverOffset": 8
    }]
  },
  "options": {
    "plugins": {"title": {"display": true, "text": "Codebase by Feature Area (%)"}},
    "cutout": "60%"
  }
}
```

### Radar Chart — Editor Comparison

```chartjs
{
  "type": "radar",
  "data": {
    "labels": ["Speed","Features","Design","Math","Diagrams","Export"],
    "datasets": [
      {
        "label": "MarkPad",
        "data": [95, 90, 92, 98, 97, 88],
        "borderColor": "rgb(99,102,241)",
        "backgroundColor": "rgba(99,102,241,0.2)"
      },
      {
        "label": "Obsidian",
        "data": [80, 95, 85, 70, 80, 75],
        "borderColor": "rgb(16,185,129)",
        "backgroundColor": "rgba(16,185,129,0.2)"
      },
      {
        "label": "Typora",
        "data": [88, 78, 95, 60, 50, 82],
        "borderColor": "rgb(245,158,11)",
        "backgroundColor": "rgba(245,158,11,0.2)"
      }
    ]
  },
  "options": {
    "plugins": {"title": {"display": true, "text": "Editor Comparison Radar"}},
    "scales": {"r": {"min": 0, "max": 100}}
  }
}
```

### Polar Area Chart — Bug Distribution

```chartjs
{
  "type": "polarArea",
  "data": {
    "labels": ["UI","Parser","Export","Network","Math","Diagrams"],
    "datasets": [{
      "data": [12, 8, 5, 3, 6, 4],
      "backgroundColor": [
        "rgba(99,102,241,0.7)",
        "rgba(239,68,68,0.7)",
        "rgba(245,158,11,0.7)",
        "rgba(16,185,129,0.7)",
        "rgba(139,92,246,0.7)",
        "rgba(6,182,212,0.7)"
      ]
    }]
  },
  "options": {
    "plugins": {"title": {"display": true, "text": "Open Bug Count by Module"}}
  }
}
```

### Scatter Plot — Performance Benchmarks

```chartjs
{
  "type": "scatter",
  "data": {
    "datasets": [
      {
        "label": "Parse Time",
        "data": [
          {"x":100,"y":12},{"x":500,"y":45},{"x":1000,"y":89},
          {"x":2000,"y":162},{"x":5000,"y":390},{"x":10000,"y":810}
        ],
        "backgroundColor": "rgba(99,102,241,0.7)"
      },
      {
        "label": "Render Time",
        "data": [
          {"x":100,"y":20},{"x":500,"y":78},{"x":1000,"y":142},
          {"x":2000,"y":260},{"x":5000,"y":610},{"x":10000,"y":1250}
        ],
        "backgroundColor": "rgba(239,68,68,0.7)"
      }
    ]
  },
  "options": {
    "plugins": {"title": {"display": true, "text": "Performance: Word Count vs Time (ms)"}},
    "scales": {
      "x": {"title": {"display": true, "text": "Word Count"}},
      "y": {"title": {"display": true, "text": "Time (ms)"}}
    }
  }
}
```

### Bubble Chart — Repository Activity

```chartjs
{
  "type": "bubble",
  "data": {
    "datasets": [
      {
        "label": "MarkPad",
        "data": [{"x": 12, "y": 480, "r": 20}],
        "backgroundColor": "rgba(99,102,241,0.7)"
      },
      {
        "label": "Obsidian",
        "data": [{"x": 48, "y": 1200, "r": 35}],
        "backgroundColor": "rgba(16,185,129,0.7)"
      },
      {
        "label": "Typora",
        "data": [{"x": 8, "y": 320, "r": 14}],
        "backgroundColor": "rgba(245,158,11,0.7)"
      },
      {
        "label": "Zettlr",
        "data": [{"x": 22, "y": 650, "r": 18}],
        "backgroundColor": "rgba(239,68,68,0.7)"
      },
      {
        "label": "Mark Text",
        "data": [{"x": 6, "y": 210, "r": 11}],
        "backgroundColor": "rgba(139,92,246,0.7)"
      }
    ]
  },
  "options": {
    "plugins": {"title": {"display": true, "text": "Editors: Commits × Stars (bubble = contributors)"}},
    "scales": {
      "x": {"title": {"display": true, "text": "Monthly Commits"}},
      "y": {"title": {"display": true, "text": "GitHub Stars (hundreds)"}}
    }
  }
}
```

### Mixed Bar + Line Chart — Downloads & Growth Rate

```chartjs
{
  "type": "bar",
  "data": {
    "labels": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
    "datasets": [
      {
        "type": "bar",
        "label": "Downloads",
        "data": [800,1100,1300,1700,2100,2600,3000,3400,3900,4500,5200,6100],
        "backgroundColor": "rgba(99,102,241,0.6)",
        "borderRadius": 4,
        "yAxisID": "y"
      },
      {
        "type": "line",
        "label": "MoM Growth %",
        "data": [0,37,18,30,23,23,15,13,14,15,15,17],
        "borderColor": "rgb(245,158,11)",
        "backgroundColor": "rgba(245,158,11,0.1)",
        "tension": 0.4,
        "yAxisID": "y1"
      }
    ]
  },
  "options": {
    "plugins": {"title": {"display": true, "text": "Monthly Downloads + Growth Rate"}},
    "scales": {
      "y":  {"position": "left",  "title": {"display": true, "text": "Downloads"}},
      "y1": {"position": "right", "title": {"display": true, "text": "Growth %"},
             "grid": {"drawOnChartArea": false}}
    }
  }
}
```

---

## 📊 Tables

### Feature Matrix

| Feature           | Shortcut      | Markdown | Status  |
|-------------------|---------------|----------|---------|
| Bold              | `Ctrl+B`      | `**...**`| ✅ Done |
| Italic            | `Ctrl+I`      | `*...*`  | ✅ Done |
| Strikethrough     | `Ctrl+Shift+S`| `~~...~~`| ✅ Done |
| Inline Code       | `` Ctrl+` ``  | `` `...` ``| ✅ Done |
| Heading 1         | `Ctrl+1`      | `# ...`  | ✅ Done |
| Insert Table      | `Ctrl+T`      | `| ... |`| ✅ Done |
| PDF Export        | `Ctrl+Shift+E`| —        | ✅ Done |
| Math (MathJax)    | —             | `$$ ... $$`| ✅ Done |
| Diagrams (Mermaid)| —             | ` ```mermaid `| ✅ Done |
| Charts (Chart.js) | —             | ` ```chartjs `| ✅ Done |

### Keyboard Shortcuts Reference

| Action             | macOS           | Windows/Linux   |
|--------------------|-----------------|-----------------|
| New File           | `⌘ N`           | `Ctrl+N`        |
| Open File          | `⌘ O`           | `Ctrl+O`        |
| Save               | `⌘ S`           | `Ctrl+S`        |
| Save As            | `⌘ ⇧ S`         | `Ctrl+Shift+S`  |
| Export PDF         | `⌘ ⇧ E`         | `Ctrl+Shift+E`  |
| Bold               | `⌘ B`           | `Ctrl+B`        |
| Italic             | `⌘ I`           | `Ctrl+I`        |
| Find               | `⌘ F`           | `Ctrl+F`        |
| Toggle Preview     | `⌘ P`           | `Ctrl+P`        |
| Increase Font      | `⌘ +`           | `Ctrl++`        |
| Decrease Font      | `⌘ −`           | `Ctrl+-`        |
| Reset Font         | `⌘ 0`           | `Ctrl+0`        |

### Supported Mermaid Diagram Types

| Type           | Keyword      | Use Case                          |
|----------------|--------------|-----------------------------------|
| Flowchart      | `graph`      | Logic flows, pipelines            |
| Sequence       | `sequenceDiagram` | API calls, protocols         |
| Gantt          | `gantt`      | Project timelines                 |
| Class          | `classDiagram`| OOP architecture                 |
| State          | `stateDiagram-v2`| State machines               |
| ER             | `erDiagram`  | Database schemas                  |
| Pie            | `pie`        | Part-to-whole proportions         |
| Mind Map       | `mindmap`    | Brainstorming, concept maps       |
| Git Graph      | `gitGraph`   | Branch & merge history            |
| Timeline       | `timeline`   | Historical sequences              |

---

## 📐 Typography Scale

# Heading 1 — 2.5rem, bold
## Heading 2 — 2rem, bold
### Heading 3 — 1.75rem, semi-bold
#### Heading 4 — 1.5rem, semi-bold
##### Heading 5 — 1.25rem, medium
###### Heading 6 — 1rem, medium

---

## 🔗 Links & Images

[Visit Anthropic](https://www.anthropic.com) | [GitHub](https://github.com) | [CommonMark Spec](https://spec.commonmark.org)

Images use the same syntax with a `!` prefix:
`![Alt text](https://via.placeholder.com/400x200 "Optional title")`

---

## 📌 Horizontal Rules

Three ways to draw one:

---
***
___

---

## 🌐 HTML Inside Markdown

<details>
<summary>Click to expand a hidden section</summary>

This content is hidden by default. You can put **markdown** *inside* HTML blocks!

```python
print("Hidden code block!")
```
</details>

<br>

<kbd>Ctrl</kbd> + <kbd>S</kbd> to save &nbsp;&nbsp; | &nbsp;&nbsp; <kbd>⌘</kbd> + <kbd>P</kbd> to preview

---

## 🧮 More Math

### Taylor Series Expansion

$$ e^x = \sum_{n=0}^{\infty} \frac{x^n}{n!} = 1 + x + \frac{x^2}{2!} + \frac{x^3}{3!} + \cdots $$

### Bayes' Theorem

$$ P(A \mid B) = \frac{P(B \mid A)\, P(A)}{P(B)} $$

### Navier–Stokes (Incompressible Flow)

$$ \rho \left(\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla)\mathbf{u}\right) = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f} $$

### Maxwell's Equations (Differential Form)

$$\nabla \cdot \mathbf{E} = \frac{\rho}{\varepsilon_0}$$

$$\nabla \cdot \mathbf{B} = 0$$

$$\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}$$

$$\nabla \times \mathbf{B} = \mu_0 \mathbf{J} + \mu_0\varepsilon_0 \frac{\partial \mathbf{E}}{\partial t}$$

---

## 📖 Extended Blockquotes

> ### On Writing
> Writing is thinking. To write well is to think clearly.
> That's why it's so hard.
>
> — *David McCullough*

> ### On Software
> Programs must be written for people to read, and only incidentally for machines to execute.
>
> — *Harold Abelson, SICP*

---

*Edit here — preview updates live!* 🚀

[^1]: Footnote support depends on the Markdown flavour / parser in use.
"""
