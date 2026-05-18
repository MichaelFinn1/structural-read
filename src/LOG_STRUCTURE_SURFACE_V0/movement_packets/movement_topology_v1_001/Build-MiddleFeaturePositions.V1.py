import csv
from pathlib import Path

SRC = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001/measured_netsparker_window_dial_v1/traversal_windows_v0.csv")
OUT = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001/middle_feature_positions_v1.csv")

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))
features = []

for r in rows:
    size = int(r["window_size"])
    start = int(r["line_start"])
    end = int(r["line_end"])
    width = end - start + 1

    stable = float(r["stable_share"])
    middle = float(r["middle_share"])

    if middle <= 0:
        continue

    middle_start = start + int(round(width * stable))
    middle_width = max(1, int(round(width * middle)))
    middle_end = min(end, middle_start + middle_width - 1)
    center = (middle_start + middle_end) / 2.0

    features.append({
        "window_size": size,
        "window_id": r["window_id"],
        "line_start": start,
        "line_end": end,
        "middle_start": middle_start,
        "middle_end": middle_end,
        "middle_center": round(center, 2),
        "middle_width": middle_width,
        "middle_share": middle
    })

features.sort(key=lambda x: (x["window_size"], x["middle_center"]))

with OUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(features[0].keys()))
    writer.writeheader()
    writer.writerows(features)

print("WROTE")
print(OUT.resolve())
