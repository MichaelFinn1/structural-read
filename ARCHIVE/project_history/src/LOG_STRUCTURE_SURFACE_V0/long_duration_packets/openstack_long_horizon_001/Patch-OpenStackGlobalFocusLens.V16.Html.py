from pathlib import Path

base = Path("src/LOG_STRUCTURE_SURFACE_V0/long_duration_packets/openstack_long_horizon_001/visualizations")
src = base / "openstack_global_focus_lens_v15.html"
out = base / "openstack_global_focus_lens_v16.html"

text = src.read_text(encoding="utf-8")
text = text.replace("OpenStack Global Focus Lens V15", "OpenStack Global Focus Lens V16")

text = text.replace("</style>", """
.bandSignatureBox { border: 1px solid #999; padding: 10px; margin-top: 14px; }
.bandSignatureList { border: 1px solid #bbb; min-height: 80px; max-height: 260px; overflow: auto; padding: 8px; font-family: Consolas, monospace; font-size: 12px; white-space: pre-wrap; }
.bandSignatureButtons { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 8px; }
.bandSignatureButtons button { font-size: 14px; padding: 5px 8px; }
</style>""")

band_js = r'''
const bandSignatureBox = document.createElement("div");
bandSignatureBox.className = "bandSignatureBox";
bandSignatureBox.innerHTML = `
  <div style="font-size:18px; text-align:center;">Card internal band signatures</div>
  <div class="bandSignatureButtons">
    <button id="buildBandSignatures">Build internal band signatures</button>
    <button id="compareLastTwoBandSignatures">Compare last two band signatures</button>
    <button id="clearBandSignatures">Clear band signatures</button>
  </div>
  <div id="bandSignatureList" class="bandSignatureList">No internal band signatures yet.</div>
`;

document.getElementById("wrap").appendChild(bandSignatureBox);

const buildBandSignatures = document.getElementById("buildBandSignatures");
const compareLastTwoBandSignatures = document.getElementById("compareLastTwoBandSignatures");
const clearBandSignatures = document.getElementById("clearBandSignatures");
const bandSignatureList = document.getElementById("bandSignatureList");

let bandSignatures = [];

function colorForPart(part) {
  if (part === "stable") return "white";
  if (part === "middle") return "grey";
  if (part === "residual") return "black";
  return part;
}

function mergeBand(seq, color, width) {
  if (width <= 0) return;
  const last = seq.length > 0 ? seq[seq.length - 1] : null;
  if (last && last.color === color) {
    last.width += width;
  } else {
    seq.push({ color: color, width: width });
  }
}

function internalBandSignatureForBookmark(b) {
  const size = parseInt(b.focus_window);
  const start = parseInt(b.raw_start || b.focus_start);
  const end = parseInt(b.raw_end || b.focus_end);

  const rows = data.rows
    .filter(r =>
      parseInt(r.window_size) === size &&
      r.line_end >= start &&
      r.line_start <= end
    )
    .sort((a, z) => a.line_start - z.line_start);

  let seq = [];

  rows.forEach(r => {
    const a = Math.max(r.line_start, start);
    const z = Math.min(r.line_end, end);
    const overlap = Math.max(0, z - a + 1);

    [
      ["stable", r.stable_share],
      ["middle", r.middle_share],
      ["residual", r.residual_share]
    ].forEach(pair => {
      const width = overlap * pair[1];
      if (width >= 1) {
        mergeBand(seq, colorForPart(pair[0]), width);
      }
    });
  });

  let totals = { white: 0, grey: 0, black: 0 };
  let counts = { white: 0, grey: 0, black: 0 };

  seq.forEach(band => {
    totals[band.color] += band.width;
    counts[band.color] += 1;
  });

  const whiteIndexes = [];
  seq.forEach((band, i) => {
    if (band.color === "white") whiteIndexes.push(i);
  });

  let firstWhiteOffset = "";
  let secondWhiteOffset = "";
  let distanceBetweenWhiteBands = "";

  if (whiteIndexes.length >= 1) {
    firstWhiteOffset = seq.slice(0, whiteIndexes[0]).reduce((a, x) => a + x.width, 0).toFixed(1);
  }

  if (whiteIndexes.length >= 2) {
    secondWhiteOffset = seq.slice(0, whiteIndexes[1]).reduce((a, x) => a + x.width, 0).toFixed(1);
    distanceBetweenWhiteBands = (
      seq.slice(0, whiteIndexes[1]).reduce((a, x) => a + x.width, 0) -
      seq.slice(0, whiteIndexes[0]).reduce((a, x) => a + x.width, 0)
    ).toFixed(1);
  }

  let greyAttachedToWhite = "no";
  seq.forEach((band, i) => {
    if (band.color === "grey") {
      const left = i > 0 ? seq[i - 1].color : "";
      const right = i < seq.length - 1 ? seq[i + 1].color : "";
      if (left === "white" || right === "white") greyAttachedToWhite = "yes";
    }
  });

  const compactSeq = seq.map(x => x.color).join(" -> ");
  const widthPattern = seq.map(x => x.color + ":" + x.width.toFixed(1)).join(" | ");

  return {
    bookmark_id: b.bookmark_id,
    note: b.operator_note || "",
    focus_window: size,
    raw_start: start,
    raw_end: end,
    band_sequence: compactSeq,
    white_band_count: counts.white,
    grey_band_count: counts.grey,
    black_band_count: counts.black,
    white_width_total: totals.white.toFixed(1),
    grey_width_total: totals.grey.toFixed(1),
    black_width_total: totals.black.toFixed(1),
    first_white_offset: firstWhiteOffset,
    second_white_offset: secondWhiteOffset,
    distance_between_white_bands: distanceBetweenWhiteBands,
    grey_attached_to_white: greyAttachedToWhite,
    band_width_pattern: widthPattern
  };
}

function renderBandSignatures(extra) {
  if (bandSignatures.length === 0 && !extra) {
    bandSignatureList.textContent = "No internal band signatures yet.";
    return;
  }

  let lines = [];

  bandSignatures.forEach((s, i) => {
    lines.push(
      String(i + 1).padStart(3, " ") +
      " | " + s.raw_start + "-" + s.raw_end +
      " | f" + s.focus_window +
      " | W/G/B counts=" + s.white_band_count + "/" + s.grey_band_count + "/" + s.black_band_count +
      " | W/G/B width=" + s.white_width_total + "/" + s.grey_width_total + "/" + s.black_width_total +
      " | firstW=" + s.first_white_offset +
      " secondW=" + s.second_white_offset +
      " distW=" + s.distance_between_white_bands +
      " | grey_attached=" + s.grey_attached_to_white +
      " | " + s.note.substring(0, 45)
    );

    lines.push("    seq: " + s.band_sequence);
    lines.push("    widths: " + s.band_width_pattern);
  });

  if (extra) {
    lines.push("");
    lines.push(extra);
  }

  bandSignatureList.textContent = lines.join("\\n");
}

buildBandSignatures.addEventListener("click", evt => {
  bandSignatures = [];

  if (!bookmarks || bookmarks.length === 0) {
    bandSignatureList.textContent = "No saved cards available.";
    return;
  }

  bookmarks.forEach(b => {
    bandSignatures.push(internalBandSignatureForBookmark(b));
  });

  renderBandSignatures("");
});

compareLastTwoBandSignatures.addEventListener("click", evt => {
  if (bandSignatures.length < 2) {
    bandSignatureList.textContent = "Need at least two internal band signatures.";
    return;
  }

  const a = bandSignatures[bandSignatures.length - 2];
  const b = bandSignatures[bandSignatures.length - 1];

  const comparison =
    "CARD_INTERNAL_BAND_COMPARISON_V1\\n" +
    "A: " + a.raw_start + "-" + a.raw_end + "\\n" +
    "B: " + b.raw_start + "-" + b.raw_end + "\\n" +
    "\\n" +
    "white count: " + a.white_band_count + " -> " + b.white_band_count + "\\n" +
    "grey count: " + a.grey_band_count + " -> " + b.grey_band_count + "\\n" +
    "black count: " + a.black_band_count + " -> " + b.black_band_count + "\\n" +
    "white width total: " + a.white_width_total + " -> " + b.white_width_total + "\\n" +
    "grey width total: " + a.grey_width_total + " -> " + b.grey_width_total + "\\n" +
    "black width total: " + a.black_width_total + " -> " + b.black_width_total + "\\n" +
    "first white offset: " + a.first_white_offset + " -> " + b.first_white_offset + "\\n" +
    "second white offset: " + a.second_white_offset + " -> " + b.second_white_offset + "\\n" +
    "distance between white bands: " + a.distance_between_white_bands + " -> " + b.distance_between_white_bands + "\\n" +
    "grey attached to white: " + a.grey_attached_to_white + " -> " + b.grey_attached_to_white + "\\n" +
    "\\n" +
    "read: internal band grammar only; no semantic claim.";

  renderBandSignatures(comparison);
});

clearBandSignatures.addEventListener("click", evt => {
  bandSignatures = [];
  renderBandSignatures("");
});
'''

idx = text.rfind("render();")
if idx < 0:
    raise RuntimeError("Could not find final render();")

text = text[:idx] + band_js + "\n" + text[idx:]

out.write_text(text, encoding="utf-8")
print("WROTE", out)
