import csv
from pathlib import Path

ROOT = Path("comparison_packets/master_comparative_field_001")
src = ROOT / "master_comparative_field_v0.csv"

with src.open("r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

width = 1500
height = 950
left = 130
right = 170
top = 90
bottom = 110

xs = [float(r["avg_residual_share"]) for r in rows]
ys = [float(r["avg_residual_stable_attachment"]) for r in rows]

xmax = max(xs) * 1.12
ymax = max(ys) * 1.12

def sx(x):
    return left + (x / xmax) * (width - left - right)

def sy(y):
    return height - bottom - (y / ymax) * (height - top - bottom)

parts = []
parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">')
parts.append('<rect width="100%" height="100%" fill="white"/>')

parts.append(f'<text x="{width/2}" y="38" text-anchor="middle" font-size="28">Master Comparative Field V0</text>')
parts.append(f'<text x="{width/2}" y="64" text-anchor="middle" font-size="14">white=terrain | gray=Apache sub-basin | x=residual share | y=stable attachment | size=middle share | ring=self-adjacency</text>')

parts.append(f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="black"/>')
parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="black"/>')

parts.append(f'<text x="{width/2}" y="{height-45}" text-anchor="middle" font-size="18">Residual Share</text>')
parts.append(f'<text x="38" y="{height/2}" text-anchor="middle" font-size="18" transform="rotate(-90 38 {height/2})">Residual Stable Attachment</text>')

for row in rows:
    x = sx(float(row["avg_residual_share"]))
    y = sy(float(row["avg_residual_stable_attachment"]))
    middle = float(row["avg_middle_share"])
    self_adj = float(row["avg_residual_self_adjacent"])

    radius = 8 + (middle * 120)
    ring = 1 + (self_adj * 10)

    if row["map_group"] == "apache_sub_basin":
        fill = "#d9d9d9"
        dash = ' stroke-dasharray="6 4"'
    else:
        fill = "white"
        dash = ""

    name = row["display_name"]

    parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" fill="{fill}" stroke="black" stroke-width="{ring:.1f}"{dash}/>')
    parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="black"/>')
    parts.append(f'<text x="{x + radius + 8:.1f}" y="{y + 4:.1f}" font-size="13">{name}</text>')

parts.append('</svg>')

out = ROOT / "master_comparative_field_v0.svg"
out.write_text("\n".join(parts), encoding="utf-8")

print("")
print("WROTE")
print(out.resolve())
print("ROWS", len(rows))
print("")
