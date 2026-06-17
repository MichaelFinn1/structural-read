import csv
from pathlib import Path

ROOT = Path("comparison_packets")

terrain_file = ROOT / "traversal_comparison_surface_001" / "traversal_comparison_surface_v0.csv"
apache_file  = ROOT / "apache_comparison_basin_001" / "apache_basin_comparison_surface_v0.csv"

OUTDIR = ROOT / "master_comparative_field_001"
OUTDIR.mkdir(parents=True, exist_ok=True)

rows = []

with terrain_file.open("r", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        rows.append({
            "display_name": r["terrain"],
            "map_group": "terrain",
            "parent_family": r["terrain"],
            "avg_residual_share": r["avg_residual_share"],
            "avg_middle_share": r["avg_middle_share"],
            "avg_residual_self_adjacent": r["avg_residual_self_adjacent"],
            "avg_residual_stable_attachment": r["avg_residual_stable_attachment"],
            "dominant_posture": r["dominant_posture"],
        })

with apache_file.open("r", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        rows.append({
            "display_name": "Apache/" + r["source"],
            "map_group": "apache_sub_basin",
            "parent_family": "Apache",
            "avg_residual_share": r["avg_residual_share"],
            "avg_middle_share": r["avg_middle_share"],
            "avg_residual_self_adjacent": r["avg_residual_self_adjacent"],
            "avg_residual_stable_attachment": r["avg_residual_stable_attachment"],
            "dominant_posture": r["dominant_posture"],
        })

out = OUTDIR / "master_comparative_field_v0.csv"

fields = [
    "display_name",
    "map_group",
    "parent_family",
    "avg_residual_share",
    "avg_middle_share",
    "avg_residual_self_adjacent",
    "avg_residual_stable_attachment",
    "dominant_posture",
]

with out.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print("")
print("WROTE")
print(out.resolve())
print("ROWS", len(rows))
print("")
