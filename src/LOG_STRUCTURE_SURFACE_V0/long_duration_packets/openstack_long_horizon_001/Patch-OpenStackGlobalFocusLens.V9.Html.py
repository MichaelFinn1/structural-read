from pathlib import Path
import re

base = Path("src/LOG_STRUCTURE_SURFACE_V0/long_duration_packets/openstack_long_horizon_001/visualizations")
src = base / "openstack_global_focus_lens_v8.html"
out = base / "openstack_global_focus_lens_v9.html"

text = src.read_text(encoding="utf-8")
text = text.replace("OpenStack Global Focus Lens V8", "OpenStack Global Focus Lens V9")

text = text.replace("</style>", """
.seg { outline: none !important; border: 0 !important; }
.linePreview { border:1px solid #999; padding:12px; height:260px; overflow:auto; font-family:Consolas, monospace; font-size:13px; }
.lineRow { display:grid; grid-template-columns: 28px 82px 108px 1fr; gap:8px; padding:2px 0; border-bottom:1px solid #eee; }
.lineRow.off { opacity:0.35; text-decoration: line-through; }
.lineStable { background:#ffffff; }
.lineMiddle { background:#d0d0d0; }
.lineResidual { background:#222; color:white; }
.packageControls { margin: 8px 0; display:flex; gap:8px; flex-wrap:wrap; }
.packageControls button { font-size:13px; }
#packageSummary { font-family:Consolas, monospace; font-size:13px; margin:6px 0; }
</style>""")

text = text.replace(
    '<pre id="linePreview">Click or drag inside the focus lens to preview precise raw source lines.</pre>',
    '''<div id="linePreview" class="linePreview">Click or drag inside the focus lens to preview precise raw source lines.</div>
<div class="packageControls">
  <button id="selectAllLines">select all shown</button>
  <button id="clearAllLines">clear all shown</button>
  <button id="selectStableLines">select white/stable</button>
  <button id="selectMiddleLines">select grey/middle</button>
  <button id="selectResidualLines">select black/residual</button>
</div>
<div id="packageSummary">Selected package: none</div>'''
)

text = text.replace(
    'const linePreviewLabel = document.getElementById("linePreviewLabel");',
    '''const linePreviewLabel = document.getElementById("linePreviewLabel");
const selectAllLines = document.getElementById("selectAllLines");
const clearAllLines = document.getElementById("clearAllLines");
const selectStableLines = document.getElementById("selectStableLines");
const selectMiddleLines = document.getElementById("selectMiddleLines");
const selectResidualLines = document.getElementById("selectResidualLines");
const packageSummary = document.getElementById("packageSummary");'''
)

text = text.replace(
    "let selectedStart = null;\nlet selectedEnd = null;",
    "let selectedStart = null;\nlet selectedEnd = null;\nlet previewRows = [];\nlet includedLines = new Set();"
)

text = re.sub(
    r'function dominantPostureForLine\(line, size\) \{[\s\S]*?\n\}',
    r'''function dominantPostureForLine(line, size) {
  const rows = data.rows.filter(r =>
    parseInt(r.window_size) === size &&
    r.line_start <= line &&
    r.line_end >= line
  );

  if (rows.length === 0) return "unmapped";

  const r = rows[0];
  const total = r.line_end - r.line_start + 1;
  const pos = (line - r.line_start + 0.5) / total;

  if (pos <= r.stable_share) return "white/stable";
  if (pos <= r.stable_share + r.middle_share) return "grey/middle";
  return "black/residual";
}''',
    text,
    count=1
)

text = re.sub(
    r'function previewLineRange\(startLine, endLine\) \{[\s\S]*?\n\}',
    r'''function previewLineRange(startLine, endLine, restoreIncluded=null) {
  const s = state();
  const start = Math.max(1, Math.min(startLine, endLine));
  const end = Math.min(data.max_line, Math.max(startLine, endLine));
  const cappedEnd = Math.min(end, start + 250);

  selectedStart = start;
  selectedEnd = end;
  previewRows = [];

  if (restoreIncluded) {
    includedLines = new Set(restoreIncluded.map(x => parseInt(x)));
  } else {
    includedLines = new Set();
    for (let i = start; i <= cappedEnd; i++) includedLines.add(i);
  }

  for (let i = start; i <= cappedEnd; i++) {
    previewRows.push({
      line_no: i,
      posture: dominantPostureForLine(i, s.focusSize),
      text: data.source_lines[i - 1] || ""
    });
  }

  linePreviewLabel.innerHTML = "Selected raw lines: " + start + "-" + end + " | focus window " + s.focusSize;
  render();
  renderLinePreview();

  if (cappedEnd < end) {
    packageSummary.innerHTML = "Selected package: " + includedLines.size + " included lines. Preview capped at 250; selected range continues to " + end + ".";
  }
}''',
    text,
    count=1
)

insert_before = "function renderCards() {"
helpers = r'''
function postureClass(posture) {
  if (posture === "white/stable") return "lineStable";
  if (posture === "grey/middle") return "lineMiddle";
  if (posture === "black/residual") return "lineResidual";
  return "";
}

function renderLinePreview() {
  linePreview.innerHTML = "";

  previewRows.forEach(r => {
    const row = document.createElement("div");
    row.className = "lineRow " + postureClass(r.posture);
    if (!includedLines.has(r.line_no)) row.className += " off";

    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.checked = includedLines.has(r.line_no);
    cb.addEventListener("change", evt => {
      if (cb.checked) includedLines.add(r.line_no);
      else includedLines.delete(r.line_no);
      renderLinePreview();
    });

    const ln = document.createElement("div");
    ln.textContent = String(r.line_no).padStart(8, " ");

    const po = document.createElement("div");
    po.textContent = r.posture;

    const tx = document.createElement("div");
    tx.textContent = r.text;

    row.appendChild(cb);
    row.appendChild(ln);
    row.appendChild(po);
    row.appendChild(tx);
    linePreview.appendChild(row);
  });

  packageSummary.innerHTML = "Selected package: " + includedLines.size + " of " + previewRows.length + " shown lines included";
}

function selectPreviewWhere(mode) {
  if (mode === "all") {
    previewRows.forEach(r => includedLines.add(r.line_no));
  } else if (mode === "none") {
    includedLines.clear();
  } else {
    previewRows.forEach(r => {
      if (r.posture === mode) includedLines.add(r.line_no);
      else includedLines.delete(r.line_no);
    });
  }
  renderLinePreview();
}

'''
text = text.replace(insert_before, helpers + insert_before, 1)

text = text.replace(
    'previewLineRange(selectedStart, selectedEnd);',
    'previewLineRange(selectedStart, selectedEnd, b.included_lines || null);'
)

text = re.sub(
    r'raw_end: selectedEnd === null \? s\.end : selectedEnd,',
    r'''raw_end: selectedEnd === null ? s.end : selectedEnd,
    included_lines: Array.from(includedLines).sort((a, b) => a - b),
    included_count: includedLines.size,''',
    text,
    count=1
)

text = text.replace(
    'meta.textContent = "g" + b.global_window + " f" + b.focus_window + " raw " + b.raw_start + "-" + b.raw_end;',
    'meta.textContent = "g" + b.global_window + " f" + b.focus_window + " raw " + b.raw_start + "-" + b.raw_end + " included " + (b.included_count || 0);'
)

text = text.replace(
    '''  linePreviewLabel.innerHTML = "Selected raw lines";
  linePreview.textContent = "Click or drag inside the focus lens to preview precise raw source lines.";
  render();''',
    '''  linePreviewLabel.innerHTML = "Selected raw lines";
  linePreview.innerHTML = "Click or drag inside the focus lens to preview precise raw source lines.";
  packageSummary.innerHTML = "Selected package: none";
  previewRows = [];
  includedLines = new Set();
  render();'''
)

text = text.replace(
    'render();\n</script>',
    '''selectAllLines.addEventListener("click", evt => selectPreviewWhere("all"));
clearAllLines.addEventListener("click", evt => selectPreviewWhere("none"));
selectStableLines.addEventListener("click", evt => selectPreviewWhere("white/stable"));
selectMiddleLines.addEventListener("click", evt => selectPreviewWhere("grey/middle"));
selectResidualLines.addEventListener("click", evt => selectPreviewWhere("black/residual"));

render();
</script>'''
)

out.write_text(text, encoding="utf-8")
print("WROTE", out)
