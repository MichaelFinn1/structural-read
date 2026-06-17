import csv
from pathlib import Path

SRC = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001/middle_feature_positions_v1.csv")
OUT = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001/stance_relation_summary_v1.csv")

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))

for r in rows:
    r["window_size"] = int(r["window_size"])
    r["middle_center"] = float(r["middle_center"])
    r["middle_width"] = int(r["middle_width"])

sizes = sorted(set(r["window_size"] for r in rows))

results = []

for size in sizes:

    current = [r for r in rows if r["window_size"] == size]
    current = sorted(current, key=lambda r: r["middle_center"])

    if len(current) < 2:
        continue

    for i in range(len(current) - 1):

        a = current[i]
        b = current[i + 1]

        separation = round(
            b["middle_center"] - a["middle_center"],
            2
        )

        width_ratio = round(
            max(a["middle_width"], b["middle_width"]) /
            max(1, min(a["middle_width"], b["middle_width"])),
            3
        )

        if separation < 80:
            relation = "tight_pair"
        elif separation < 250:
            relation = "moderate_pair"
        else:
            relation = "wide_pair"

        if width_ratio < 1.25:
            balance = "balanced"
        elif a["middle_width"] > b["middle_width"]:
            balance = "left_dominant"
        else:
            balance = "right_dominant"

        midpoint = round(
            (a["middle_center"] + b["middle_center"]) / 2,
            2
        )

        if midpoint >= 750 and midpoint <= 1250:
            hollow_relation = "circles_null_zone"
        else:
            hollow_relation = "outside_null_zone"

        results.append({
            "window_size": size,
            "left_center": a["middle_center"],
            "right_center": b["middle_center"],
            "left_width": a["middle_width"],
            "right_width": b["middle_width"],
            "pair_separation": separation,
            "width_ratio": width_ratio,
            "pair_relation": relation,
            "balance_relation": balance,
            "midpoint": midpoint,
            "null_zone_relation": hollow_relation
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
