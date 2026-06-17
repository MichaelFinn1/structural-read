from pathlib import Path
import re

base = Path("src/LOG_STRUCTURE_SURFACE_V0/long_duration_packets/openstack_long_horizon_001/visualizations")
src = base / "openstack_global_focus_lens_v7.html"
out = base / "openstack_global_focus_lens_v8.html"

text = src.read_text(encoding="utf-8")
text = text.replace("OpenStack Global Focus Lens V7", "OpenStack Global Focus Lens V8")

text = text.replace("</style>", """
.selectedSpan { position:absolute; top:0; height:100%; border-left:3px solid red; border-right:3px solid red; background: rgba(255,0,0,0.18); pointer-events:none; }
</style>""")

text = text.replace(
"let bookmarks = [];",
"let bookmarks = [];\nlet selectedStart = null;\nlet selectedEnd = null;"
)

text = text.replace(
"renderBar(focusBar, s.focusSize, s.start, s.end, false);",
"""renderBar(focusBar, s.focusSize, s.start, s.end, false);
  addSelectedSpan();"""
)

insert_before = "function previewLineRange(startLine, endLine) {"
helper = r'''
function dominantPostureForLine(line, size) {
  const rows = data.rows.filter(r =>
    parseInt(r.window_size) === size &&
    r.line_start <= line &&
    r.line_end >= line
  );

  if (rows.length === 0) return "unmapped";

  const r = rows[0];
  const vals = [
    ["white/stable", r.stable_share],
    ["grey/middle", r.middle_share],
    ["black/residual", r.residual_share]
  ];

  vals.sort((a, b) => b[1] - a[1]);
  return vals[0][0];
}

function addSelectedSpan() {
  if (selectedStart === null || selectedEnd === null) return;

  const s = state();
  const a = Math.max(Math.min(selectedStart, selectedEnd), s.start);
  const b = Math.min(Math.max(selectedStart, selectedEnd), s.end);

  if (b < s.start || a > s.end) return;

  const div = document.createElement("div");
  div.className = "selectedSpan";
  div.style.left = ((a - s.start) / (s.end - s.start + 1) * 100) + "%";
  div.style.width = ((b - a + 1) / (s.end - s.start + 1) * 100) + "%";
  focusBar.appendChild(div);
}

'''
text = text.replace(insert_before, helper + insert_before, 1)

text = re.sub(
    r'function previewLineRange\(startLine, endLine\) \{[\s\S]*?\n\}',
    r'''function previewLineRange(startLine, endLine) {
  const s = state();
  const start = Math.max(1, Math.min(startLine, endLine));
  const end = Math.min(data.max_line, Math.max(startLine, endLine));
  const cappedEnd = Math.min(end, start + 250);

  selectedStart = start;
  selectedEnd = end;

  let out = [];
  for (let i = start; i <= cappedEnd; i++) {
    const line = data.source_lines[i - 1] || "";
    const posture = dominantPostureForLine(i, s.focusSize);
    out.push(String(i).padStart(8, " ") + " | " + posture.padEnd(14, " ") + " | " + line);
  }

  let suffix = "";
  if (cappedEnd < end) {
    suffix = "\\n\\n... preview capped at 250 lines. Selected range continues to " + end + ".";
  }

  linePreviewLabel.innerHTML = "Selected raw lines: " + start + "-" + end + " | focus window " + s.focusSize;
  linePreview.textContent = out.join("\\n") + suffix;
  render();
}''',
    text,
    count=1
)

text = re.sub(
    r'function previewLines\(centerLine\) \{[\s\S]*?\n\}',
    r'''function previewLines(centerLine) {
  const radius = 8;
  previewLineRange(centerLine - radius, centerLine + radius);
}''',
    text,
    count=1
)

text = re.sub(
    r'raw_start: s\.start,\s*raw_end: s\.end,',
    r'''raw_start: selectedStart === null ? s.start : selectedStart,
    raw_end: selectedEnd === null ? s.end : selectedEnd,''',
    text,
    count=1
)

text = text.replace(
'''      noteText.value = b.operator_note;
      unresolvedText.value = b.unresolved_status;

      render();
      previewLineRange(parseInt(b.raw_start), parseInt(b.raw_end));''',
'''      selectedStart = parseInt(b.raw_start);
      selectedEnd = parseInt(b.raw_end);

      noteText.value = b.operator_note;
      unresolvedText.value = b.unresolved_status;

      render();
      previewLineRange(selectedStart, selectedEnd);'''
)

text = text.replace(
'''  noteText.value = "";
  unresolvedText.value = "";
});''',
'''  selectedStart = null;
  selectedEnd = null;
  noteText.value = "";
  unresolvedText.value = "";
  bookmarkPreview.textContent = "";
  linePreviewLabel.innerHTML = "Selected raw lines";
  linePreview.textContent = "Click or drag inside the focus lens to preview precise raw source lines.";
  render();
});''',
1
)

out.write_text(text, encoding="utf-8")
print("WROTE", out)
