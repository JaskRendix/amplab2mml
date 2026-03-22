from datetime import UTC, datetime
from string import Template

_HTML_TEMPLATE = Template(
    """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>$title</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:        #0f1117;
    --surface:   #181c27;
    --border:    #2a2f3d;
    --accent:    #4ade80;
    --accent2:   #38bdf8;
    --warn:      #fbbf24;
    --muted:     #6b7280;
    --text:      #e2e8f0;
    --text-dim:  #94a3b8;
    --radius:    6px;
    --mono:      'IBM Plex Mono', monospace;
    --sans:      'IBM Plex Sans', sans-serif;
  }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--sans);
    font-size: 14px;
    line-height: 1.6;
    padding: 2rem;
  }

  header {
    border-bottom: 1px solid var(--border);
    padding-bottom: 1.5rem;
    margin-bottom: 2rem;
  }

  header h1 {
    font-size: 1.4rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    color: var(--accent);
    font-family: var(--mono);
  }

  header p {
    color: var(--text-dim);
    font-size: 0.85rem;
    margin-top: 0.3rem;
  }

  .grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    margin-bottom: 2rem;
  }

  @media (max-width: 900px) { .grid { grid-template-columns: 1fr; } }

  .stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.25rem;
  }

  .stat-card .label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    font-family: var(--mono);
  }

  .stat-card .value {
    font-size: 1.8rem;
    font-weight: 600;
    font-family: var(--mono);
    color: var(--accent2);
    margin-top: 0.2rem;
  }

  section { margin-bottom: 2.5rem; }

  section h2 {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    font-family: var(--mono);
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
  }

  /* warnings */
  .warnings { list-style: none; }
  .warnings li {
    background: #2a1f0a;
    border-left: 3px solid var(--warn);
    padding: 0.5rem 0.75rem;
    border-radius: 0 var(--radius) var(--radius) 0;
    margin-bottom: 0.4rem;
    font-family: var(--mono);
    font-size: 0.82rem;
    color: var(--warn);
  }

  /* tree */
  .tree { list-style: none; }
  .tree li { margin: 0; }

  .tree-node {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    margin-bottom: 0.4rem;
    overflow: hidden;
  }

  .tree-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.5rem 0.75rem;
    cursor: pointer;
    user-select: none;
    transition: background 0.15s;
  }

  .tree-header:hover { background: #1e2330; }

  .toggle {
    font-family: var(--mono);
    font-size: 0.7rem;
    color: var(--muted);
    width: 14px;
    display: inline-block;
    flex-shrink: 0;
  }

  .eq-name {
    font-family: var(--mono);
    font-weight: 600;
    font-size: 0.88rem;
    color: var(--text);
    flex: 1;
  }

  .badge {
    font-size: 0.68rem;
    font-family: var(--mono);
    padding: 0.1rem 0.45rem;
    border-radius: 99px;
    background: #1a2535;
    color: var(--accent2);
    border: 1px solid #2a3a50;
  }

  .badge-class {
    background: #1a2a1a;
    color: var(--accent);
    border-color: #2a402a;
  }

  .tree-body {
    display: none;
    padding: 0.5rem 0.75rem 0.75rem 2rem;
    border-top: 1px solid var(--border);
  }

  .tree-body.open { display: block; }

  .props-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 0.75rem;
    font-size: 0.82rem;
  }

  .props-table td {
    padding: 0.2rem 0.5rem;
    border-bottom: 1px solid var(--border);
    vertical-align: top;
  }

  .props-table td:first-child {
    font-family: var(--mono);
    color: var(--text-dim);
    white-space: nowrap;
    width: 40%;
  }

  .props-table td:last-child { color: var(--text); }

  .children-list {
    list-style: none;
    margin-top: 0.5rem;
  }

  /* classes table */
  .cls-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
  }

  .cls-table th {
    text-align: left;
    font-family: var(--mono);
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--muted);
    padding: 0.4rem 0.75rem;
    border-bottom: 1px solid var(--border);
  }

  .cls-table td {
    padding: 0.4rem 0.75rem;
    border-bottom: 1px solid var(--border);
    vertical-align: top;
  }

  .cls-table tr:last-child td { border-bottom: none; }

  .cls-table td:first-child {
    font-family: var(--mono);
    color: var(--accent);
    white-space: nowrap;
  }

  .cls-table td:nth-child(2) {
    font-family: var(--mono);
    color: var(--text-dim);
    font-size: 0.78rem;
  }

  .cls-row { background: var(--surface); }
  .cls-row:hover { background: #1e2330; }

  .prop-pill {
    display: inline-block;
    font-family: var(--mono);
    font-size: 0.72rem;
    padding: 0.1rem 0.4rem;
    margin: 0.1rem;
    border-radius: 3px;
    background: #1a2535;
    border: 1px solid var(--border);
    color: var(--text-dim);
  }
  .prop-pill span { color: var(--accent2); }
</style>
</head>
<body>

<header>
  <h1>&#x25A0; Ampla Equipment Report</h1>
  <p>Generated $generated_at &nbsp;·&nbsp; $total_equipment equipment nodes &nbsp;·&nbsp; $total_classes classes &nbsp;·&nbsp; max depth $max_depth</p>
</header>

$warnings_section

<section>
  <h2>Equipment Hierarchy</h2>
  <ul class="tree">
    $equipment_tree
  </ul>
</section>

<section>
  <h2>Equipment Classes</h2>
  <table class="cls-table">
    <thead>
      <tr><th>Name</th><th>Parent</th><th>Properties</th></tr>
    </thead>
    <tbody>
      $classes_rows
    </tbody>
  </table>
</section>

<script>
  document.querySelectorAll('.tree-header').forEach(h => {
    h.addEventListener('click', () => {
      const body = h.nextElementSibling;
      const toggle = h.querySelector('.toggle');
      if (!body) return;
      const open = body.classList.toggle('open');
      toggle.textContent = open ? '▾' : '▸';
    });
  });
</script>
</body>
</html>
"""
)


def _render_equipment_node(eq) -> str:
    has_children = bool(eq.children)
    has_props = bool(eq.properties)
    has_classes = bool(eq.class_ids)
    has_body = has_children or has_props or has_classes

    toggle = "▸" if has_body else " "

    badges = f'<span class="badge">{_esc(eq.level)}</span>'
    for cid in eq.class_ids:
        badges += f' <span class="badge badge-class">{_esc(cid)}</span>'

    props_html = ""
    if has_props:
        rows = "".join(
            f"<tr><td>{_esc(p.name)}</td><td>{_esc(p.value or '')}</td></tr>"
            for p in eq.properties
        )
        props_html = f'<table class="props-table"><tbody>{rows}</tbody></table>'

    children_html = ""
    if has_children:
        inner = "".join(_render_equipment_node(c) for c in eq.children)
        children_html = f'<ul class="children-list">{inner}</ul>'

    body_html = ""
    if has_body:
        body_html = f'<div class="tree-body">{props_html}{children_html}</div>'

    return (
        f'<li class="tree-node">'
        f'<div class="tree-header">'
        f'<span class="toggle">{toggle}</span>'
        f'<span class="eq-name">{_esc(eq.name or eq.full_name or eq.id)}</span>'
        f"{badges}"
        f"</div>"
        f"{body_html}"
        f"</li>"
    )


def _render_classes(classes) -> str:
    rows = []
    for cls in classes:
        pills = "".join(
            f'<span class="prop-pill">{_esc(p.name)}: <span>{_esc(p.value or "")}</span></span>'
            for p in cls.properties
        )
        rows.append(
            f'<tr class="cls-row">'
            f"<td>{_esc(cls.name)}</td>"
            f'<td>{_esc(cls.parent or "")}</td>'
            f"<td>{pills}</td>"
            f"</tr>"
        )
    return "".join(rows)


def _render_warnings(warnings: list) -> str:
    if not warnings:
        return ""
    items = "".join(f"<li>{_esc(w)}</li>" for w in warnings)
    return f'<section><h2>Warnings</h2><ul class="warnings">{items}</ul></section>'


def _esc(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _count_equipment(equipment_list) -> int:
    total = 0
    for eq in equipment_list:
        total += 1
        total += _count_equipment(eq.children)
    return total


def _max_depth(equipment_list, depth=1) -> int:
    if not equipment_list:
        return 0
    return max(
        max((depth, _max_depth(eq.children, depth + 1))) for eq in equipment_list
    )


def export_to_html(model: dict) -> str:
    equipment = model["equipment"]
    classes = model["classes"]
    warnings = model.get("warnings", [])

    total_equipment = _count_equipment(equipment)
    total_classes = len(classes)
    depth = _max_depth(equipment)
    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

    tree_html = "".join(_render_equipment_node(eq) for eq in equipment)
    classes_html = _render_classes(classes)
    warnings_html = _render_warnings(warnings)

    return _HTML_TEMPLATE.substitute(
        title="Ampla Equipment Report",
        generated_at=generated_at,
        total_equipment=total_equipment,
        total_classes=total_classes,
        max_depth=depth,
        warnings_section=warnings_html,
        equipment_tree=tree_html,
        classes_rows=classes_html,
    )
