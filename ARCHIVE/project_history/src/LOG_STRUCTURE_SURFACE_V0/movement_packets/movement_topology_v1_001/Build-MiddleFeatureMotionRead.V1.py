import csv
from pathlib import Path

SRC = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001/middle_feature_positions_v1.csv")
OUT = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001/middle_feature_motion_read_v1.csv")

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))

for r in rows:
    r["window_size"] = int(r["window_size"])
    r["middle_center"] = float(r["middle_center"])
    r["middle_width"] = int(r["middle_width"])
    r["middle_start"] = int(r["middle_start"])
    r["middle_end"] = int(r["middle_end"])

sizes = sorted(set(r["window_size"] for r in rows))

tracks = []
track_id = 1
prev = []

for size in sizes:
    current = [r for r in rows if r["window_size"] == size]
    current = sorted(current, key=lambda r: r["middle_center"])

    if not prev:
        for r in current:
            r["track_id"] = f"middle_track_{track_id:03d}"
            r["motion_from_previous"] = "birth_at_lowest_constitution"
            track_id += 1
    else:
        used_prev = set()

        for r in current:
            nearest = None
            nearest_dist = None

            for p in prev:
                if p["track_id"] in used_prev:
                    continue

                dist = abs(r["middle_center"] - p["middle_center"])

                if nearest is None or dist < nearest_dist:
                    nearest = p
                    nearest_dist = dist

            if nearest is not None and nearest_dist <= max(80, size * 0.9):
                r["track_id"] = nearest["track_id"]
                used_prev.add(nearest["track_id"])

                delta = r["middle_center"] - nearest["middle_center"]

                if abs(delta) < 10:
                    motion = "holds_position"
                elif delta > 0:
                    motion = "moves_right"
                else:
                    motion = "moves_left"

                width_delta = r["middle_width"] - nearest["middle_width"]

                if width_delta > 10:
                    width_motion = "widens"
                elif width_delta < -10:
                    width_motion = "thins"
                else:
                    width_motion = "similar_width"

                r["motion_from_previous"] = f"{motion};{width_motion};delta={round(delta,2)}"
            else:
                r["track_id"] = f"middle_track_{track_id:03d}"
                r["motion_from_previous"] = "new_or_merged_feature"
                track_id += 1

    tracks.extend(current)
    prev = current

fields = [
    "track_id",
    "window_size",
    "window_id",
    "middle_start",
    "middle_end",
    "middle_center",
    "middle_width",
    "middle_share",
    "motion_from_previous"
]

with OUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    for r in tracks:
        writer.writerow({k: r[k] for k in fields})

print("")
print("WROTE")
print(OUT.resolve())
print("")
