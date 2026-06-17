import csv
from pathlib import Path

SRC = Path("src/LOG_STRUCTURE_SURFACE_V0/comparison_packets/apache_comparison_basin_001/netsparker_scale_survivability_250_500_1000_v0.csv")
OUT = Path("src/LOG_STRUCTURE_SURFACE_V0/product_packets/operator_workbench_v1_001/netsparker_layered_window_read_v0.svg")

rows = []
with SRC.open("r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

width = 1400
height = 520
left = 80
right = 50
top = 70

layers = [
    ("1000", 90, 90),
    ("500", 220, 70),
    ("250", 330, 52),
]

max_line = max(int(r["line_end"]) for r in rows)

def sx(v):
    return left + (int(v) / max_line) * (width - left - right)

parts = []
parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">')
parts.append('<rect width="100%" height="100%" fill="white"/>')
parts.append(f'<text x="{width/2}" y="32" text-anchor="middle" font-size="24">Netsparker Layered Window Read V0</text>')
parts.append(f'<text x="{width/2}" y="55" text-anchor="middle" font-size="13">1000 background | 500 middle | 250 foreground | residual = dark | middle = light | stable = pale</text>')

for scale, y, h in layers:
    parts.append(f'<text x="20" y="{y + h/2 + 5}" font-size="16">{scale}</text>')
    scale_rows = [r for r in rows if r["window_size"] == scale]

    for r in scale_rows:
        x1 = sx(r["line_start"])
        x2 = sx(r["line_end"])
        w = x2 - x1

        stable = float(r["stable_share"])
        middle = float(r["middle_share"])
        residual = float(r["residual_share"])

        stable_w = w * stable
        middle_w = w * middle
        residual_w = w * residual

        x = x1

        if stable_w > 0:
            parts.append(f'<rect x="{x:.1f}" y="{y}" width="{stable_w:.1f}" height="{h}" fill="#eeeeee" stroke="black" stroke-width="0.5"/>')
            x += stable_w

        if middle_w > 0:
            parts.append(f'<rect x="{x:.1f}" y="{y}" width="{middle_w:.1f}" height="{h}" fill="#bbbbbb" stroke="black" stroke-width="0.5"/>')
            x += middle_w

        if residual_w > 0:
            parts.append(f'<rect x="{x:.1f}" y="{y}" width="{residual_w:.1f}" height="{h}" fill="#444444" stroke="black" stroke-width="0.5"/>')

        parts.append(f'<rect x="{x1:.1f}" y="{y}" width="{w:.1f}" height="{h}" fill="none" stroke="black" stroke-width="1"/>')

parts.append(f'<line x1="{left}" y1="430" x2="{width-right}" y2="430" stroke="black"/>')
parts.append(f'<text x="{left}" y="455" font-size="12">line 1</text>')
parts.append(f'<text x="{width-right}" y="455" text-anchor="end" font-size="12">line {max_line}</text>')

parts.append('</svg>')

OUT.write_text("\n".join(parts), encoding="utf-8")

print("")
print("WROTE")
print(OUT.resolve())
print("")
