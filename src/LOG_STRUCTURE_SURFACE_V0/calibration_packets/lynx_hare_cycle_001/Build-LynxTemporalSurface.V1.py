import csv
from pathlib import Path

ROOT = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/lynx_hare_cycle_001")
SRC = ROOT / "raw" / "lynx_cycle.csv"
OUT = ROOT / "measured" / "lynx_temporal_surface_v1.csv"

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))
out_rows = []

prior = None

for r in rows:
    year = int(float(r["time"]))
    count = int(float(r["value"]))

    delta = 0 if prior is None else count - prior

    if count >= 6000:
        phase = "high_population"
    elif count >= 3000:
        phase = "mid_population"
    else:
        phase = "low_population"

    if delta > 1500:
        motion = "rapid_rise"
    elif delta > 300:
        motion = "slow_rise"
    elif delta < -1500:
        motion = "rapid_fall"
    elif delta < -300:
        motion = "slow_fall"
    else:
        motion = "plateau"

    out_rows.append({
        "year": year,
        "population": count,
        "delta": delta,
        "phase": phase,
        "motion": motion
    })

    prior = count

with OUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["year", "population", "delta", "phase", "motion"]
    )
    writer.writeheader()
    writer.writerows(out_rows)

print("WROTE", OUT.resolve())
print("ROWS", len(out_rows))
