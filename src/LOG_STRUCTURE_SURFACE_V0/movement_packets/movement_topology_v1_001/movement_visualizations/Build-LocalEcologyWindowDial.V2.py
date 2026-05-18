import csv, json
from pathlib import Path

SRC = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001/measured_netsparker_window_dial_v1/traversal_windows_v0.csv")
OUT = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001/movement_visualizations/local_ecology_window_dial_v2.html")

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))

for r in rows:
    for k in ["window_size","line_start","line_end","stable_share","middle_share","residual_share"]:
        r[k] = float(r[k])

sizes = sorted(set(int(r["window_size"]) for r in rows))
max_line = max(int(r["line_end"]) for r in rows)

payload = {"rows": rows, "sizes": sizes, "max_line": max_line}

html = f"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Local Ecology Window Dial V2</title>
<style>
body {{ font-family: Georgia, serif; margin: 30px; background: white; }}
h1 {{ text-align: center; font-weight: normal; }}
#wrap {{ width: 96%; margin: 0 auto; }}
#dial {{ width: 100%; }}
#label {{ text-align: center; font-size: 22px; margin: 20px; }}
.bar {{ position: relative; height: 95px; border: 1px solid black; margin-top: 35px; display: flex; }}
.seg {{ height: 100%; }}
.stable {{ background: white; }}
.middle {{ background: #bfbfbf; }}
.residual {{ background: #222222; }}
.windowBoundary {{ position: absolute; top: 0; bottom: 0; border-left: 1px solid #777; opacity: 0.7; display: none; }}
.controls {{ text-align: center; margin-top: 20px; font-size: 16px; }}
.legend {{ text-align: center; margin-top: 25px; font-size: 16px; }}
.note {{ margin-top: 25px; font-size: 16px; }}
</style>
</head>
<body>
<div id="wrap">
<h1>Local Ecology Window Dial V2</h1>
<div id="label"></div>
<input id="dial" type="range" min="0" max="{len(sizes)-1}" value="0" step="1">
<div class="controls">
<label><input id="boundaries" type="checkbox"> show measured window boundaries</label>
</div>
<div id="bar" class="bar"></div>
<div class="legend">white = stable | grey = middle | black = residual</div>
<div class="note">Read question: which visible features persist, drift, merge, split, or disappear as constitution changes?</div>
</div>

<script>
const data = {json.dumps(payload)};
const dial = document.getElementById("dial");
const bar = document.getElementById("bar");
const label = document.getElementById("label");
const boundaries = document.getElementById("boundaries");

function render() {{
  const size = data.sizes[parseInt(dial.value)];
  label.innerHTML = "window size: " + size;
  bar.innerHTML = "";

  const rows = data.rows.filter(r => parseInt(r.window_size) === size);

  rows.forEach(r => {{
    const total = r.line_end - r.line_start + 1;

    [["stable", r.stable_share], ["middle", r.middle_share], ["residual", r.residual_share]].forEach(pair => {{
      const div = document.createElement("div");
      div.className = "seg " + pair[0];
      div.style.width = (pair[1] * total / data.max_line * 100) + "%";
      bar.appendChild(div);
    }});

    const b = document.createElement("div");
    b.className = "windowBoundary";
    b.style.left = ((r.line_start - 1) / data.max_line * 100) + "%";
    b.style.display = boundaries.checked ? "block" : "none";
    bar.appendChild(b);
  }});
}}

dial.addEventListener("input", render);
boundaries.addEventListener("change", render);
render();
</script>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print("WROTE")
print(OUT.resolve())
