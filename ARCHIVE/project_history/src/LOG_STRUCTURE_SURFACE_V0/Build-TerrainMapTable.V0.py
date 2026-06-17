import csv
from pathlib import Path

ROOT = Path("comparison_packets/traversal_comparison_surface_001")
OUT = Path("comparison_packets/terrain_map_reread_v0")
OUT.mkdir(exist_ok=True)

src = ROOT / "traversal_comparison_surface_v0.csv"

with src.open("r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

rows.sort(key=lambda r: float(r["avg_residual_share"]))

cols = [
    "terrain",
    "avg_residual_share",
    "avg_middle_share",
    "avg_residual_self_adjacent",
    "avg_residual_stable_attachment",
    "dominant_posture"
]

out = OUT / "terrain_map_table_v0.csv"

with out.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=cols)
    writer.writeheader()
    writer.writerows([{k: r[k] for k in cols} for r in rows])

print("")
print("WROTE")
print(out.resolve())
print("")
