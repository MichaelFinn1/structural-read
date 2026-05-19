import csv
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/naturalistic_calibration_002")
MEASURED = BASE / "measured_hierarchical_burst_structural_v2_dense_v1"

BANDS = MEASURED / "residual_band_sequence_v1.csv"
CADENCE = MEASURED / "cadence_survivability_surface_v1.csv"
ANCHOR = MEASURED / "anchor_survivability_between_constitutions_v1.csv"

OUT = MEASURED / "constitution_phase_transition_surface_v1.csv"

band_rows = list(csv.DictReader(BANDS.open("r", encoding="utf-8")))
cad_rows = list(csv.DictReader(CADENCE.open("r", encoding="utf-8")))
anchor_rows = list(csv.DictReader(ANCHOR.open("r", encoding="utf-8")))

for r in band_rows:
    r["window_size"] = int(r["window_size"])
    r["band_width"] = int(r["band_width"])

for r in cad_rows:
    r["window_size"] = int(r["window_size"])
    r["dominant_gap"] = int(r["dominant_gap"])
    r["cadence_strength"] = float(r["cadence_strength"])

for r in anchor_rows:
    r["to_window"] = int(r["to_window"])
    r["relation"] = r["relation"]

windows = sorted(set(r["window_size"] for r in band_rows))

out_rows = []

prior_class = None

for ws in windows:

    local_bands = [r for r in band_rows if r["window_size"] == ws]

    packet_count = len(local_bands)

    largest_band = max(r["band_width"] for r in local_bands)

    cad = next((r for r in cad_rows if r["window_size"] == ws), None)

    dominant_gap = ""
    cadence_strength = 0

    if cad:
        dominant_gap = cad["dominant_gap"]
        cadence_strength = cad["cadence_strength"]

    local_anchor_rows = [
        r for r in anchor_rows
        if r["to_window"] == ws and r["relation"] == "anchor_holds"
    ]

    anchor_count = len(local_anchor_rows)

    # lightweight procedural classification

    if packet_count >= 5 and cadence_strength >= 0.9:
        field_class = "packeted"

    elif packet_count >= 2 and largest_band >= 1500:
        field_class = "mixed_packet_ladder"

    elif packet_count == 1 and largest_band < 3800:
        field_class = "ladder"

    elif packet_count == 1 and largest_band >= 3800:
        field_class = "broad_consolidation"

    else:
        field_class = "unresolved_transition"

    if prior_class is None:
        transition = "initial_state"

    elif prior_class == field_class:
        transition = "class_holds"

    else:
        transition = f"{prior_class}_to_{field_class}"

    out_rows.append({
        "terrain": "hierarchical_burst_structural_v2",
        "window_size": ws,
        "packet_count": packet_count,
        "dominant_gap": dominant_gap,
        "anchor_count": anchor_count,
        "largest_band_width": largest_band,
        "cadence_strength": cadence_strength,
        "field_class": field_class,
        "transition_from_prior": transition,
        "boundary_note": "observer_side_phase_class_no_causal_claim"
    })

    prior_class = field_class

fieldnames = [
    "terrain",
    "window_size",
    "packet_count",
    "dominant_gap",
    "anchor_count",
    "largest_band_width",
    "cadence_strength",
    "field_class",
    "transition_from_prior",
    "boundary_note",
]

with OUT.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(out_rows)

print("WROTE", OUT.resolve())
