import csv
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/naturalistic_calibration_003")
MEASURED = BASE / "measured_sparse_misleading_structural_v1"

SRC = MEASURED / "traversal_windows_v0.csv"
OUT = MEASURED / "residual_band_sequence_v1.csv"

RESIDUAL_THRESHOLD = 0.08

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))

for r in rows:
    r["window_size"] = int(float(r["window_size"]))
    r["line_start"] = int(float(r["line_start"]))
    r["line_end"] = int(float(r["line_end"]))
    r["residual_share"] = float(r["residual_share"])
    r["stable_share"] = float(r["stable_share"])

out_rows = []

for ws in sorted(set(r["window_size"] for r in rows)):
    local = [r for r in rows if r["window_size"] == ws]
    local.sort(key=lambda r: r["line_start"])

    bands = []
    current = []

    for r in local:
        if r["residual_share"] >= RESIDUAL_THRESHOLD:
            current.append(r)
        else:
            if current:
                bands.append(current)
                current = []

    if current:
        bands.append(current)

    for idx, band in enumerate(bands, start=1):
        start = band[0]["line_start"]
        end = band[-1]["line_end"]
        width = end - start + 1
        center = round((start + end) / 2, 2)

        gap = ""
        if idx > 1:
            prev_end = bands[idx - 2][-1]["line_end"]
            gap = start - prev_end - 1

        out_rows.append({
            "terrain": "sparse_misleading_structural_v1",
            "window_size": ws,
            "band_id": f"{ws}_B{idx:02d}",
            "band_order": idx,
            "band_start": start,
            "band_end": end,
            "band_width": width,
            "band_center": center,
            "gap_from_previous": gap,
            "windows_merged": len(band),
            "avg_residual_share": round(sum(x["residual_share"] for x in band) / len(band), 4),
            "avg_stable_share": round(sum(x["stable_share"] for x in band) / len(band), 4),
        })

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
    "windows_merged",
    "avg_residual_share",
    "avg_stable_share",
]

with OUT.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(out_rows)

print("WROTE", OUT.resolve())
