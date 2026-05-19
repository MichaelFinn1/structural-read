import csv, json
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/naturalistic_calibration_001")
VIZ = BASE / "visualizations_v2"
VIZ.mkdir(parents=True, exist_ok=True)

for folder in BASE.glob("measured_*_window_dial_dense_v2"):
    terrain = folder.name.replace("measured_", "").replace("_window_dial_dense_v2", "")
    src = folder / "traversal_windows_v0.csv"
    out = VIZ / f"local_ecology_window_dial_{terrain}_dense_v2.html"

    rows = list(csv.DictReader(src.open("r", encoding="utf-8")))

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
<title>{terrain} Dense V2</title>
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
.legend {{ text-align: center; margin-top: 25px; font-size: 16px; }}
.note {{ margin-top: 25px; font-size: 16px; }}
</style>
</head>
<body>
<div id="wrap">
<h1>{terrain} Local Ecology Window Dial Dense V2</h1>
<div id="label"></div>
<input id="dial" type="range" min="0" max="{len(sizes)-1}" value="0" step="1">
<div id="bar" class="bar"></div>
<div class="legend">white = stable | grey = middle | black = residual</div>
<div class="note">Calibration V2: terrains vary emitted recurrence structure, not only scalar values.</div>
</div>
<script>
const data = {json.dumps(payload)};
const dial = document.getElementById("dial");
const bar = document.getElementById("bar");
const label = document.getElementById("label");

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
  }});
}}
dial.addEventListener("input", render);
render();
</script>
</body>
</html>
"""
    out.write_text(html, encoding="utf-8")
    print("WROTE", out.resolve())
