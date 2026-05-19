import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox
from PyQt6.QtCore import Qt

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEnginePage
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False

class MindMapEditorPage(QWebEnginePage):
    def __init__(self, parent_panel):
        super().__init__(parent_panel)
        self.panel = parent_panel

    def javaScriptAlert(self, securityOrigin, msg):
        if msg.startswith("SAVE_MARKDOWN:"):
            md_text = msg.split("SAVE_MARKDOWN:", 1)[1]
            self.panel.save_markdown(md_text)
        else:
            super().javaScriptAlert(securityOrigin, msg)

class MindMapEditorPanel(QWidget):
    def __init__(self, theme: dict):
        super().__init__()
        self.T = theme
        self.setStyleSheet(f"background:{theme['preview_bg']};")
        
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        lbl = QLabel("MIND MAP EDITOR")
        lbl.setObjectName("section_label")
        lay.addWidget(lbl)

        if HAS_WEBENGINE:
            self.web = QWebEngineView()
            self.page = MindMapEditorPage(self)
            self.web.setPage(self.page)
            self.web.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
            lay.addWidget(self.web, 1)
            self.load_editor()
        else:
            lbl = QLabel("QWebEngineView is required for the Mind Map.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lay.addWidget(lbl, 1)

    def save_markdown(self, md_text):
        parent = self.parent()
        while parent:
            if hasattr(parent, "tabs_data"):
                break
            parent = parent.parent()
            
        if not parent:
            return
            
        parent._add_tab(md_text, None)
        QMessageBox.information(self, "Mind Map Editor", "Saved as a new Markdown file!")

    def load_editor(self):
        dot_color = "#48484a" if self.T == "dark" else "#d1d1d6"
        bg_color = self.T["preview_bg"]
        text_color = self.T["editor_fg"]
        accent = self.T["accent"]
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
  body {{ 
    margin: 0; padding: 0; background-color: {bg_color}; overflow: hidden; 
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background-image: radial-gradient({dot_color} 1px, transparent 1px);
    background-size: 20px 20px;
    color: {text_color};
  }}
  svg {{ width: 100vw; height: 100vh; }}
  
  .node rect {{ 
      fill: {bg_color}; stroke-width: 2px; rx: 8; ry: 8; 
      cursor: grab; transition: box-shadow 0.2s; 
  }}
  .node:active rect {{ cursor: grabbing; }}
  .node:hover rect {{ box-shadow: 0 4px 12px rgba(0,0,0,0.1); stroke-width: 3px; }}
  .node text {{ fill: {text_color}; font-size: 14px; pointer-events: none; font-weight: 500; }}
  
  .link {{ fill: none; stroke-width: 2px; opacity: 0.8; }}
  
  .controls {{ opacity: 0; transition: opacity 0.2s; }}
  .node:hover .controls {{ opacity: 1; }}
  
  .add-btn circle {{ fill: {accent}; cursor: pointer; }}
  .add-btn path {{ stroke: #fff; stroke-width: 2px; pointer-events: none; fill: none; }}
  
  .del-btn circle {{ fill: #ff3b30; cursor: pointer; }}
  .del-btn path {{ stroke: #fff; stroke-width: 2px; pointer-events: none; fill: none; }}

  /* Toolbar */
  .toolbar {{
    position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%);
    background: {self.T['toolbar_bg']}; padding: 8px 16px; border-radius: 20px;
    display: flex; gap: 8px; align-items: center;
    border: 1px solid {self.T['border']}; box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  }}
  .btn {{
    background: transparent; color: {text_color}; border: none; padding: 8px;
    border-radius: 12px; cursor: pointer; display: flex; align-items: center; justify-content: center;
    transition: all 0.2s; width: 36px; height: 36px;
  }}
  .btn:hover {{ background: {self.T['btn_hover']}; }}
  .btn svg {{ width: 20px; height: 20px; fill: {text_color}; }}
  
  .btn.primary {{ background: {accent}; color: #fff; width: auto; padding: 8px 16px; font-weight: 600; font-size: 14px; }}
  .btn.primary svg {{ fill: #fff; margin-right: 6px; }}
  .btn.primary:hover {{ background: {accent}; opacity: 0.9; }}

  foreignObject {{ overflow: visible; }}
  input.editor {{
    width: 100%; height: 100%; background: {bg_color}; border: 2px solid {accent};
    color: {text_color}; font-size: 14px; text-align: center; border-radius: 8px;
    outline: none; box-sizing: border-box; font-family: inherit; font-weight: 500;
  }}
</style>
</head>
<body>
<div class="toolbar">
  <button class="btn" onclick="zoomIn()" title="Zoom In">
    <svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14zm2.5-4h-2v2H9v-2H7V9h2V7h1v2h2v1z"/></svg>
  </button>
  <button class="btn" onclick="zoomOut()" title="Zoom Out">
    <svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14zM7 9h5v1H7V9z"/></svg>
  </button>
  <button class="btn" onclick="resetZoom()" title="Reset Zoom">
    <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm5 11h-4v4h-2v-4H7v-2h4V7h2v4h4v2z"/></svg>
  </button>
  <div style="width: 1px; height: 24px; background: {self.T['border']}; margin: 0 4px;"></div>
  <button class="btn" onclick="exportImage()" title="Export Image">
    <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zm-5.04-6.71l-2.75 3.54-1.96-2.36L6.5 17h11l-3.54-4.71z"/></svg>
  </button>
  <button class="btn primary" onclick="exportData()">
    <svg viewBox="0 0 24 24"><path d="M19 12v7H5v-7H3v7c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-7h-2zm-6 .67l2.59-2.58L17 11.5l-5 5-5-5 1.41-1.41L11 12.67V3h2v9.67z"/></svg>
    Save Markdown
  </button>
</div>
<script>
  let rawData = {{
    name: "Central Idea", id: "root", children: []
  }};

  function treeToMarkdown(node, level = 1) {{
      let md = `${{'#'.repeat(Math.min(level, 6))}} ${{node.name}}\\n`;
      if (node.children) {{
          node.children.forEach(c => {{ md += treeToMarkdown(c, level + 1); }});
      }}
      return md;
  }}

  let root;
  const width = window.innerWidth;
  const height = window.innerHeight;
  
  // Richer color palette for nodes
  const color = d3.scaleOrdinal(["#0ea5e9", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#14b8a6", "#f97316"]);
  
  const zoom = d3.zoom().scaleExtent([0.1, 3]).on("zoom", (e) => {{
    svgGroup.attr("transform", e.transform);
  }});

  const svg = d3.select("body").append("svg").call(zoom).on("dblclick.zoom", null);
  const svgGroup = svg.append("g");
  
  svg.call(zoom.transform, d3.zoomIdentity.translate(width/4, height/2).scale(1.2));

  let treeLayout = d3.tree().nodeSize([50, 200]);
  let editingId = null;

  function update() {{
    root = d3.hierarchy(rawData);
    const treeData = treeLayout(root);
    const nodes = treeData.descendants();
    const links = treeData.links();

    nodes.forEach(d => {{
       d.w = Math.max(100, d.data.name.length * 8 + 30);
       d.h = 36;
    }});

    const node = svgGroup.selectAll('g.node')
      .data(nodes, d => d.data.id);

    const nodeEnter = node.enter().append('g')
      .attr('class', 'node')
      .attr('transform', d => `translate(${{d.y + (d.data.oy||0)}},${{d.x + (d.data.ox||0)}})`)
      .call(d3.drag()
          .on("start", function(event, d) {{
              event.sourceEvent.stopPropagation();
              d3.select(this).raise();
          }})
          .on("drag", function(event, d) {{
              d.data.ox = (d.data.ox || 0) + event.dy;
              d.data.oy = (d.data.oy || 0) + event.dx;
              d3.select(this).attr('transform', `translate(${{d.y + d.data.oy}},${{d.x + d.data.ox}})`);
              updateLinks();
          }})
      );

    nodeEnter.append('rect')
      .attr('y', d => -d.h/2)
      .attr('x', 0)
      .style('stroke', d => color(Math.max(1, d.depth)))
      .on('dblclick', (e, d) => {{
          e.stopPropagation();
          editingId = d.data.id;
          update();
      }});

    nodeEnter.append('text')
      .attr('dy', '0.35em')
      .attr('text-anchor', 'middle');

    const controls = nodeEnter.append('g').attr('class', 'controls');
      
    // Add child
    const addBtn = controls.append('g')
      .attr('class', 'add-btn')
      .on('click', (e, d) => {{
         e.stopPropagation();
         if (!d.data.children) d.data.children = [];
         d.data.children.push({{ name: "New Node", id: "n" + Date.now(), children: [], color: Math.floor(Math.random() * 8) }});
         update();
      }});
    addBtn.append('circle').attr('r', 10);
    addBtn.append('path').attr('d', 'M-5,0 L5,0 M0,-5 L0,5');

    // Add sibling
    const addSibBtn = controls.append('g')
      .attr('class', 'add-btn')
      .attr('transform', 'translate(0, 24)')
      .on('click', (e, d) => {{
         e.stopPropagation();
         if (d.parent) {{
             if (!d.parent.data.children) d.parent.data.children = [];
             d.parent.data.children.push({{ name: "New Node", id: "n" + Date.now(), children: [], color: Math.floor(Math.random() * 8) }});
             update();
         }}
      }});
    addSibBtn.append('circle').attr('r', 10).style('fill', '#10b981');
    addSibBtn.append('path').attr('d', 'M-5,0 L5,0 M0,-5 L0,5');

    // Delete
    const delBtn = controls.append('g')
      .attr('class', 'del-btn')
      .on('click', (e, d) => {{
         e.stopPropagation();
         if (d.parent) {{
             d.parent.data.children = d.parent.data.children.filter(c => c.id !== d.data.id);
             update();
         }}
      }});
    delBtn.append('circle').attr('r', 10);
    delBtn.append('path').attr('d', 'M-5,0 L5,0');

    const nodeUpdate = nodeEnter.merge(node);
    
    nodeUpdate.transition().duration(250)
      .attr('transform', d => `translate(${{d.y + (d.data.oy||0)}},${{d.x + (d.data.ox||0)}})`);

    nodeUpdate.selectAll('rect')
      .attr('width', d => d.w)
      .attr('height', d => d.h)
      .style('stroke', d => d.data.color !== undefined ? color(d.data.color) : color(Math.max(1, d.depth)))
      .style('display', d => d.data.id === editingId ? 'none' : 'block');
      
    nodeUpdate.selectAll('text')
      .attr('x', d => d.w/2)
      .text(d => d.data.name)
      .style('display', d => d.data.id === editingId ? 'none' : 'block');
      
    nodeUpdate.selectAll('.add-btn').attr('transform', d => `translate(${{d.w + 12}}, 0)`);
    nodeUpdate.selectAll('.del-btn').attr('transform', `translate(-12, 0)`);
    
    nodeUpdate.selectAll('foreignObject').remove();
    
    nodeUpdate.filter(d => d.data.id === editingId).append('foreignObject')
      .attr('width', d => d.w + 20)
      .attr('height', d => d.h)
      .attr('x', -10)
      .attr('y', d => -d.h/2)
      .append('xhtml:input')
      .attr('class', 'editor')
      .attr('value', d => d.data.name)
      .on('blur', function(e, d) {{
          d.data.name = this.value || "Empty";
          editingId = null;
          update();
      }})
      .on('keydown', function(e, d) {{
          if (e.key === 'Enter') this.blur();
      }});
      
    setTimeout(() => {{
        const inputs = document.querySelectorAll('input.editor');
        if (inputs.length > 0) {{ inputs[0].focus(); inputs[0].select(); }}
    }}, 50);

    node.exit().transition().duration(250)
      .attr('transform', d => `translate(${{d.parent ? d.parent.y : d.y}},${{d.parent ? d.parent.x : d.x}})`)
      .style('opacity', 0)
      .remove();

    const link = svgGroup.selectAll('path.link')
      .data(links, d => d.target.data.id);

    const linkEnter = link.enter().insert('path', 'g')
      .attr('class', 'link')
      .style('stroke', d => color(Math.max(1, d.target.depth)))
      .attr('d', d => {{
        const o = {{x: d.source.x + (d.source.data.ox||0), y: d.source.y + (d.source.data.oy||0) + d.source.w}};
        return diagonal(o, o);
      }});

    linkEnter.merge(link).transition().duration(250)
      .attr('d', d => {{
          const s = {{x: d.source.x + (d.source.data.ox||0), y: d.source.y + (d.source.data.oy||0) + d.source.w}};
          const t = {{x: d.target.x + (d.target.data.ox||0), y: d.target.y + (d.target.data.oy||0)}};
          return diagonal(s, t);
      }})
      .style('stroke', d => color(Math.max(1, d.target.depth)));

    link.exit().transition().duration(250)
      .attr('d', d => {{
        const o = {{x: d.source.x + (d.source.data.ox||0), y: d.source.y + (d.source.data.oy||0) + d.source.w}};
        return diagonal(o, o);
      }}).remove();
      
    svgGroup.selectAll('.del-btn').style('display', d => d.parent ? 'block' : 'none');
    
    window.updateLinks = function() {{
        svgGroup.selectAll('path.link').attr('d', d => {{
          const s = {{x: d.source.x + (d.source.data.ox||0), y: d.source.y + (d.source.data.oy||0) + d.source.w}};
          const t = {{x: d.target.x + (d.target.data.ox||0), y: d.target.y + (d.target.data.oy||0)}};
          return diagonal(s, t);
        }});
    }};
  }}

  function diagonal(s, d) {{
    // Smooth bezier curve
    return `M ${{s.y}} ${{s.x}}
            C ${{(s.y + d.y) / 2}} ${{s.x}},
              ${{(s.y + d.y) / 2}} ${{d.x}},
              ${{d.y}} ${{d.x}}`;
  }}

  update();

  function zoomIn() {{ svg.transition().call(zoom.scaleBy, 1.3); }}
  function zoomOut() {{ svg.transition().call(zoom.scaleBy, 0.7); }}
  function resetZoom() {{ svg.transition().call(zoom.transform, d3.zoomIdentity.translate(width/4, height/2).scale(1.2)); }}
  
  function exportData() {{
      const md = treeToMarkdown(rawData);
      alert("SAVE_MARKDOWN:" + md);
  }}
  
  function exportImage() {{
      const svgElement = document.querySelector('svg');
      const clonedSvg = svgElement.cloneNode(true);
      
      const g = clonedSvg.querySelector('g');
      g.setAttribute('transform', 'translate(50, ' + height/2 + ')');
      
      const xml = new XMLSerializer().serializeToString(clonedSvg);
      const svg64 = btoa(unescape(encodeURIComponent(xml)));
      const b64Start = 'data:image/svg+xml;base64,';
      const image64 = b64Start + svg64;
      
      const img = new Image();
      img.onload = function() {{
          const canvas = document.createElement('canvas');
          canvas.width = svgElement.clientWidth;
          canvas.height = svgElement.clientHeight;
          const ctx = canvas.getContext('2d');
          
          ctx.fillStyle = '{bg_color}';
          ctx.fillRect(0, 0, canvas.width, canvas.height);
          
          ctx.drawImage(img, 0, 0);
          
          const a = document.createElement('a');
          a.download = 'mind_map.png';
          a.href = canvas.toDataURL('image/png');
          a.click();
      }};
      img.src = image64;
  }}
</script>
</body>
</html>
        """
        self.web.setHtml(html)
