import csv
from pathlib import Path

ROOT = Path("comparison_packets/traversal_comparison_surface_001")
OUT = Path("comparison_packets/terrain_map_reread_v0")
OUT.mkdir(exist_ok=True)

def read_rows():
    with (ROOT / "traversal_comparison_surface_v0.csv").open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def svg_scatter(rows, xkey, ykey, title, xlabel, ylabel, outfile):
    width = 900
    height = 620
    left = 90
    right = 40
    top = 60
    bottom = 80

    xs = [float(r[xkey]) for r in rows]
    ys = [float(r[ykey]) for r in rows]

    xmin, xmax = 0.0, max(xs) * 1.12 if max(xs) > 0 else 1.0
    ymin, ymax = 0.0, max(ys) * 1.12 if max(ys) > 0 else 1.0

    def sx(x):
        return left + ((x - xmin) / (xmax - xmin)) * (width - left - right)

    def sy(y):
        return height - bottom - ((y - ymin) / (ymax - ymin)) * (height - top - bottom)

    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">')
    parts.append('<rect width="100%" height="100%" fill="white"/>')
    parts.append(f'<text x="{width/2}" y="30" text-anchor="middle" font-size="20">{title}</text>')
    parts.append(f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="black"/>')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="black"/>')
    parts.append(f'<text x="{width/2}" y="{height-25}" text-anchor="middle" font-size="14">{xlabel}</text>')
    parts.append(f'<text x="25" y="{height/2}" text-anchor="middle" font-size="14" transform="rotate(-90 25 {height/2})">{ylabel}</text>')

    for r in rows:
        x = sx(float(r[xkey]))
        y = sy(float(r[ykey]))
        name = r["terrain"]
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="black"/>')
        parts.append(f'<text x="{x+8:.1f}" y="{y-8:.1f}" font-size="13">{name}</text>')

    parts.append('</svg>')

    out = OUT / outfile
    out.write_text("\n".join(parts), encoding="utf-8")
    print("WROTE")
    print(out.resolve())

rows = read_rows()

svg_scatter(
    rows,
    "avg_residual_share",
    "avg_residual_stable_attachment",
    "Six-Terrain Field: Residual Share vs Stable Attachment",
    "Residual Share",
    "Residual Stable Attachment",
    "terrain_field_residual_attachment_v0.svg"
)

svg_scatter(
    rows,
    "avg_middle_share",
    "avg_residual_self_adjacent",
    "Six-Terrain Field: Middle Share vs Residual Continuity",
    "Middle Share",
    "Residual Self-Adjacency",
    "terrain_field_middle_continuity_v0.svg"
)
