import csv
from pathlib import Path
from collections import Counter

ROOT = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/lynx_hare_cycle_001")
SRC = ROOT / "measured" / "lynx_temporal_surface_v1.csv"
OUT = ROOT / "measured" / "traversal_windows_v0.csv"

WINDOWS = [3, 5, 7, 9, 11, 15]

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))

for r in rows:
    r["year"] = int(r["year"])
    r["population"] = int(r["population"])
    r["delta"] = int(r["delta"])

out_rows = []

def shares(chunk):
    phases = Counter(r["phase"] for r in chunk)
    motions = Counter(r["motion"] for r in chunk)

    stable_count = phases["low_population"] + motions["plateau"]
    middle_count = phases["mid_population"] + motions["slow_rise"] + motions["slow_fall"]
    residual_count = phases["high_population"] + motions["rapid_rise"] + motions["rapid_fall"]

    total = stable_count + middle_count + residual_count

    if total == 0:
        return 1.0, 0.0, 0.0

    return (
        stable_count / total,
        middle_count / total,
        residual_count / total,
    )

for w in WINDOWS:
    window_id = 0

    for start in range(0, len(rows), w):
        chunk = rows[start:start + w]

        if not chunk:
            continue

        window_id += 1

        stable, middle, residual = shares(chunk)

        vals = {
            "stable": stable,
            "middle": middle,
            "residual": residual,
        }

        dominant = max(vals, key=vals.get)

        out_rows.append({
            "window_size": w,
            "window_id": f"window_{window_id:03d}",
            "line_start": start + 1,
            "line_end": start + len(chunk),
            "year_start": chunk[0]["year"],
            "year_end": chunk[-1]["year"],
            "stable_share": round(stable, 4),
            "middle_share": round(middle, 4),
            "residual_share": round(residual, 4),
            "dominant_posture": dominant,
            "boundary_note": "natural_windowed_traversal_no_ecological_causality_claim",
        })

fieldnames = [
    "window_size",
    "window_id",
    "line_start",
    "line_end",
    "year_start",
    "year_end",
    "stable_share",
    "middle_share",
    "residual_share",
    "dominant_posture",
    "boundary_note",
]

with OUT.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(out_rows)

print("WROTE", OUT.resolve())
print("ROWS", len(out_rows))
