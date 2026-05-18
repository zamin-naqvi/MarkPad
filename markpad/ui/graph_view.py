"""
Interactive Graph View for MarkPad — D3.js force-directed graph.

Features:
  - Fully draggable and zoomable nodes
  - Scans vault directory for all .md files
  - Parses [[wiki-links]] and [](standard-links)
  - Click nodes to navigate to files
  - Resizable dialog
  - Physics simulation with collision detection
"""

import json
import os
import re
from typing import Optional

from PyQt6.QtWidgets import QDialog, QVBoxLayout
from PyQt6.QtCore import QUrl

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False

from markpad.utils.helpers import find_md_files, extract_links


def _build_graph_data(current_file: Optional[str], current_text: str, vault_dir: Optional[str] = None):
    """Build nodes and edges data for the graph."""
    nodes = []
    edges = []
    node_ids = set()

    current_name = os.path.basename(current_file) if current_file else "Untitled"
    nodes.append({"id": current_name, "label": current_name, "group": "current", "path": current_file or ""})
    node_ids.add(current_name)

    # Extract links from current document
    links = extract_links(current_text)
    for link in links:
        fname = link["label"] if link["type"] == "wiki" else os.path.basename(link["url"])
        if fname.startswith("http"):
            continue
        if fname not in node_ids:
            nodes.append({"id": fname, "label": fname, "group": "linked", "path": ""})
            node_ids.add(fname)
        edges.append({"source": current_name, "target": fname})

    # Scan vault for backlinks
    if vault_dir and os.path.isdir(vault_dir):
        md_files = find_md_files(vault_dir)
        for md_path in md_files:
            if md_path == current_file:
                continue
            md_name = os.path.basename(md_path)
            try:
                with open(md_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(10000)  # Read first 10KB only for speed
            except (IOError, PermissionError):
                continue

            file_links = extract_links(content)
            has_link_to_current = False
            for link in file_links:
                target = link["label"] if link["type"] == "wiki" else os.path.basename(link["url"])
                if target == current_name or target == os.path.splitext(current_name)[0]:
                    has_link_to_current = True
                    break

            if has_link_to_current:
                if md_name not in node_ids:
                    nodes.append({"id": md_name, "label": md_name, "group": "backlink", "path": md_path})
                    node_ids.add(md_name)
                edges.append({"source": md_name, "target": current_name})

    return nodes, edges


def _build_graph_html(nodes, edges, theme):
    """Build the D3.js graph HTML."""
    is_dark = theme.get("bg") == "#1C1C1E"
    bg = theme["bg"]
    fg = theme["editor_fg"]
    accent = theme["accent"]
    border = theme["border"]

    nodes_json = json.dumps(nodes)
    edges_json = json.dumps(edges)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ background: {bg}; overflow: hidden; font-family: -apple-system, "Segoe UI", sans-serif; }}
    svg {{ width: 100vw; height: 100vh; }}
    .node-circle {{ cursor: grab; transition: r 0.2s; }}
    .node-circle:hover {{ filter: brightness(1.2); }}
    .node-circle:active {{ cursor: grabbing; }}
    .node-label {{ fill: {fg}; font-size: 12px; pointer-events: none; user-select: none; }}
    .link {{ stroke: {border}; stroke-opacity: 0.6; stroke-width: 1.5px; }}
    .controls {{
        position: fixed; bottom: 16px; right: 16px;
        display: flex; gap: 8px; z-index: 10;
    }}
    .ctrl-btn {{
        width: 36px; height: 36px; border-radius: 8px;
        background: {"#3A3A3C" if is_dark else "#FFFFFF"};
        border: 1px solid {border}; color: {fg};
        font-size: 18px; cursor: pointer; display: flex;
        align-items: center; justify-content: center;
        transition: background 0.15s;
    }}
    .ctrl-btn:hover {{ background: {"#48484A" if is_dark else "#E5E5EA"}; }}
    .info {{
        position: fixed; top: 12px; left: 16px; color: {fg};
        font-size: 11px; opacity: 0.6;
    }}
</style>
</head>
<body>
<div class="info">Drag nodes to reposition • Scroll to zoom • Click to select</div>
<div class="controls">
    <button class="ctrl-btn" onclick="zoomIn()" title="Zoom In">+</button>
    <button class="ctrl-btn" onclick="zoomOut()" title="Zoom Out">−</button>
    <button class="ctrl-btn" onclick="resetZoom()" title="Reset">⟳</button>
</div>
<svg id="graph"></svg>

<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
const nodes = {nodes_json};
const links = {edges_json};
const width = window.innerWidth;
const height = window.innerHeight;

const colorMap = {{
    current: "{accent}",
    linked: "{"#6B7280" if not is_dark else "#9CA3AF"}",
    backlink: "{"#10B981" if not is_dark else "#34D399"}"
}};
const sizeMap = {{ current: 14, linked: 8, backlink: 9 }};

const svg = d3.select("#graph");
const g = svg.append("g");

// Zoom behavior
const zoom = d3.zoom()
    .scaleExtent([0.2, 5])
    .on("zoom", (event) => g.attr("transform", event.transform));
svg.call(zoom);

window.zoomIn = () => svg.transition().duration(300).call(zoom.scaleBy, 1.4);
window.zoomOut = () => svg.transition().duration(300).call(zoom.scaleBy, 0.7);
window.resetZoom = () => svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity);

// Simulation
const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id).distance(100).strength(0.5))
    .force("charge", d3.forceManyBody().strength(-300))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide().radius(d => sizeMap[d.group] + 20))
    .force("x", d3.forceX(width / 2).strength(0.05))
    .force("y", d3.forceY(height / 2).strength(0.05));

// Links
const link = g.append("g")
    .selectAll("line")
    .data(links)
    .join("line")
    .attr("class", "link");

// Node groups
const node = g.append("g")
    .selectAll("g")
    .data(nodes)
    .join("g")
    .call(d3.drag()
        .on("start", dragStarted)
        .on("drag", dragged)
        .on("end", dragEnded));

// Circles
node.append("circle")
    .attr("class", "node-circle")
    .attr("r", d => sizeMap[d.group] || 8)
    .attr("fill", d => colorMap[d.group] || "#888")
    .attr("stroke", d => d.group === "current" ? "{accent}" : "transparent")
    .attr("stroke-width", d => d.group === "current" ? 3 : 0);

// Glow for current node
node.filter(d => d.group === "current")
    .append("circle")
    .attr("r", 22)
    .attr("fill", "none")
    .attr("stroke", "{accent}")
    .attr("stroke-width", 1)
    .attr("opacity", 0.3);

// Labels
node.append("text")
    .attr("class", "node-label")
    .attr("dy", d => -(sizeMap[d.group] + 8))
    .attr("text-anchor", "middle")
    .text(d => d.label.replace(/\\.md$/, ""));

simulation.on("tick", () => {{
    link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);
    node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
}});

function dragStarted(event, d) {{
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x; d.fy = d.y;
}}
function dragged(event, d) {{
    d.fx = event.x; d.fy = event.y;
}}
function dragEnded(event, d) {{
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null; d.fy = null;
}}

// Initial zoom to fit
svg.call(zoom.transform, d3.zoomIdentity.translate(0, 0).scale(1));
</script>
</body>
</html>"""


def show_graph_view(parent, current_file, current_text, theme, vault_dir=None):
    """Show the interactive graph view dialog."""
    if not HAS_WEBENGINE:
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.warning(parent, "Graph View", "Graph View requires PyQt6-WebEngine.")
        return

    if vault_dir is None and current_file:
        vault_dir = os.path.dirname(current_file)

    nodes, edges = _build_graph_data(current_file, current_text, vault_dir)

    html = _build_graph_html(nodes, edges, theme)

    dlg = QDialog(parent)
    dlg.setWindowTitle("Graph View — MarkPad")
    dlg.resize(900, 650)
    dlg.setMinimumSize(500, 400)
    dlg_lay = QVBoxLayout(dlg)
    dlg_lay.setContentsMargins(0, 0, 0, 0)
    web = QWebEngineView()
    web.setHtml(html)
    dlg_lay.addWidget(web)
    dlg.exec()
