import csv
from pathlib import Path

ROOT = Path("comparison_packets")

SRC = (
    ROOT
    / "traversal_comparison_surface_001"
    / "openstack_traversal_windows_v0.csv"
)

OUT = (
    ROOT
    / "master_comparative_field_001"
    / "openstack_scale_survivability_250_500_1000_v0.csv"
)

wanted = {"250", "500", "1000"}

with SRC.open("r", encoding="utf-8") as f:
    rows = [
        r for r in csv.DictReader(f)
        if r["window_size"] in wanted
    ]

fields = [
    "window_size",
    "window_id",
    "line_start",
    "line_end",
    "stable_share",
    "middle_share",
    "residual_share",
    "residual_self_adjacent_share",
    "residual_near_stable_share",
    "dominant_residual_family_share",
    "dominant_residual_family",
    "local_residue_posture",
]

with OUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()

    for r in rows:
        writer.writerow({k: r[k] for k in fields})

print("")
print("WROTE")
print(OUT.resolve())
print("ROWS", len(rows))
print("")
