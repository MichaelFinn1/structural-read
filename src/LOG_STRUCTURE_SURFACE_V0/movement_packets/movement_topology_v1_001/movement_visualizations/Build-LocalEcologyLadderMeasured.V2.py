import csv
from pathlib import Path

SRC = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001/measured_netsparker_windows_v2/traversal_windows_v0.csv")
OUT = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001/movement_visualizations/local_ecology_ladder_measured_v2.svg")

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))

layers = [
    ("1000", "OUTER_CONTEXT", 90, 105),
    ("500", "OPERATOR_CONTINUITY", 225, 85),
    ("250", "LOCAL_SEAM", 340, 65),
    ("100", "MICRO_SEAM", 435, 48),
    ("50", "RUNNER_FRAGMENT", 510, 34),
]

width = 1600
height = 680
left = 140
right = 70
max_line = max(int(r["line_end"]) for r in rows)

def sx(v):
    return left + (int(v) / max_line) * (width - left - right)

parts = []
parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">')
parts.append('<rect width="100%" height="100%" fill="white"/>')
parts.append(f'<text x="{width/2}" y="34" text-anchor="middle" font-size="26">Measured Local Ecology Ladder V2</text>')
parts.append(f'<text x="{width/2}" y="58" text-anchor="middle" font-size="13">No synthetic rows | no guide lines | white=stable | grey=middle | black=residual</text>')

for scale, label, y, h in layers:
    parts.append(f'<text x="12" y="{y + h/2 - 4}" font-size="12">{label}</text>')
    parts.append(f'<text x="12" y="{y + h/2 + 14}" font-size="10">{scale}</text>')

    layer_rows = [r for r in rows if r["window_size"] == scale]

    for r in layer_rows:
        x1 = sx(r["line_start"])
        x2 = sx(r["line_end"])
        w = x2 - x1

        stable = float(r["stable_share"])
        middle = float(r["middle_share"])
        residual = float(r["residual_share"])

        x = x1

        sw = w * stable
        mw = w * middle
        rw = w * residual

        if sw > 0:
            parts.append(f'<rect x="{x:.1f}" y="{y}" width="{sw:.1f}" height="{h}" fill="#f5f5f5"/>')
            x += sw

        if mw > 0:
            parts.append(f'<rect x="{x:.1f}" y="{y}" width="{mw:.1f}" height="{h}" fill="#bfbfbf"/>')
            x += mw

        if rw > 0:
            parts.append(f'<rect x="{x:.1f}" y="{y}" width="{rw:.1f}" height="{h}" fill="#222222"/>')

        parts.append(f'<rect x="{x1:.1f}" y="{y}" width="{w:.1f}" height="{h}" fill="none" stroke="black" stroke-width="0.5"/>')

parts.append(f'<line x1="{left}" y1="580" x2="{width-right}" y2="580" stroke="black"/>')
parts.append(f'<text x="{left}" y="605" font-size="12">line 1</text>')
parts.append(f'<text x="{width-right}" y="605" text-anchor="end" font-size="12">line {max_line}</text>')
parts.append(f'<text x="{left}" y="645" font-size="13">Read question: which local ecology remains coherent before fragmentation collapse?</text>')
parts.append('</svg>')

OUT.write_text("\n".join(parts), encoding="utf-8")

print("")
print("WROTE")
print(OUT.resolve())
print("")
