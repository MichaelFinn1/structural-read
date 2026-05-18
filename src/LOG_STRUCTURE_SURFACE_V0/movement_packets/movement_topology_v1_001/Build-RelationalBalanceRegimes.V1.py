import csv
from pathlib import Path

SRC = Path(
    "src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001/stance_relation_summary_v1.csv"
)

OUT = Path(
    "src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001/relational_balance_regimes_v1.csv"
)

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))

results = []

for r in rows:

    separation = float(r["pair_separation"])
    width_ratio = float(r["width_ratio"])

    left_center = float(r["left_center"])
    right_center = float(r["right_center"])

    midpoint = float(r["midpoint"])

    spacing_symmetry = "asymmetric"

    if separation < 75:
        spacing_symmetry = "tight"
    elif separation < 250:
        spacing_symmetry = "moderate"
    else:
        spacing_symmetry = "wide"

    width_symmetry = "balanced"

    if width_ratio >= 1.5:
        width_symmetry = "asymmetric"

    centerline_relation = "off_center"

    if midpoint >= 750 and midpoint <= 1250:
        centerline_relation = "null_spanning"

    carrier_relation = "local_feature"

    if (
        float(r["left_width"]) >= 150
        and left_center < 250
    ):
        carrier_relation = "persistent_carrier_candidate"

    results.append({
        "window_size": r["window_size"],
        "left_center": left_center,
        "right_center": right_center,
        "pair_separation": separation,
        "width_symmetry": width_symmetry,
        "spacing_symmetry": spacing_symmetry,
        "centerline_relation": centerline_relation,
        "carrier_relation": carrier_relation
    })

fields = list(results[0].keys())

with OUT.open("w", newline="", encoding="utf-8") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fields
    )

    writer.writeheader()

    for r in results:
        writer.writerow(r)

print("")
print("WROTE")
print(OUT.resolve())
print("")
