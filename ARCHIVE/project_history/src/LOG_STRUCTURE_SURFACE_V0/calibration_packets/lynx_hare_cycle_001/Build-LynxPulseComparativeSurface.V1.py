import csv
from pathlib import Path

ROOT = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/lynx_hare_cycle_001")
SRC = ROOT / "measured" / "lynx_cycle_pulse_surface_v1.csv"
OUT = ROOT / "measured" / "lynx_pulse_comparative_surface_v1.csv"

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))

out_rows = []

for r in rows:
    peak = int(r["peak_population"])
    rise = float(r["rise_slope"])
    fall = float(r["fall_slope"])
    fall_abs = abs(fall)

    if peak >= 6000:
        amplitude_class = "high_amplitude"
    elif peak >= 3500:
        amplitude_class = "medium_amplitude"
    else:
        amplitude_class = "low_amplitude"

    if rise == 0 or fall_abs == 0:
        symmetry_class = "unfinished_or_one_sided"
    else:
        ratio = fall_abs / rise

        if ratio >= 1.6:
            symmetry_class = "fall_dominant"
        elif ratio <= 0.65:
            symmetry_class = "rise_dominant"
        else:
            symmetry_class = "near_symmetric"

    recovery = r["recovery_class"]

    if recovery == "deep_return_to_low":
        recovery_depth = "deep_recovery"
    elif recovery == "partial_return_to_low":
        recovery_depth = "partial_recovery"
    else:
        recovery_depth = "unfinished_or_incomplete"

    if symmetry_class == "fall_dominant" and recovery_depth == "deep_recovery":
        pulse_shape = "gradual_rise_sharp_fall"
    elif symmetry_class == "near_symmetric" and recovery_depth == "deep_recovery":
        pulse_shape = "sharp_rise_sharp_fall"
    elif symmetry_class == "rise_dominant":
        pulse_shape = "extended_rise_soft_return"
    elif recovery_depth == "unfinished_or_incomplete":
        pulse_shape = "unfinished_recovery"
    else:
        pulse_shape = "mixed_pulse_shape"

    out_rows.append({
        "cycle_id": r["cycle_id"],
        "amplitude_class": amplitude_class,
        "symmetry_class": symmetry_class,
        "recovery_depth": recovery_depth,
        "pulse_shape": pulse_shape,
        "peak_population": peak,
        "rise_slope": rise,
        "fall_slope": fall,
        "boundary_note": "comparative_pulse_shape_no_ecological_causality_claim",
    })

fieldnames = [
    "cycle_id",
    "amplitude_class",
    "symmetry_class",
    "recovery_depth",
    "pulse_shape",
    "peak_population",
    "rise_slope",
    "fall_slope",
    "boundary_note",
]

with OUT.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(out_rows)

print("WROTE", OUT.resolve())
print("ROWS", len(out_rows))
