import csv, json
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/long_duration_packets/openstack_long_horizon_001")
SRC = BASE / "measured" / "traversal_windows_v0.csv"
OUT = BASE / "visualizations" / "openstack_global_focus_lens_v47a.html"

# ============================================================
# SECTION 1 — DATA LOAD
# ============================================================

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))
for r in rows:
    for k in ["window_size","line_start","line_end","stable_share","middle_share","residual_share"]:
        r[k] = float(r[k])

sizes = sorted(set(int(r["window_size"]) for r in rows))
max_line = max(int(r["line_end"]) for r in rows)

source_path = BASE / "raw" / "openstack_normal2.log"
source_lines = source_path.read_text(encoding="utf-8", errors="replace").splitlines()

payload = {"rows": rows, "sizes": sizes, "max_line": max_line, "source_lines": source_lines}
payload_json = json.dumps(payload)

html = f"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>OpenStack Global Focus Lens V47A</title>
<style>
body {{ font-family: Georgia, serif; margin: 26px; background: white; }}
h1 {{ text-align: center; font-weight: normal; }}
#wrap {{ width: 96%; margin: 0 auto; }}
.controls {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin: 18px 0; }}
.box {{ border: 1px solid #aaa; padding: 12px; }}
input[type=range] {{ width: 100%; }}
.label {{ text-align: center; font-size: 18px; margin: 10px; }}
.bar {{ position: relative; height: 78px; border: 1px solid black; margin-top: 14px; display: flex; overflow: hidden; user-select: none; }}
.focusBar {{ height: 145px; cursor: crosshair; }}
.seg {{ height: 100%; }}
.stable {{ background: white; }}
.middle {{ background: #bfbfbf; }}
.residual {{ background: #222222; }}
.lens {{ position: absolute; top: 0; height: 100%; border-left: 3px solid red; border-right: 3px solid red; background: rgba(255,0,0,0.10); pointer-events: none; }}
.dragBox {{ position: absolute; top: 0; height: 100%; background: rgba(255,0,0,0.18); border-left: 2px dashed red; border-right: 2px dashed red; pointer-events: none; }}
.legend {{ text-align: center; margin-top: 18px; font-size: 15px; }}
.note {{ margin-top: 22px; font-size: 16px; line-height: 1.4; }}
#linePreview {{ border:1px solid #999; padding:12px; height:240px; overflow:auto; white-space:pre-wrap; font-family:Consolas, monospace; font-size:13px; }}
</style>
</head>
<body>
<div id="wrap">
<h1>OpenStack Global Focus Lens V47A</h1>

<div class="box">
  <div>Global window</div>
  <input id="globalSizeDial" type="range" min="0" max="{len(sizes)-1}" value="{max(0, sizes.index(350) if 350 in sizes else 0)}" step="1">
  <div id="globalSizeLabel" class="label"></div>
</div>

<div class="label" id="globalLabel"></div>
<div id="globalBar" class="bar"></div>

<div class="controls">
  <div class="box">
    <div>Focus width</div>
    <input id="spanDial" type="range" min="500" max="30000" value="3400" step="100">
    <div id="spanLabel" class="label"></div>
  </div>

  <div class="box" style="grid-column: span 2;">
    <div>Focus center</div>
    <input id="centerDial" type="range" min="1" max="{max_line}" value="31300" step="50">
    <div id="centerLabel" class="label"></div>
  </div>
</div>

<div class="box">
  <div>Focus window</div>
  <input id="focusSizeDial" type="range" min="0" max="{len(sizes)-1}" value="{max(0, sizes.index(100) if 100 in sizes else 0)}" step="1">
  <div id="focusSizeLabel" class="label"></div>
</div>

<div class="label" id="focusLabel"></div>
<div id="focusBar" class="bar focusBar"></div>

<div class="legend">white = stable | grey = middle | black = residual | red lens = selected focus region</div>

<div class="label" id="linePreviewLabel">Selected raw lines</div>
<pre id="linePreview">Click or drag inside the focus lens to preview precise raw source lines.</pre>

<div class="box">
  <div>Investigatory sticky note</div>
  <input id="noteText" type="text" placeholder="Why is this region interesting?" style="width:100%; font-size:16px; padding:6px;">
  <input id="unresolvedText" type="text" placeholder="What remains unresolved?" style="width:100%; font-size:16px; padding:6px; margin-top:8px;">
  <button id="saveBookmark" style="margin-top:10px; font-size:16px;">Save sticky note</button>
  <pre id="bookmarkPreview" style="border:1px solid #999; padding:10px; white-space:pre-wrap; font-family:Consolas, monospace; font-size:13px;"></pre>
</div>

<div class="note">
Use the upper bar as the map. Click or drag on it to choose a region. Mouse wheel over the global map changes the focus window size. Click or drag inside the focus lens to preview raw lines.
</div>
</div>

<script>
/* SECTION 1 — DOM REFERENCES */
const data = __PAYLOAD__;

const globalSizeDial = document.getElementById("globalSizeDial");
const focusSizeDial = document.getElementById("focusSizeDial");
const spanDial = document.getElementById("spanDial");
const centerDial = document.getElementById("centerDial");
const globalBar = document.getElementById("globalBar");
const focusBar = document.getElementById("focusBar");
const globalSizeLabel = document.getElementById("globalSizeLabel");
const focusSizeLabel = document.getElementById("focusSizeLabel");
const spanLabel = document.getElementById("spanLabel");
const centerLabel = document.getElementById("centerLabel");
const globalLabel = document.getElementById("globalLabel");
const focusLabel = document.getElementById("focusLabel");
const linePreview = document.getElementById("linePreview");
const linePreviewLabel = document.getElementById("linePreviewLabel");
const noteText = document.getElementById("noteText");
const unresolvedText = document.getElementById("unresolvedText");
const saveBookmark = document.getElementById("saveBookmark");
const bookmarkPreview = document.getElementById("bookmarkPreview");

/* SECTION 2 — STATE */
let dragging = false;
let dragStartLine = null;
let dragBox = null;

let focusDragging = false;
let focusDragStartLine = null;
let focusDragBox = null;

function clamp(v, lo, hi) {{ return Math.max(lo, Math.min(hi, v)); }}

function state() {{
  const globalSize = data.sizes[parseInt(globalSizeDial.value)];
  const focusSize = data.sizes[parseInt(focusSizeDial.value)];
  const span = parseInt(spanDial.value);
  let center = parseInt(centerDial.value);

  let start = Math.round(center - span / 2);
  let end = Math.round(center + span / 2);

  if (start < 1) {{ start = 1; end = span; }}
  if (end > data.max_line) {{ end = data.max_line; start = data.max_line - span + 1; }}

  start = clamp(start, 1, data.max_line);
  end = clamp(end, 1, data.max_line);

  center = Math.round((start + end) / 2);
  centerDial.value = center;

  return {{globalSize, focusSize, span, center, start, end}};
}}

function lineFromMouse(evt, bar, start, end) {{
  const rect = bar.getBoundingClientRect();
  const x = clamp(evt.clientX - rect.left, 0, rect.width);
  return Math.round(start + (x / rect.width) * (end - start));
}}

function clearBar(bar) {{ bar.innerHTML = ""; }}

function addSeg(bar, cls, widthPct) {{
  const div = document.createElement("div");
  div.className = "seg " + cls;
  div.style.width = widthPct + "%";
  bar.appendChild(div);
}}

/* SECTION 4 — BAR RENDERING */
function renderBar(bar, size, start, end, fullScale) {{
  clearBar(bar);

  const rows = data.rows.filter(r =>
    parseInt(r.window_size) === size &&
    r.line_end >= start &&
    r.line_start <= end
  );

  const span = end - start + 1;

  rows.forEach(r => {{
    const localStart = Math.max(r.line_start, start);
    const localEnd = Math.min(r.line_end, end);
    const total = localEnd - localStart + 1;

    [["stable", r.stable_share], ["middle", r.middle_share], ["residual", r.residual_share]].forEach(pair => {{
      const denom = fullScale ? data.max_line : span;
      addSeg(bar, pair[0], pair[1] * total / denom * 100);
    }});
  }});
}}

/* SECTION 5 — GLOBAL LENS */
function addLens(start, end) {{
  const lens = document.createElement("div");
  lens.className = "lens";
  lens.style.left = ((start - 1) / data.max_line * 100) + "%";
  lens.style.width = ((end - start + 1) / data.max_line * 100) + "%";
  globalBar.appendChild(lens);
}}

/* SECTION 6 — RAW EVIDENCE PREVIEW */
function previewLineRange(startLine, endLine) {{
  const start = Math.max(1, Math.min(startLine, endLine));
  const end = Math.min(data.max_line, Math.max(startLine, endLine));
  const cappedEnd = Math.min(end, start + 250);

  let out = [];
  for (let i = start; i <= cappedEnd; i++) {{
    const line = data.source_lines[i - 1] || "";
    out.push(String(i).padStart(8, " ") + " | " + line);
  }}

  let suffix = "";
  if (cappedEnd < end) {{
    suffix = "\\n\\n... preview capped at 250 lines. Selected range continues to " + end + ".";
  }}

  linePreviewLabel.innerHTML = "Selected raw lines: " + start + "-" + end;
  linePreview.textContent = out.join("\\n") + suffix;
}}

function previewLines(centerLine) {{
  const radius = 8;
  previewLineRange(centerLine - radius, centerLine + radius);
}}

/* SECTION 7 — MAIN RENDER */
function render() {{
  const s = state();

  globalSizeLabel.innerHTML = s.globalSize;
  focusSizeLabel.innerHTML = s.focusSize;
  spanLabel.innerHTML = "focus width: " + s.span + " lines";
  centerLabel.innerHTML = "focus center: " + s.center;

  renderBar(globalBar, s.globalSize, 1, data.max_line, true);
  addLens(s.start, s.end);
  renderBar(focusBar, s.focusSize, s.start, s.end, false);

  globalLabel.innerHTML = "Global map: lines 1-" + data.max_line;
  focusLabel.innerHTML = "Focus lens: lines " + s.start + "-" + s.end + " | span " + (s.end - s.start + 1);
}}

/* SECTION 8 — GLOBAL INTERACTION */
globalBar.addEventListener("mousedown", evt => {{
  dragging = true;
  dragStartLine = lineFromMouse(evt, globalBar, 1, data.max_line);

  if (dragBox) {{ dragBox.remove(); }}

  dragBox = document.createElement("div");
  dragBox.className = "dragBox";
  globalBar.appendChild(dragBox);
}});

globalBar.addEventListener("mousemove", evt => {{
  if (!dragging || !dragBox) return;

  const currentLine = lineFromMouse(evt, globalBar, 1, data.max_line);
  const a = Math.min(dragStartLine, currentLine);
  const b = Math.max(dragStartLine, currentLine);

  dragBox.style.left = ((a - 1) / data.max_line * 100) + "%";
  dragBox.style.width = ((b - a + 1) / data.max_line * 100) + "%";
}});

globalBar.addEventListener("mouseup", evt => {{
  if (!dragging) return;

  dragging = false;

  const endLine = lineFromMouse(evt, globalBar, 1, data.max_line);
  const a = Math.min(dragStartLine, endLine);
  const b = Math.max(dragStartLine, endLine);

  const span = Math.max(500, b - a + 1);
  const center = Math.round((a + b) / 2);

  spanDial.value = clamp(span, parseInt(spanDial.min), parseInt(spanDial.max));
  centerDial.value = clamp(center, 1, data.max_line);

  if (dragBox) {{ dragBox.remove(); dragBox = null; }}
  render();
}});

globalBar.addEventListener("wheel", evt => {{
  evt.preventDefault();

  let idx = parseInt(globalSizeDial.value);
  idx = evt.deltaY > 0 ? idx + 1 : idx - 1;

  globalSizeDial.value = clamp(idx, parseInt(globalSizeDial.min), parseInt(globalSizeDial.max));
  render();
}});

focusBar.addEventListener("wheel", evt => {{
  evt.preventDefault();

  let idx = parseInt(focusSizeDial.value);
  idx = evt.deltaY > 0 ? idx + 1 : idx - 1;

  focusSizeDial.value = clamp(idx, parseInt(focusSizeDial.min), parseInt(focusSizeDial.max));
  render();
}});

/* SECTION 9 — FOCUS INTERACTION */
focusBar.addEventListener("mousedown", evt => {{
  focusDragging = true;

  const s = state();
  focusDragStartLine = lineFromMouse(evt, focusBar, s.start, s.end);

  if (focusDragBox) {{ focusDragBox.remove(); }}

  focusDragBox = document.createElement("div");
  focusDragBox.className = "dragBox";
  focusBar.appendChild(focusDragBox);
}});

focusBar.addEventListener("mousemove", evt => {{
  if (!focusDragging || !focusDragBox) return;

  const s = state();
  const currentLine = lineFromMouse(evt, focusBar, s.start, s.end);
  const a = Math.min(focusDragStartLine, currentLine);
  const b = Math.max(focusDragStartLine, currentLine);

  focusDragBox.style.left = ((a - s.start) / (s.end - s.start + 1) * 100) + "%";
  focusDragBox.style.width = ((b - a + 1) / (s.end - s.start + 1) * 100) + "%";
}});

focusBar.addEventListener("mouseup", evt => {{
  if (!focusDragging) return;

  focusDragging = false;

  const s = state();
  const endLine = lineFromMouse(evt, focusBar, s.start, s.end);
  const a = Math.min(focusDragStartLine, endLine);
  const b = Math.max(focusDragStartLine, endLine);

  if (Math.abs(b - a) < 3) {{
    previewLines(a);
  }} else {{
    previewLineRange(a, b);
  }}

  if (focusDragBox) {{
    focusDragBox.remove();
    focusDragBox = null;
  }}
}});

focusBar.addEventListener("mouseleave", evt => {{
  if (focusDragging) {{
    focusDragging = false;
    if (focusDragBox) {{
      focusDragBox.remove();
      focusDragBox = null;
    }}
  }}
}});

[globalSizeDial, focusSizeDial, spanDial, centerDial].forEach(el => {{
  el.addEventListener("input", render);
}});

/* SECTION 10 — STICKY NOTE */
saveBookmark.addEventListener("click", evt => {{
  const s = state();

  const bookmark = {{
    bookmark_id: "local_" + Date.now(),
    terrain: "OpenStack_long_normal2",
    global_window: s.globalSize,
    focus_window: s.focusSize,
    focus_start: s.start,
    focus_end: s.end,
    focus_width: s.span,
    operator_note: noteText.value,
    unresolved_status: unresolvedText.value,
    next_lawful_revisit: "return under alternate constitution",
    created_local: new Date().toISOString()
  }};

  bookmarkPreview.textContent = JSON.stringify(bookmark, null, 2);
}});

render();
</script>
</body>
</html>
"""

html = html.replace("__PAYLOAD__", payload_json)

OUT.write_text(html, encoding="utf-8")
print("WROTE", OUT.resolve())




