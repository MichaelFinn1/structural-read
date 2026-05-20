import csv
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/naturalistic_calibration_003")
MEASURED = BASE / "measured_sparse_misleading_structural_v1"

TRAVERSAL = MEASURED / "traversal_windows_v0.csv"
BANDS = MEASURED / "residual_band_sequence_v1.csv"
OUT = MEASURED / "constitution_phase_transition_surface_v1.csv"

trav_rows = list(csv.DictReader(TRAVERSAL.open("r", encoding="utf-8")))
band_rows = list(csv.DictReader(BANDS.open("r", encoding="utf-8")))

for r in trav_rows:
    r["window_size"] = int(float(r["window_size"]))
    r["stable_share"] = float(r["stable_share"])
    r["middle_share"] = float(r["middle_share"])
    r["residual_share"] = float(r["residual_share"])

for r in band_rows:
    r["window_size"] = int(r["window_size"])
    r["band_width"] = int(r["band_width"])

out_rows = []
prior_class = None

for ws in sorted(set(r["window_size"] for r in trav_rows)):
    local_trav = [r for r in trav_rows if r["window_size"] == ws]
    local_bands = [r for r in band_rows if r["window_size"] == ws]

    packet_count = len(local_bands)
    largest_band = max([int(r["band_width"]) for r in local_bands], default=0)

    avg_residual = sum(r["residual_share"] for r in local_trav) / len(local_trav)
    max_residual = max(r["residual_share"] for r in local_trav)

    if packet_count == 0 and max_residual < 0.08:
        field_class = "no_residual_basin"
    elif packet_count == 0:
        field_class = "subthreshold_residual_pressure"
    elif packet_count >= 5 and largest_band < 1000:
        field_class = "fragmented_sparse_packets"
    elif packet_count >= 2:
        field_class = "weak_distributed_bands"
    elif packet_count == 1 and largest_band >= 3000:
        field_class = "broad_consolidation"
    else:
        field_class = "single_local_band"

    if prior_class is None:
        transition = "initial_state"
    elif prior_class == field_class:
        transition = "class_holds"
    else:
        transition = f"{prior_class}_to_{field_class}"

    out_rows.append({
        "terrain": "sparse_misleading_structural_v1",
        "window_size": ws,
        "packet_count": packet_count,
        "largest_band_width": largest_band,
        "avg_residual": round(avg_residual, 4),
        "max_residual": round(max_residual, 4),
        "field_class": field_class,
        "transition_from_prior": transition,
        "boundary_note": "failure_terrain_observer_restraint_test",
    })

    prior_class = field_class

fieldnames = [
    "terrain",
    "window_size",
    "packet_count",
    "largest_band_width",
    "avg_residual",
    "max_residual",
    "field_class",
    "transition_from_prior",
    "boundary_note",
]

with OUT.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(out_rows)

print("WROTE", OUT.resolve())
