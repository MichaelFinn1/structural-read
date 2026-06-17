import csv, json
from pathlib import Path

SRC = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001/measured_netsparker_window_dial_v1/traversal_windows_v0.csv")
OUT = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001/movement_visualizations/local_ecology_window_dial_v3_soft.html")

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))

for r in rows:
    for k in ["window_size", "line_start", "line_end", "stable_share", "middle_share", "residual_share"]:
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
<title>Local Ecology Window Dial V3 Soft</title>
<style>
body {{
  font-family: Georgia, serif;
  margin: 30px;
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
#dial {{
  width: 100%;
}}
#label {{
  text-align: center;
  font-size: 22px;
  margin: 20px;
}}
.bar {{
  position: relative;
  height: 95px;
  border: 1px solid #999;
  margin-top: 35px;
  display: flex;
  overflow: hidden;
  border-radius: 12px;
  background: #f7f7f7;
}}
.seg {{
  height: 100%;
}}
.stable {{
  background: rgba(245,245,245,0.95);
}}
.middle {{
  background: rgba(120,120,120,0.38);
}}
.residual {{
  background: rgba(30,30,30,0.62);
}}
.windowBoundary {{
  position: absolute;
  top: 0;
  bottom: 0;
  border-left: 1px solid #777;
  opacity: 0.45;
  display: none;
}}
.controls {{
  text-align: center;
  margin-top: 20px;
  font-size: 16px;
}}
.legend {{
  text-align: center;
  margin-top: 25px;
  font-size: 16px;
}}
.note {{
  margin-top: 25px;
  font-size: 16px;
  line-height: 1.45;
}}
</style>
</head>
<body>
<div id="wrap">
<h1>Local Ecology Window Dial V3 Soft</h1>
<div id="label"></div>
<input id="dial" type="range" min="0" max="{len(sizes)-1}" value="0" step="1">

<div class="controls">
<label><input id="boundaries" type="checkbox"> show measured window boundaries</label>
</div>

<div id="bar" class="bar"></div>

<div class="legend">
light field = stable participation | soft grey = middle participation | dark density = residual participation
</div>

<div class="note">
Read question: how does one emitted surface redistribute continuity, middle participation, and residual density under changing reread constitution?
<br>
Boundary: this is not object motion, identity tracking, anomaly detection, or semantic explanation.
</div>
</div>

<script>
const data = {json.dumps(payload)};
const dial = document.getElementById("dial");
const bar = document.getElementById("bar");
const label = document.getElementById("label");
const boundaries = document.getElementById("boundaries");

function stanceName(size) {{
  if (size >= 1000) return "climate continuity";
  if (size >= 500) return "regional persistence";
  if (size >= 250) return "seam / chamber organization";
  if (size >= 100) return "local ecology";
  return "fragmentation threshold";
}}

function render() {{
  const size = data.sizes[parseInt(dial.value)];
  label.innerHTML = "window size: " + size + " — " + stanceName(size);
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

print("")
print("WROTE")
print(OUT.resolve())
print("")
