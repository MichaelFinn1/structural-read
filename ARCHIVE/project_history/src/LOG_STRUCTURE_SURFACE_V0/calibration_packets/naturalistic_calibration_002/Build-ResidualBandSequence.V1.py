import csv
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/naturalistic_calibration_002")
MEASURED = BASE / "measured_hierarchical_burst_structural_v2_dense_v1"
SRC = MEASURED / "traversal_windows_v0.csv"
OUT = MEASURED / "residual_band_sequence_v1.csv"

TARGET_WINDOWS = [125, 150, 175, 200, 250, 300, 350, 400, 500, 1000]
RESIDUAL_THRESHOLD = 0.10
MAX_JOIN_GAP = 1

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))

for r in rows:
    r["window_size"] = int(float(r["window_size"]))
    r["line_start"] = int(float(r["line_start"]))
    r["line_end"] = int(float(r["line_end"]))
    r["stable_share"] = float(r["stable_share"])
    r["middle_share"] = float(r["middle_share"])
    r["residual_share"] = float(r["residual_share"])

max_line = max(r["line_end"] for r in rows)
section_width = max_line / 4

def section_for(mid):
    s = int((mid - 1) // section_width) + 1
    if s < 1:
        s = 1
    if s > 4:
        s = 4
    return f"Q{s}"

out_rows = []

for ws in TARGET_WINDOWS:
    selected = [r for r in rows if r["window_size"] == ws]
    selected.sort(key=lambda r: r["line_start"])

    active = [r for r in selected if r["residual_share"] >= RESIDUAL_THRESHOLD]

    bands = []
    current = None

    for r in active:
        if current is None:
            current = {
                "start": r["line_start"],
                "end": r["line_end"],
                "rows": [r],
            }
            continue

        gap = r["line_start"] - current["end"] - 1

        if gap <= MAX_JOIN_GAP:
            current["end"] = r["line_end"]
            current["rows"].append(r)
        else:
            bands.append(current)
            current = {
                "start": r["line_start"],
                "end": r["line_end"],
                "rows": [r],
            }

    if current is not None:
        bands.append(current)

    prev_end = None

    for idx, b in enumerate(bands, start=1):
        width = b["end"] - b["start"] + 1
        mid = (b["start"] + b["end"]) / 2
        gap = "" if prev_end is None else b["start"] - prev_end - 1
        avg_residual = sum(r["residual_share"] for r in b["rows"]) / len(b["rows"])
        avg_stable = sum(r["stable_share"] for r in b["rows"]) / len(b["rows"])

        out_rows.append({
            "terrain": "hierarchical_burst_structural_v2",
            "window_size": ws,
            "band_id": f"{ws}_B{idx:02d}",
            "band_order": idx,
            "band_start": b["start"],
            "band_end": b["end"],
            "band_width": width,
            "band_center": round(mid, 2),
            "gap_from_previous": gap,
            "section": section_for(mid),
            "windows_merged": len(b["rows"]),
            "avg_residual_share": round(avg_residual, 4),
            "avg_stable_share": round(avg_stable, 4),
        })

        prev_end = b["end"]

fieldnames = [
    "terrain",
    "window_size",
    "band_id",
    "band_order",
    "band_start",
    "band_end",
    "band_width",
    "band_center",
    "gap_from_previous",
    "section",
    "windows_merged",
    "avg_residual_share",
    "avg_stable_share",
]

with OUT.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(out_rows)

print("WROTE", OUT.resolve())
