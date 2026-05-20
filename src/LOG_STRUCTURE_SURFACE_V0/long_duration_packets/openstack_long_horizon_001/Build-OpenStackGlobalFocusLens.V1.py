import csv, json
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/long_duration_packets/openstack_long_horizon_001")
SRC = BASE / "measured" / "traversal_windows_v0.csv"
OUT = BASE / "visualizations" / "openstack_global_focus_lens_v1.html"

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))

for r in rows:
    for k in ["window_size","line_start","line_end","stable_share","middle_share","residual_share"]:
        r[k] = float(r[k])

sizes = sorted(set(int(r["window_size"]) for r in rows))
max_line = max(int(r["line_end"]) for r in rows)

payload = {
    "rows": rows,
    "sizes": sizes,
    "max_line": max_line
}

html = f"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>OpenStack Global Focus Lens V1</title>
<style>
body {{
    font-family: Georgia, serif;
    margin: 28px;
    background: white;
}}
h1 {{
    text-align: center;
    font-weight: normal;
}}
#wrap {{
    width: 96%;
    margin: 0 auto;
}}
.controls {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 18px;
    margin: 20px 0;
}}
.controlBox {{
    border: 1px solid #999;
    padding: 12px;
}}
input[type=range] {{
    width: 100%;
}}
input[type=number] {{
    width: 100%;
    font-size: 16px;
}}
.label {{
    text-align: center;
    font-size: 20px;
    margin: 12px;
}}
.bar {{
    position: relative;
    height: 72px;
    border: 1px solid black;
    margin-top: 18px;
    display: flex;
    overflow: hidden;
}}
.focusBar {{
    height: 140px;
}}
.seg {{
    height: 100%;
}}
.stable {{
    background: white;
}}
.middle {{
    background: #bfbfbf;
}}
.residual {{
    background: #222222;
}}
.lens {{
    position: absolute;
    top: 0;
    height: 100%;
    border-left: 3px solid red;
    border-right: 3px solid red;
    background: rgba(255,0,0,0.08);
    pointer-events: none;
}}
.legend {{
    text-align: center;
    margin-top: 18px;
    font-size: 15px;
}}
.note {{
    margin-top: 22px;
    font-size: 16px;
    line-height: 1.4;
}}
button {{
    font-size: 15px;
    margin: 4px;
}}
</style>
</head>
<body>
<div id="wrap">
<h1>OpenStack Global Focus Lens V1</h1>

<div class="controls">
  <div class="controlBox">
    <div>Constitution / window size</div>
    <input id="sizeDial" type="range" min="0" max="{len(sizes)-1}" value="0" step="1">
    <div id="sizeLabel" class="label"></div>
  </div>

  <div class="controlBox">
    <div>Focus start line</div>
    <input id="startInput" type="number" min="1" max="{max_line}" value="29600">
    <button onclick="shiftFocus(-1000)">-1000</button>
    <button onclick="shiftFocus(-100)">-100</button>
    <button onclick="shiftFocus(100)">+100</button>
    <button onclick="shiftFocus(1000)">+1000</button>
  </div>

  <div class="controlBox">
    <div>Focus end line</div>
    <input id="endInput" type="number" min="1" max="{max_line}" value="33000">
    <button onclick="setSpan(1000)">span 1000</button>
    <button onclick="setSpan(2500)">span 2500</button>
    <button onclick="setSpan(5000)">span 5000</button>
    <button onclick="setSpan(10000)">span 10000</button>
  </div>
</div>

<div class="label" id="globalLabel"></div>
<div id="globalBar" class="bar"></div>

<div class="label" id="focusLabel"></div>
<div id="focusBar" class="bar focusBar"></div>

<div class="legend">
white = stable | grey = middle | black = residual | red lens = selected focus region
</div>

<div class="note">
This view separates global orientation from local descent. The upper bar preserves the whole terrain under the selected constitution. The red lens marks the selected region. The lower bar magnifies only that region without erasing the global map.
</div>
</div>

<script>
const data = {json.dumps(payload)};

const sizeDial = document.getElementById("sizeDial");
const startInput = document.getElementById("startInput");
const endInput = document.getElementById("endInput");
const globalBar = document.getElementById("globalBar");
const focusBar = document.getElementById("focusBar");
const sizeLabel = document.getElementById("sizeLabel");
const globalLabel = document.getElementById("globalLabel");
const focusLabel = document.getElementById("focusLabel");

function clamp(v, lo, hi) {{
    return Math.max(lo, Math.min(hi, v));
}}

function getState() {{
    let start = parseInt(startInput.value);
    let end = parseInt(endInput.value);

    start = clamp(start, 1, data.max_line);
    end = clamp(end, 1, data.max_line);

    if (end < start) {{
        const t = start;
        start = end;
        end = t;
    }}

    startInput.value = start;
    endInput.value = end;

    const size = data.sizes[parseInt(sizeDial.value)];

    return {{size, start, end}};
}}

function clearBar(bar) {{
    bar.innerHTML = "";
}}

function addSeg(bar, cls, widthPct) {{
    const div = document.createElement("div");
    div.className = "seg " + cls;
    div.style.width = widthPct + "%";
    bar.appendChild(div);
}}

function renderGlobal(size, start, end) {{
    clearBar(globalBar);

    const rows = data.rows.filter(r => parseInt(r.window_size) === size);

    rows.forEach(r => {{
        const total = r.line_end - r.line_start + 1;

        [["stable", r.stable_share], ["middle", r.middle_share], ["residual", r.residual_share]].forEach(pair => {{
            addSeg(globalBar, pair[0], pair[1] * total / data.max_line * 100);
        }});
    }});

    const lens = document.createElement("div");
    lens.className = "lens";
    lens.style.left = ((start - 1) / data.max_line * 100) + "%";
    lens.style.width = ((end - start + 1) / data.max_line * 100) + "%";
    globalBar.appendChild(lens);

    globalLabel.innerHTML = "Global terrain span: 1-" + data.max_line;
}}

function renderFocus(size, start, end) {{
    clearBar(focusBar);

    const span = end - start + 1;
    const rows = data.rows.filter(r =>
        parseInt(r.window_size) === size &&
        r.line_end >= start &&
        r.line_start <= end
    );

    rows.forEach(r => {{
        const localStart = Math.max(r.line_start, start);
        const localEnd = Math.min(r.line_end, end);
        const total = localEnd - localStart + 1;

        [["stable", r.stable_share], ["middle", r.middle_share], ["residual", r.residual_share]].forEach(pair => {{
            addSeg(focusBar, pair[0], pair[1] * total / span * 100);
        }});
    }});

    focusLabel.innerHTML = "Focus region: " + start + "-" + end + " | visible span: " + span;
}}

function render() {{
    const st = getState();
    sizeLabel.innerHTML = "window size: " + st.size;
    renderGlobal(st.size, st.start, st.end);
    renderFocus(st.size, st.start, st.end);
}}

function shiftFocus(delta) {{
    let start = parseInt(startInput.value);
    let end = parseInt(endInput.value);
    const span = end - start;
    start = clamp(start + delta, 1, data.max_line - span);
    end = start + span;
    startInput.value = start;
    endInput.value = end;
    render();
}}

function setSpan(span) {{
    let start = parseInt(startInput.value);
    let end = start + span - 1;
    if (end > data.max_line) {{
        end = data.max_line;
        start = Math.max(1, end - span + 1);
    }}
    startInput.value = start;
    endInput.value = end;
    render();
}}

sizeDial.addEventListener("input", render);
startInput.addEventListener("change", render);
endInput.addEventListener("change", render);

render();
</script>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print("WROTE", OUT.resolve())
