import csv
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/naturalistic_calibration_002")
MEASURED = BASE / "measured_hierarchical_burst_structural_v2_dense_v1"
SRC = MEASURED / "traversal_windows_v0.csv"
OUT = MEASURED / "meso_deformation_sections_v1.csv"

TARGET_WINDOWS = [125, 150, 175, 200, 250, 300, 350, 400, 500, 1000]
SECTION_COUNT = 4

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))

for r in rows:
    for k in ["window_size","line_start","line_end","stable_share","middle_share","residual_share"]:
        r[k] = float(r[k])

max_line = max(int(r["line_end"]) for r in rows)

def section_for(line_start, line_end):
    mid = (line_start + line_end) / 2
    section_width = max_line / SECTION_COUNT
    idx = int((mid - 1) // section_width) + 1
    if idx < 1:
        idx = 1
    if idx > SECTION_COUNT:
        idx = SECTION_COUNT
    return idx

def posture(stable, middle, residual):
    if residual >= 0.50:
        return "residual_dominant"
    if stable >= 0.85:
        return "stable_enclosed"
    if residual >= 0.20:
        return "residual_pressure"
    if middle >= 0.15:
        return "middle_visible"
    return "mixed_low_pressure"

out_rows = []

for ws in TARGET_WINDOWS:
    selected = [r for r in rows if int(r["window_size"]) == ws]
    if not selected:
        continue

    buckets = {i: [] for i in range(1, SECTION_COUNT + 1)}

    for r in selected:
        s = section_for(int(r["line_start"]), int(r["line_end"]))
        buckets[s].append(r)

    for section_id, bucket in buckets.items():
        if not bucket:
            continue

        stable = sum(float(r["stable_share"]) for r in bucket) / len(bucket)
        middle = sum(float(r["middle_share"]) for r in bucket) / len(bucket)
        residual = sum(float(r["residual_share"]) for r in bucket) / len(bucket)

        out_rows.append({
            "terrain": "hierarchical_burst_structural_v2",
            "window_size": ws,
            "section": f"Q{section_id}",
            "line_start": min(int(r["line_start"]) for r in bucket),
            "line_end": max(int(r["line_end"]) for r in bucket),
            "windows_in_section": len(bucket),
            "stable_share_avg": round(stable, 4),
            "middle_share_avg": round(middle, 4),
            "residual_share_avg": round(residual, 4),
            "dominant_posture": posture(stable, middle, residual),
        })

fieldnames = [
    "terrain",
    "window_size",
    "section",
    "line_start",
    "line_end",
    "windows_in_section",
    "stable_share_avg",
    "middle_share_avg",
    "residual_share_avg",
    "dominant_posture",
]

with OUT.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(out_rows)

print("WROTE", OUT.resolve())
