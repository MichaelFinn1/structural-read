import csv
from pathlib import Path

ROOT = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/biodiversity_persistence_001")
SRC = ROOT / "raw" / "seasonal_passenger_series.csv"
OUT = ROOT / "measured" / "seasonal_persistence_surface_v1.csv"

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))

out = []
prior = None

for i, r in enumerate(rows, start=1):
    month = r["Month"]
    value = int(r["Passengers"])

    delta = 0 if prior is None else value - prior

    if value >= 450:
        carrier_class = "high_carrier"
    elif value >= 250:
        carrier_class = "mid_carrier"
    else:
        carrier_class = "low_carrier"

    if delta >= 60:
        motion_class = "rapid_rise"
    elif delta >= 15:
        motion_class = "slow_rise"
    elif delta <= -60:
        motion_class = "rapid_fall"
    elif delta <= -15:
        motion_class = "slow_fall"
    else:
        motion_class = "plateau"

    out.append({
        "index": i,
        "month": month,
        "value": value,
        "delta": delta,
        "carrier_class": carrier_class,
        "motion_class": motion_class,
        "boundary_note": "seasonal_persistence_no_domain_causality_claim",
    })

    prior = value

with OUT.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
    w.writeheader()
    w.writerows(out)

print("WROTE", OUT.resolve())
print("ROWS", len(out))
