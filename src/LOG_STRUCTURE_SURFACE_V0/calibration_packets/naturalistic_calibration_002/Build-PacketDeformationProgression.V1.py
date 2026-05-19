import csv
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/naturalistic_calibration_002")
MEASURED = BASE / "measured_hierarchical_burst_structural_v2_dense_v1"
SRC = MEASURED / "residual_band_sequence_v1.csv"
OUT = MEASURED / "packet_deformation_progression_v1.csv"

TARGET_WINDOW = 125

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))
rows = [r for r in rows if int(r["window_size"]) == TARGET_WINDOW]
rows.sort(key=lambda r: int(r["band_order"]))

out_rows = []

prev = None

for r in rows:
    order = int(r["band_order"])
    width = int(r["band_width"])
    gap_raw = r["gap_from_previous"]
    gap = "" if gap_raw == "" else int(gap_raw)

    if prev is None:
        width_delta = ""
        gap_delta = ""
        deformation_from_prior = "initial_boundary"
    else:
        prev_width = int(prev["band_width"])
        prev_gap_raw = prev["gap_from_previous"]
        prev_gap = "" if prev_gap_raw == "" else int(prev_gap_raw)

        width_delta = width - prev_width

        if gap == "" or prev_gap == "":
            gap_delta = ""
        else:
            gap_delta = gap - prev_gap

        if width == prev_width and gap_delta == 0:
            deformation_from_prior = "repeats_spacing_and_width"
        elif width == prev_width:
            deformation_from_prior = "width_holds_spacing_changes"
        elif width < prev_width:
            deformation_from_prior = "thins"
        elif width > prev_width:
            deformation_from_prior = "thickens"
        else:
            deformation_from_prior = "ambiguous"

    if width >= 400:
        width_class = "heavy"
    elif width >= 200:
        width_class = "medium"
    else:
        width_class = "thin"

    out_rows.append({
        "terrain": r["terrain"],
        "window_size": TARGET_WINDOW,
        "packet_order": order,
        "band_id": r["band_id"],
        "band_start": r["band_start"],
        "band_end": r["band_end"],
        "band_width": width,
        "width_class": width_class,
        "gap_from_previous": gap,
        "width_delta_from_prior": width_delta,
        "gap_delta_from_prior": gap_delta,
        "section": r["section"],
        "avg_residual_share": r["avg_residual_share"],
        "deformation_from_prior": deformation_from_prior,
        "boundary_note": "observer_side_packet_band_no_identity_claim",
    })

    prev = r

fieldnames = [
    "terrain",
    "window_size",
    "packet_order",
    "band_id",
    "band_start",
    "band_end",
    "band_width",
    "width_class",
    "gap_from_previous",
    "width_delta_from_prior",
    "gap_delta_from_prior",
    "section",
    "avg_residual_share",
    "deformation_from_prior",
    "boundary_note",
]

with OUT.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(out_rows)

print("WROTE", OUT.resolve())
