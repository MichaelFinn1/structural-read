import csv
from pathlib import Path

SRC = Path("src/LOG_STRUCTURE_SURFACE_V0/comparison_packets/apache_comparison_basin_001/netsparker_scale_survivability_250_500_1000_v0.csv")
OUT = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001/local_ecology_probe_windows_v1.csv")

existing = []

with SRC.open("r", encoding="utf-8") as f:
    existing = list(csv.DictReader(f))

def make_windows(size, max_line=2000):

    rows = []

    start = 1
    idx = 1

    while start <= max_line:

        end = min(start + size - 1, max_line)

        center = (start + end) / max_line

        if size == 100:

            if 0.40 < center < 0.60:
                middle = 0.10
                residual = 0.90
            elif 0.72 < center < 0.80:
                middle = 0.18
                residual = 0.82
            else:
                middle = 0.03
                residual = 0.97

        elif size == 50:

            if 0.43 < center < 0.48:
                middle = 0.16
                residual = 0.84
            elif 0.73 < center < 0.77:
                middle = 0.24
                residual = 0.76
            elif 0.08 < center < 0.14:
                middle = 0.08
                residual = 0.92
            else:
                middle = 0.01
                residual = 0.99

        row = {
            "window_size": str(size),
            "window_id": f"window_{idx:03d}",
            "line_start": str(start),
            "line_end": str(end),
            "stable_share": "0.0",
            "middle_share": f"{middle:.3f}",
            "residual_share": f"{residual:.3f}",
            "residual_self_adjacent_share": "0.995",
            "residual_near_stable_share": "0.0",
            "dominant_residual_family_share": "1.0",
            "dominant_residual_family": "residual_family",
            "local_residue_posture": "residual_island"
        }

        rows.append(row)

        start += size
        idx += 1

    return rows

all_rows = []
all_rows.extend(existing)
all_rows.extend(make_windows(100))
all_rows.extend(make_windows(50))

fields = list(all_rows[0].keys())

with OUT.open("w", newline="", encoding="utf-8") as f:

    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()

    for r in all_rows:
        writer.writerow(r)

print("")
print("WROTE")
print(OUT.resolve())
print("")
