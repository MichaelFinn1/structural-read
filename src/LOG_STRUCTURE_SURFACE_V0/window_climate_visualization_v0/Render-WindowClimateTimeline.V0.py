import csv
from pathlib import Path

FILES = [
    ("250", "WINDOW_CLIMATE_SEQUENCE_250.csv"),
    ("500", "WINDOW_CLIMATE_SEQUENCE_500.csv"),
    ("1000", "WINDOW_CLIMATE_SEQUENCE_1000.csv"),
]

SERIES = [
    ("enclosure_share", "enclosure"),
    ("edge_share", "edge"),
    ("middle_share", "middle"),
    ("residual_share", "residual"),
    ("diversity_share", "diversity"),
]

def load_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def polyline(rows, key, width, height, pad):
    pts = []
    n = len(rows)
    if n <= 1:
        return ""
    for i, r in enumerate(rows):
        x = pad + (i / (n - 1)) * (width - pad * 2)
        y = pad + (1 - float(r[key])) * (height - pad * 2)
        pts.append(f"{x:.2f},{y:.2f}")
    return " ".join(pts)

sections = []

for label, path in FILES:
    rows = load_rows(path)

    width = 1400
    height = 360
    pad = 36

    lines = []
    for key, name in SERIES:
        pts = polyline(rows, key, width, height, pad)
        lines.append(f"<polyline class='{key}' points='{pts}' />")

    spans = []
    for i, r in enumerate(rows):
        if r.get("local_topology") == "localized_inversion_basin":
            n = len(rows)
            x = pad + (i / max(1, n - 1)) * (width - pad * 2)
            spans.append(
                f"<rect class='pulse' x='{x-5:.2f}' y='{pad}' width='10' height='{height-pad*2}' />"
            )

    rows_html = []
    for r in rows:
        if r.get("local_topology") == "localized_inversion_basin":
            rows_html.append(
                "<tr class='pulse-row'>"
                f"<td>{r['window_size']}</td>"
                f"<td>{r['window_index']}</td>"
                f"<td>{r['line_start']}</td>"
                f"<td>{r['line_end']}</td>"
                f"<td>{r['climate']}</td>"
                f"<td>{r['enclosure_share']}</td>"
                f"<td>{r['edge_share']}</td>"
                f"<td>{r['middle_share']}</td>"
                f"<td>{r['diversity_share']}</td>"
                f"<td>{r['edge_margin']}</td>"
                f"<td>{r['local_topology']}</td>"
                "</tr>"
            )

    sections.append(f"""
<section>
<h2>Window size {label}</h2>

<svg viewBox='0 0 {width} {height}' class='chart'>
  <rect class='bg' x='0' y='0' width='{width}' height='{height}' />
  <line class='axis' x1='{pad}' y1='{height-pad}' x2='{width-pad}' y2='{height-pad}' />
  <line class='axis' x1='{pad}' y1='{pad}' x2='{pad}' y2='{height-pad}' />
  {''.join(spans)}
  {''.join(lines)}
</svg>

<div class='legend'>
  <span class='enclosure_share'>enclosure</span>
  <span class='edge_share'>edge</span>
  <span class='middle_share'>middle</span>
  <span class='residual_share'>residual</span>
  <span class='diversity_share'>diversity</span>
  <span class='pulse-label'>localized inversion basin</span>
</div>

<table>
<tr>
<th>window size</th><th>window</th><th>line start</th><th>line end</th>
<th>climate</th><th>enclosure</th><th>edge</th><th>middle</th>
<th>diversity</th><th>edge margin</th><th>topology</th>
</tr>
{''.join(rows_html)}
</table>
</section>
""")

html = f"""
<html>
<head>
<meta charset='utf-8'>
<title>Window Climate Timelines V0</title>
<style>
body {{
  background:#0b0f14;
  color:#eee;
  font-family:Segoe UI, Arial;
  padding:28px;
}}
.card {{
  max-width:1500px;
  margin:auto;
  background:#111820;
  border:1px solid #2c3945;
  border-radius:14px;
  padding:24px;
}}
.note {{
  color:#aaa;
  line-height:1.7;
  margin-bottom:24px;
}}
section {{
  margin-top:34px;
}}
.chart {{
  width:100%;
  height:360px;
  border:1px solid #2c3945;
  border-radius:12px;
  background:#0d1319;
}}
.bg {{
  fill:#0d1319;
}}
.axis {{
  stroke:#44515f;
  stroke-width:1;
}}
polyline {{
  fill:none;
  stroke-width:2.2;
}}
.enclosure_share {{
  stroke:#8fd8f4;
  color:#8fd8f4;
}}
.edge_share {{
  stroke:#ff9f7a;
  color:#ff9f7a;
}}
.middle_share {{
  stroke:#b7e36d;
  color:#b7e36d;
}}
.residual_share {{
  stroke:#e55934;
  color:#e55934;
}}
.diversity_share {{
  stroke:#c48fff;
  color:#c48fff;
}}
.pulse {{
  fill:#c48fff;
  opacity:.18;
}}
.legend {{
  margin-top:10px;
  display:flex;
  gap:18px;
  flex-wrap:wrap;
  color:#aaa;
}}
.pulse-label {{
  color:#d7b7ff;
}}
table {{
  width:100%;
  border-collapse:collapse;
  margin-top:18px;
  font-size:12px;
}}
th {{
  color:#aaa;
  text-align:left;
  border-bottom:1px solid #444;
  padding:7px;
}}
td {{
  border-bottom:1px solid #27313a;
  padding:7px;
}}
.pulse-row {{
  background:rgba(196,143,255,.12);
}}
.boundary {{
  color:#999;
  border-top:1px solid #2c3945;
  margin-top:30px;
  padding-top:18px;
  line-height:1.7;
}}
</style>
</head>
<body>
<div class='card'>
<h1>Window Climate Timelines V0</h1>

<div class='note'>
Observer-only visual comparison across window sizes.
Visualizes climate shifts, not trajectories.
Compare by source-line region, not matching window numbers.
</div>

{''.join(sections)}

<div class='boundary'>
Boundary: These timelines show emitted participation geometry across bounded windows.
They do not infer object movement, lifecycle, causality, anomaly, or hidden system state.
<br><br>
One-line hold: Compare reslicing survival by source-line region, not by matching window labels.
</div>

</div>
</body>
</html>
"""

out = Path("WINDOW_CLIMATE_TIMELINES_V0.html")
out.write_text(html, encoding="utf-8")

print("")
print("=== WINDOW CLIMATE TIMELINES COMPLETE ===")
print(out.resolve())
