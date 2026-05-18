import csv
from pathlib import Path

SRC = Path("src/LOG_STRUCTURE_SURFACE_V0/comparison_packets/apache_comparison_basin_001/netsparker_scale_survivability_250_500_1000_v0.csv")
OUT = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001/movement_visualizations/constitution_transition_1000_500_250_v1.svg")

rows = []
with SRC.open("r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

width = 1500
height = 640
left = 100
right = 70
top = 90

layers = [
    {"scale": "1000", "label": "OUTER_CONTEXT", "y": 95, "h": 115},
    {"scale": "500",  "label": "OPERATOR_CONTINUITY", "y": 255, "h": 95},
    {"scale": "250",  "label": "LOCAL_SEAM", "y": 390, "h": 70},
]

max_line = max(int(r["line_end"]) for r in rows)

def sx(v):
    return left + (int(v) / max_line) * (width - left - right)

def rect(parts, x, y, w, h, fill, label=None):
    parts.append(
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'fill="{fill}" stroke="black" stroke-width="0.6"/>'
    )
    if label and w > 40:
        parts.append(
            f'<text x="{x + w/2:.1f}" y="{y + h/2 + 4:.1f}" '
            f'text-anchor="middle" font-size="10">{label}</text>'
        )

parts = []
parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">')
parts.append('<rect width="100%" height="100%" fill="white"/>')

parts.append(f'<text x="{width/2}" y="34" text-anchor="middle" font-size="25">Constitution Transition Read V1</text>')
parts.append(f'<text x="{width/2}" y="58" text-anchor="middle" font-size="13">Netsparker: 1000 background → 500 operator continuity → 250 local seam</text>')
parts.append(f'<text x="{width/2}" y="76" text-anchor="middle" font-size="12">white=stable | grey=middle | black=residual | outlined blocks=window boundaries</text>')

for layer in layers:
    scale = layer["scale"]
    label = layer["label"]
    y = layer["y"]
    h = layer["h"]

    parts.append(f'<text x="20" y="{y + h/2 + 5}" font-size="13">{label}</text>')
    parts.append(f'<text x="20" y="{y + h/2 + 22}" font-size="11">{scale}</text>')

    scale_rows = [r for r in rows if r["window_size"] == scale]

    for r in scale_rows:
        x1 = sx(r["line_start"])
        x2 = sx(r["line_end"])
        w = x2 - x1

        stable = float(r["stable_share"])
        middle = float(r["middle_share"])
        residual = float(r["residual_share"])

        x = x1

        stable_w = w * stable
        middle_w = w * middle
        residual_w = w * residual

        if stable_w > 0:
            rect(parts, x, y, stable_w, h, "#f2f2f2", "stable")
            x += stable_w

        if middle_w > 0:
            rect(parts, x, y, middle_w, h, "#bdbdbd", "middle")
            x += middle_w

        if residual_w > 0:
            rect(parts, x, y, residual_w, h, "#222222", None)

        parts.append(
            f'<rect x="{x1:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="none" stroke="black" stroke-width="1.1"/>'
        )

for mark in [250, 500, 750, 1000, 1250, 1500, 1750]:
    x = sx(mark)
    parts.append(f'<line x1="{x:.1f}" y1="88" x2="{x:.1f}" y2="480" stroke="#dddddd" stroke-width="0.7"/>')
    parts.append(f'<text x="{x:.1f}" y="500" text-anchor="middle" font-size="10">{mark}</text>')

parts.append(f'<line x1="{left}" y1="520" x2="{width-right}" y2="520" stroke="black"/>')
parts.append(f'<text x="{left}" y="545" font-size="12">line 1</text>')
parts.append(f'<text x="{width-right}" y="545" text-anchor="end" font-size="12">line {max_line}</text>')

parts.append(f'<text x="{left}" y="590" font-size="13">Read question: which broad continuity objects become local seam or boundary objects under constitution transition?</text>')

parts.append('</svg>')

OUT.write_text("\n".join(parts), encoding="utf-8")

print("")
print("WROTE")
print(OUT.resolve())
print("")
