from pathlib import Path

base = Path("src/LOG_STRUCTURE_SURFACE_V0/long_duration_packets/openstack_long_horizon_001/visualizations")
src = base / "openstack_global_focus_lens_v14.html"
out = base / "openstack_global_focus_lens_v15.html"

text = src.read_text(encoding="utf-8")
text = text.replace("OpenStack Global Focus Lens V14", "OpenStack Global Focus Lens V15")

text = text.replace("</style>", """
.signatureBox { border: 1px solid #999; padding: 10px; margin-top: 14px; }
.signatureList { border: 1px solid #bbb; min-height: 80px; max-height: 220px; overflow: auto; padding: 8px; font-family: Consolas, monospace; font-size: 12px; white-space: pre-wrap; }
.signatureButtons { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 8px; }
.signatureButtons button { font-size: 14px; padding: 5px 8px; }
</style>""")

signature_html = r'''
const signatureBox = document.createElement("div");
signatureBox.className = "signatureBox";
signatureBox.innerHTML = `
  <div style="font-size:18px; text-align:center;">Region signatures</div>
  <div class="signatureButtons">
    <button id="buildSignatures">Build card signatures</button>
    <button id="compareLastTwo">Compare last two signatures</button>
    <button id="clearSignatures">Clear signatures</button>
  </div>
  <div id="signatureList" class="signatureList">No region signatures yet.</div>
`;

document.getElementById("wrap").appendChild(signatureBox);

const buildSignatures = document.getElementById("buildSignatures");
const compareLastTwo = document.getElementById("compareLastTwo");
const clearSignatures = document.getElementById("clearSignatures");
const signatureList = document.getElementById("signatureList");

let regionSignatures = [];

function rowsForSpan(size, start, end) {
  return data.rows.filter(r =>
    parseInt(r.window_size) === parseInt(size) &&
    r.line_end >= start &&
    r.line_start <= end
  );
}

function signatureForBookmark(b) {
  const size = parseInt(b.focus_window);
  const start = parseInt(b.raw_start || b.focus_start);
  const end = parseInt(b.raw_end || b.focus_end);
  const rows = rowsForSpan(size, start, end);

  let total = 0;
  let stable = 0;
  let middle = 0;
  let residual = 0;
  let bandCount = rows.length;

  rows.forEach(r => {
    const a = Math.max(r.line_start, start);
    const z = Math.min(r.line_end, end);
    const width = Math.max(0, z - a + 1);

    total += width;
    stable += width * r.stable_share;
    middle += width * r.middle_share;
    residual += width * r.residual_share;
  });

  if (total <= 0) total = 1;

  const stableShare = stable / total;
  const middleShare = middle / total;
  const residualShare = residual / total;

  let dominant = "stable";
  if (middleShare >= stableShare && middleShare >= residualShare) dominant = "middle";
  if (residualShare >= stableShare && residualShare >= middleShare) dominant = "residual";

  return {
    bookmark_id: b.bookmark_id,
    note: b.operator_note || "",
    focus_window: size,
    raw_start: start,
    raw_end: end,
    stable_share: stableShare.toFixed(4),
    middle_share: middleShare.toFixed(4),
    residual_share: residualShare.toFixed(4),
    dominant_posture: dominant,
    band_count: bandCount,
    avg_band_width: (total / Math.max(1, bandCount)).toFixed(2),
    grey_presence: middleShare > 0.02 ? "present" : "thin_or_absent"
  };
}

function renderSignatures(extra) {
  if (regionSignatures.length === 0 && !extra) {
    signatureList.textContent = "No region signatures yet.";
    return;
  }

  let lines = [];

  regionSignatures.forEach((s, i) => {
    lines.push(
      String(i + 1).padStart(3, " ") +
      " | " + s.raw_start + "-" + s.raw_end +
      " | f" + s.focus_window +
      " | dom=" + s.dominant_posture +
      " | stable=" + s.stable_share +
      " middle=" + s.middle_share +
      " residual=" + s.residual_share +
      " | bands=" + s.band_count +
      " | grey=" + s.grey_presence +
      " | " + s.note.substring(0, 50)
    );
  });

  if (extra) {
    lines.push("");
    lines.push(extra);
  }

  signatureList.textContent = lines.join("\\n");
}

buildSignatures.addEventListener("click", evt => {
  regionSignatures = [];

  if (!bookmarks || bookmarks.length === 0) {
    signatureList.textContent = "No saved cards available.";
    return;
  }

  bookmarks.forEach(b => {
    regionSignatures.push(signatureForBookmark(b));
  });

  renderSignatures("");
});

compareLastTwo.addEventListener("click", evt => {
  if (regionSignatures.length < 2) {
    signatureList.textContent = "Need at least two signatures.";
    return;
  }

  const a = regionSignatures[regionSignatures.length - 2];
  const b = regionSignatures[regionSignatures.length - 1];

  const ds = (parseFloat(b.stable_share) - parseFloat(a.stable_share)).toFixed(4);
  const dm = (parseFloat(b.middle_share) - parseFloat(a.middle_share)).toFixed(4);
  const dr = (parseFloat(b.residual_share) - parseFloat(a.residual_share)).toFixed(4);

  const comparison =
    "CARD_COMPARISON_V1\\n" +
    "A: " + a.raw_start + "-" + a.raw_end + " dom=" + a.dominant_posture + "\\n" +
    "B: " + b.raw_start + "-" + b.raw_end + " dom=" + b.dominant_posture + "\\n" +
    "delta stable: " + ds + "\\n" +
    "delta middle: " + dm + "\\n" +
    "delta residual: " + dr + "\\n" +
    "read: coarse replay-addressable difference only; no semantic claim.";

  renderSignatures(comparison);
});

clearSignatures.addEventListener("click", evt => {
  regionSignatures = [];
  renderSignatures("");
});
'''

idx = text.rfind("render();")
if idx < 0:
    raise RuntimeError("Could not find final render();")

text = text[:idx] + signature_html + "\n" + text[idx:]

out.write_text(text, encoding="utf-8")
print("WROTE", out)
