import csv, json
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/long_duration_packets/netsparker_long_horizon_001")
SRC = BASE / "measured" / "traversal_windows_v0.csv"
OUT = BASE / "visualizations" / "netsparker_long_horizon_focus_dial_v1.html"

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))

for r in rows:
    for k in ["window_size","line_start","line_end","stable_share","middle_share","residual_share"]:
        r[k] = float(r[k])

sizes = sorted(set(int(r["window_size"]) for r in rows))
max_line = max(int(r["line_end"]) for r in rows)

payload = {"rows": rows, "sizes": sizes, "max_line": max_line}

html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Netsparker Long Horizon Focus Dial V1</title>
<style>
body {{ font-family: Georgia, serif; margin: 28px; background: white; }}
h1 {{ text-align: center; font-weight: normal; }}
#wrap {{ width: 96%; margin: 0 auto; }}
.control {{ margin: 18px 0; }}
input[type=range] {{ width: 100%; }}
#label {{ text-align: center; font-size: 20px; margin: 18px; }}
.bar {{ position: relative; height: 120px; border: 1px solid black; margin-top: 25px; display: flex; }}
.seg {{ height: 100%; }}
.stable {{ background: white; }}
.middle {{ background: #bfbfbf; }}
.residual {{ background: #222222; }}
.legend {{ text-align: center; margin-top: 22px; font-size: 16px; }}
.note {{ margin-top: 22px; font-size: 16px; }}
.small {{ font-size: 14px; }}
</style>
</head>
<body>
<div id="wrap">
<h1>Netsparker Long Horizon Focus Dial V1</h1>

<div id="label"></div>

<div class="control">
<div class="small">Constitution / window size</div>
<input id="dial" type="range" min="0" max="{len(sizes)-1}" value="0" step="1">
</div>

<div class="control">
<div class="small">Focus start line</div>
<input id="focusStart" type="range" min="1" max="{max_line}" value="1" step="1">
</div>

<div class="control">
<div class="small">Focus end line</div>
<input id="focusEnd" type="range" min="1" max="{max_line}" value="{max_line}" step="1">
</div>

<div id="bar" class="bar"></div>

<div class="legend">white = stable | grey = middle | black = residual</div>

<div class="note">
Window size changes reread constitution. Focus range changes descent region.
This view supports local inspection without claiming hidden trajectory or semantic state.
</div>
</div>

<script>
const data = {json.dumps(payload)};
const dial = document.getElementById("dial");
const startCtl = document.getElementById("focusStart");
const endCtl = document.getElementById("focusEnd");
const bar = document.getElementById("bar");
const label = document.getElementById("label");

function overlap(a1, a2, b1, b2) {{
    const s = Math.max(a1, b1);
    const e = Math.min(a2, b2);
    if (e < s) return 0;
    return e - s + 1;
}}

function render() {{
    const size = data.sizes[parseInt(dial.value)];
    let focusStart = parseInt(startCtl.value);
    let focusEnd = parseInt(endCtl.value);

    if (focusStart > focusEnd) {{
        const tmp = focusStart;
        focusStart = focusEnd;
        focusEnd = tmp;
    }}

    const focusWidth = focusEnd - focusStart + 1;

    label.innerHTML =
        "window size: " + size +
        " | focus: lines " + focusStart + "-" + focusEnd +
        " | visible span: " + focusWidth + " lines";

    bar.innerHTML = "";

    const rows = data.rows.filter(r =>
        parseInt(r.window_size) === size &&
        parseInt(r.line_end) >= focusStart &&
        parseInt(r.line_start) <= focusEnd
    );

    rows.forEach(r => {{
        const visible = overlap(
            parseInt(r.line_start),
            parseInt(r.line_end),
            focusStart,
            focusEnd
        );

        if (visible <= 0) return;

        [
            ["stable", r.stable_share],
            ["middle", r.middle_share],
            ["residual", r.residual_share]
        ].forEach(pair => {{
            const div = document.createElement("div");
            div.className = "seg " + pair[0];
            div.style.width = (pair[1] * visible / focusWidth * 100) + "%";
            div.title =
                "lines " + r.line_start + "-" + r.line_end +
                " | " + pair[0] + ": " + pair[1].toFixed(3);
            bar.appendChild(div);
        }});
    }});
}}

dial.addEventListener("input", render);
startCtl.addEventListener("input", render);
endCtl.addEventListener("input", render);
render();
</script>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print("WROTE", OUT.resolve())
