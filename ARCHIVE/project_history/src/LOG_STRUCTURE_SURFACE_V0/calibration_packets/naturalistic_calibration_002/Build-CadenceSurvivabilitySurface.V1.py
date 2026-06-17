import csv
from collections import Counter
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/naturalistic_calibration_002")
MEASURED = BASE / "measured_hierarchical_burst_structural_v2_dense_v1"

SRC = MEASURED / "residual_band_sequence_v1.csv"
OUT = MEASURED / "cadence_survivability_surface_v1.csv"

TARGET_WINDOWS = [125,150,175,200,250,300,350,400,500,1000]

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))

for r in rows:
    r["window_size"] = int(r["window_size"])
    r["band_order"] = int(r["band_order"])
    r["band_width"] = int(r["band_width"])

    if r["gap_from_previous"] == "":
        r["gap_from_previous"] = None
    else:
        r["gap_from_previous"] = int(r["gap_from_previous"])

out_rows = []

for ws in TARGET_WINDOWS:

    selected = [r for r in rows if r["window_size"] == ws]
    selected.sort(key=lambda r: r["band_order"])

    gaps = [r["gap_from_previous"] for r in selected if r["gap_from_previous"] is not None]

    if len(gaps) == 0:
        continue

    counts = Counter(gaps)

    dominant_gap, dominant_count = counts.most_common(1)[0]

    total_gaps = len(gaps)

    cadence_strength = round(dominant_count / total_gaps, 4)

    cadence_breaks = sum(1 for g in gaps if g != dominant_gap)

    break_positions = [
        selected[i]["band_order"]
        for i,g in enumerate(gaps, start=1)
        if g != dominant_gap
    ]

    if cadence_strength >= 0.9:
        cadence_class = "near_uniform"
    elif cadence_strength >= 0.7:
        cadence_class = "strong_with_local_breaks"
    elif cadence_strength >= 0.5:
        cadence_class = "mixed_cadence"
    else:
        cadence_class = "weak_or_fragmented"

    if cadence_breaks == 0:
        deformation_onset = "none_visible"
    else:
        deformation_onset = f"packet_{break_positions[0]}"

    out_rows.append({
        "terrain": "hierarchical_burst_structural_v2",
        "window_size": ws,
        "dominant_gap": dominant_gap,
        "dominant_gap_count": dominant_count,
        "total_gaps": total_gaps,
        "cadence_strength": cadence_strength,
        "cadence_breaks": cadence_breaks,
        "break_positions": "|".join(str(x) for x in break_positions),
        "cadence_class": cadence_class,
        "deformation_onset_region": deformation_onset,
    })

fieldnames = [
    "terrain",
    "window_size",
    "dominant_gap",
    "dominant_gap_count",
    "total_gaps",
    "cadence_strength",
    "cadence_breaks",
    "break_positions",
    "cadence_class",
    "deformation_onset_region",
]

with OUT.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(out_rows)

print("WROTE", OUT.resolve())
