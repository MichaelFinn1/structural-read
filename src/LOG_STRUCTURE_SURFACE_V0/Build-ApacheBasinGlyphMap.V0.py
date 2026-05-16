import csv
from pathlib import Path

ROOT = Path("comparison_packets/apache_comparison_basin_001")
OUT = ROOT

src = ROOT / "apache_basin_comparison_surface_v0.csv"

with src.open("r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

width = 980
height = 680
left = 95
right = 70
top = 70
bottom = 90

xs = [float(r["avg_residual_share"]) for r in rows]
ys = [float(r["avg_residual_stable_attachment"]) for r in rows]

xmax = max(xs) * 1.12 if max(xs) > 0 else 1.0
ymax = max(ys) * 1.12 if max(ys) > 0 else 1.0

def sx(x):
    return left + (x / xmax) * (width - left - right)

def sy(y):
    return height - bottom - (y / ymax) * (height - top - bottom)

parts = []
parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">')
parts.append('<rect width="100%" height="100%" fill="white"/>')
parts.append(f'<text x="{width/2}" y="32" text-anchor="middle" font-size="22">Apache Comparison Basin 001</text>')
parts.append(f'<text x="{width/2}" y="55" text-anchor="middle" font-size="13">x=residual share | y=stable attachment | size=middle share | ring=residual self-adjacency</text>')
parts.append(f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="black"/>')
parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="black"/>')
parts.append(f'<text x="{width/2}" y="{height-35}" text-anchor="middle" font-size="15">Residual Share</text>')
parts.append(f'<text x="28" y="{height/2}" text-anchor="middle" font-size="15" transform="rotate(-90 28 {height/2})">Residual Stable Attachment</text>')

for r in rows:
    name = r["source"]
    x = sx(float(r["avg_residual_share"]))
    y = sy(float(r["avg_residual_stable_attachment"]))
    middle = float(r["avg_middle_share"])
    self_adj = float(r["avg_residual_self_adjacent"])

    radius = 8 + (middle * 90)
    stroke_width = 1 + (self_adj * 8)

    parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" fill="white" stroke="black" stroke-width="{stroke_width:.1f}"/>')
    parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="black"/>')
    parts.append(f'<text x="{x + radius + 8:.1f}" y="{y + 4:.1f}" font-size="13">{name}</text>')

parts.append('</svg>')

out = OUT / "apache_basin_glyph_map_v0.svg"
out.write_text("\n".join(parts), encoding="utf-8")

print("")
print("WROTE")
print(out.resolve())
print("")
