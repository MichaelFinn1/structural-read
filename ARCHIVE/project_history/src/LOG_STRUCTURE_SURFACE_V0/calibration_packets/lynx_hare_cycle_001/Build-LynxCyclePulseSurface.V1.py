import csv
from pathlib import Path

ROOT = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/lynx_hare_cycle_001")
SRC = ROOT / "measured" / "lynx_temporal_surface_v1.csv"
OUT = ROOT / "measured" / "lynx_cycle_pulse_surface_v1.csv"

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))

for r in rows:
    r["year"] = int(r["year"])
    r["population"] = int(r["population"])
    r["delta"] = int(r["delta"])

cycles = []
in_cycle = False
cycle_start = None
peak = None
fall_end = None

for i, r in enumerate(rows):

    if not in_cycle:
        if r["motion"] in ["slow_rise", "rapid_rise"]:
            in_cycle = True
            cycle_start = r
            peak = r
            fall_end = None
        continue

    if r["population"] > peak["population"]:
        peak = r

    if r["motion"] in ["slow_fall", "rapid_fall"]:
        fall_end = r

    if fall_end is not None and r["motion"] == "plateau":
        cycles.append({
            "rise_start": cycle_start,
            "peak": peak,
            "fall_end": fall_end,
        })

        in_cycle = False
        cycle_start = None
        peak = None
        fall_end = None

if in_cycle and peak is not None:
    cycles.append({
        "rise_start": cycle_start,
        "peak": peak,
        "fall_end": fall_end if fall_end is not None else rows[-1],
    })

out_rows = []

for idx, c in enumerate(cycles, start=1):
    rise_start = c["rise_start"]
    peak = c["peak"]
    fall_end = c["fall_end"]

    rise_years = max(1, peak["year"] - rise_start["year"])
    fall_years = max(1, fall_end["year"] - peak["year"])

    rise_slope = (peak["population"] - rise_start["population"]) / rise_years
    fall_slope = (fall_end["population"] - peak["population"]) / fall_years

    duration = fall_end["year"] - rise_start["year"] + 1

    if fall_end["population"] < 500:
        recovery_class = "deep_return_to_low"
    elif fall_end["population"] < 1500:
        recovery_class = "partial_return_to_low"
    else:
        recovery_class = "incomplete_return"

    out_rows.append({
        "cycle_id": f"cycle_{idx:03d}",
        "rise_start": rise_start["year"],
        "peak_year": peak["year"],
        "fall_end": fall_end["year"],
        "duration": duration,
        "peak_population": peak["population"],
        "rise_slope": round(rise_slope, 2),
        "fall_slope": round(fall_slope, 2),
        "recovery_class": recovery_class,
        "boundary_note": "natural_cycle_pulse_no_ecological_causality_claim",
    })

fieldnames = [
    "cycle_id",
    "rise_start",
    "peak_year",
    "fall_end",
    "duration",
    "peak_population",
    "rise_slope",
    "fall_slope",
    "recovery_class",
    "boundary_note",
]

with OUT.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(out_rows)

print("WROTE", OUT.resolve())
print("CYCLES", len(out_rows))
