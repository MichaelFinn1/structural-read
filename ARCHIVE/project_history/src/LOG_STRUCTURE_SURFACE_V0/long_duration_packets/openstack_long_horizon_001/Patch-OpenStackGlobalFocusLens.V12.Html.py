from pathlib import Path
import re

base = Path("src/LOG_STRUCTURE_SURFACE_V0/long_duration_packets/openstack_long_horizon_001/visualizations")
src = base / "openstack_global_focus_lens_v10.html"
out = base / "openstack_global_focus_lens_v12.html"

text = src.read_text(encoding="utf-8")
text = text.replace("OpenStack Global Focus Lens V10", "OpenStack Global Focus Lens V12")

text = text.replace("</style>", """
.packetTray { border: 1px solid #999; padding: 10px; margin-top: 10px; }
.packetButtons { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 8px; }
.packetButtons button { font-size: 14px; padding: 5px 8px; }
.packetList { border: 1px solid #bbb; min-height: 80px; max-height: 180px; overflow: auto; padding: 8px; font-family: Consolas, monospace; font-size: 12px; white-space: pre-wrap; }
.packetHint { font-size: 13px; margin-top: 6px; color: #333; }
</style>""")

insert = '''
<div class="packetTray">
  <div style="font-size:18px; text-align:center;">CSV packet tray</div>
  <div class="packetButtons">
    <button id="addViewReceipt">Add current view</button>
    <button id="addSelectedRaw">Add selected raw lines</button>
    <button id="addStickyToPacket">Add current note</button>
    <button id="exportPacketCsv">Export CSV</button>
    <button id="clearPacket">Clear packet</button>
  </div>
  <div id="packetList" class="packetList">No packet rows yet.</div>
  <div class="packetHint">Rows are exported in the order added.</div>
</div>
'''

text = re.sub(
    r'(<pre id="linePreview"[\s\S]*?</pre>)',
    r'\1\n' + insert,
    text,
    count=1
)

text = text.replace(
'const linePreviewLabel = document.getElementById("linePreviewLabel");',
'''const linePreviewLabel = document.getElementById("linePreviewLabel");
const addViewReceipt = document.getElementById("addViewReceipt");
const addSelectedRaw = document.getElementById("addSelectedRaw");
const addStickyToPacket = document.getElementById("addStickyToPacket");
const exportPacketCsv = document.getElementById("exportPacketCsv");
const clearPacket = document.getElementById("clearPacket");
const packetList = document.getElementById("packetList");

let packetRows = [];'''
)

packet_js = r'''
function csvEscape(v) {
  const s = String(v === undefined || v === null ? "" : v);
  return '"' + s.replaceAll('"', '""') + '"';
}

function packetStateBase(itemType) {
  const s = state();
  return {
    item_type: itemType,
    terrain: "OpenStack_long_normal2",
    global_window: s.globalSize,
    focus_window: s.focusSize,
    focus_start: s.start,
    focus_end: s.end,
    focus_width: s.span,
    created_local: new Date().toISOString()
  };
}

function renderPacketRows() {
  if (packetRows.length === 0) {
    packetList.textContent = "No packet rows yet.";
    return;
  }

  packetList.textContent = packetRows.map((r, i) => {
    return String(i + 1).padStart(3, " ") + " | " +
      r.item_type + " | " +
      (r.raw_start || "") + "-" + (r.raw_end || "") + " | " +
      (r.note || "").substring(0, 80);
  }).join("\\n");
}

function addPacketRow(row) {
  row.sequence = packetRows.length + 1;
  packetRows.push(row);
  renderPacketRows();
}

addViewReceipt.addEventListener("click", evt => {
  const row = packetStateBase("view_receipt");
  row.raw_start = "";
  row.raw_end = "";
  row.line_number = "";
  row.posture = "";
  row.note = "current view";
  row.unresolved = "";
  addPacketRow(row);
});

addSelectedRaw.addEventListener("click", evt => {
  const row = packetStateBase("raw_span");
  const label = linePreviewLabel.textContent || "";

  const m = label.match(/Selected raw lines:\\s*(\\d+)\\-(\\d+)/);
  row.raw_start = m ? m[1] : row.focus_start;
  row.raw_end = m ? m[2] : row.focus_end;
  row.line_number = "";
  row.posture = "";
  row.note = linePreview.textContent || "";
  row.unresolved = "";
  addPacketRow(row);
});

addStickyToPacket.addEventListener("click", evt => {
  const row = packetStateBase("sticky_note");
  row.raw_start = "";
  row.raw_end = "";
  row.line_number = "";
  row.posture = "";
  row.note = noteText ? noteText.value : "";
  row.unresolved = unresolvedText ? unresolvedText.value : "";
  addPacketRow(row);
});

clearPacket.addEventListener("click", evt => {
  packetRows = [];
  renderPacketRows();
});

exportPacketCsv.addEventListener("click", evt => {
  const headers = [
    "sequence",
    "item_type",
    "terrain",
    "global_window",
    "focus_window",
    "focus_start",
    "focus_end",
    "focus_width",
    "raw_start",
    "raw_end",
    "line_number",
    "posture",
    "note",
    "unresolved",
    "created_local"
  ];

  const lines = [];
  lines.push(headers.join(","));

  packetRows.forEach(r => {
    lines.push(headers.map(h => csvEscape(r[h])).join(","));
  });

  const blob = new Blob([lines.join("\\n")], { type: "text/csv" });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = "openstack_investigation_packet_v1.csv";
  document.body.appendChild(a);
  a.click();
  a.remove();

  URL.revokeObjectURL(url);
});

'''

idx = text.rfind("render();")
if idx < 0:
    raise RuntimeError("Could not find final render();")

text = text[:idx] + packet_js + "\n" + text[idx:]

out.write_text(text, encoding="utf-8")
print("WROTE", out)
