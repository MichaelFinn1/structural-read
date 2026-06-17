from pathlib import Path

base = Path("src/LOG_STRUCTURE_SURFACE_V0/long_duration_packets/openstack_long_horizon_001/visualizations")
src = base / "openstack_global_focus_lens_v9.html"
out = base / "openstack_global_focus_lens_v10.html"

text = src.read_text(encoding="utf-8")
text = text.replace("OpenStack Global Focus Lens V9", "OpenStack Global Focus Lens V10")

# allow narrower focus width
text = text.replace('id="spanDial" type="range" min="500"', 'id="spanDial" type="range" min="25"')
text = text.replace('const span = Math.max(500, b - a + 1);', 'const span = Math.max(parseInt(spanDial.min), b - a + 1);')

# add single-line detail pane
text = text.replace(
'<div id="packageSummary">Selected package: none</div>',
'''<div id="packageSummary">Selected package: none</div>
<div class="box" style="margin-top:10px;">
  <div>Selected single log line</div>
  <pre id="singleLineView" style="border:1px solid #999; padding:10px; white-space:pre-wrap; font-family:Consolas, monospace; font-size:13px;">Click one raw line below to view it here.</pre>
</div>'''
)

text = text.replace(
'const packageSummary = document.getElementById("packageSummary");',
'''const packageSummary = document.getElementById("packageSummary");
const singleLineView = document.getElementById("singleLineView");
let activeLine = null;'''
)

# clicking a raw row opens it in detail pane
text = text.replace(
'''    row.appendChild(cb);
    row.appendChild(ln);
    row.appendChild(po);
    row.appendChild(tx);
    linePreview.appendChild(row);''',
'''    row.appendChild(cb);
    row.appendChild(ln);
    row.appendChild(po);
    row.appendChild(tx);

    row.addEventListener("click", evt => {
      if (evt.target.tagName.toLowerCase() === "input") return;
      activeLine = r.line_no;
      singleLineView.textContent =
        "line " + r.line_no + " | " + r.posture + "\\n\\n" + r.text;
    });

    linePreview.appendChild(row);'''
)

# save active line with bookmark
text = text.replace(
'''included_count: includedLines.size,''',
'''included_count: includedLines.size,
    active_line: activeLine,''',
1
)

# reload active line from card
text = text.replace(
'''      previewLineRange(selectedStart, selectedEnd, b.included_lines || null);''',
'''      previewLineRange(selectedStart, selectedEnd, b.included_lines || null);

      if (b.active_line) {
        activeLine = parseInt(b.active_line);
        const line = data.source_lines[activeLine - 1] || "";
        const posture = dominantPostureForLine(activeLine, data.sizes[parseInt(focusSizeDial.value)]);
        singleLineView.textContent =
          "line " + activeLine + " | " + posture + "\\n\\n" + line;
      }'''
)

# clear detail after save
text = text.replace(
'''  packageSummary.innerHTML = "Selected package: none";
  previewRows = [];''',
'''  packageSummary.innerHTML = "Selected package: none";
  singleLineView.textContent = "Click one raw line below to view it here.";
  activeLine = null;
  previewRows = [];'''
)

out.write_text(text, encoding="utf-8")
print("WROTE", out)
