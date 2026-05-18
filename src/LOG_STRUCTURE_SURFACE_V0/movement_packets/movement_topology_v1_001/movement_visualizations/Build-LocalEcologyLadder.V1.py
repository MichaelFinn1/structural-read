import csv
from pathlib import Path

SRC = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001/local_ecology_probe_windows_v1.csv")
OUT = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001/movement_visualizations/local_ecology_ladder_v1.svg")

rows = []

with SRC.open("r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

layers = [
    ("1000", "OUTER_CONTEXT", 90, 110),
    ("500",  "OPERATOR_CONTINUITY", 235, 90),
    ("250",  "LOCAL_SEAM", 355, 72),
    ("100",  "MICRO_SEAM", 455, 54),
    ("50",   "RUNNER_FRAGMENT", 535, 38),
]

width = 1600
height = 720

left = 120
right = 60

max_line = max(int(r["line_end"]) for r in rows)

def sx(v):
    return left + (int(v) / max_line) * (width - left - right)

parts = []

parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">')
parts.append('<rect width="100%" height="100%" fill="white"/>')

parts.append(f'<text x="{width/2}" y="36" text-anchor="middle" font-size="28">Local Ecology Constitution Ladder</text>')

parts.append(f'<text x="{width/2}" y="62" text-anchor="middle" font-size="13">1000 → 500 → 250 → 100 → 50</text>')

parts.append(f'<text x="{width/2}" y="84" text-anchor="middle" font-size="12">observe where continuity remains admissible vs where chamber ecology emerges</text>')

for scale, label, y, h in layers:

    parts.append(f'<text x="12" y="{y + h/2}" font-size="12">{label}</text>')
    parts.append(f'<text x="12" y="{y + h/2 + 18}" font-size="10">{scale}</text>')

    layer_rows = [r for r in rows if r["window_size"] == scale]

    for r in layer_rows:

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
            parts.append(
                f'<rect x="{x}" y="{y}" width="{stable_w}" height="{h}" fill="#f5f5f5"/>'
            )
            x += stable_w

        if middle_w > 0:
            parts.append(
                f'<rect x="{x}" y="{y}" width="{middle_w}" height="{h}" fill="#bfbfbf"/>'
            )
            x += middle_w

        if residual_w > 0:
            parts.append(
                f'<rect x="{x}" y="{y}" width="{residual_w}" height="{h}" fill="#222222"/>'
            )

        parts.append(
            f'<rect x="{x1}" y="{y}" width="{w}" height="{h}" fill="none" stroke="black" stroke-width="0.6"/>'
        )

for marker in [250,500,750,1000,1250,1500,1750]:

    x = sx(marker)

    parts.append(
        f'<line x1="{x}" y1="90" x2="{x}" y2="590" stroke="#dddddd" stroke-width="0.7"/>'
    )

    parts.append(
        f'<text x="{x}" y="620" text-anchor="middle" font-size="10">{marker}</text>'
    )

parts.append(
    f'<text x="{left}" y="675" font-size="13">Question: where does local ecology remain coherent before fragmentation collapse?</text>'
)

parts.append('</svg>')

OUT.write_text("\n".join(parts), encoding="utf-8")

print("")
print("WROTE")
print(OUT.resolve())
print("")
