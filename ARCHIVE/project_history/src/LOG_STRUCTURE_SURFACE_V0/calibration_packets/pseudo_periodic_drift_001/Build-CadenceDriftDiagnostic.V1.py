import csv
from pathlib import Path
from collections import Counter

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/pseudo_periodic_drift_001")
SOURCE = BASE / "terrains" / "pseudo_periodic_drift_v1_6k.log"
OUT = BASE / "measured_pseudo_periodic_drift_v1" / "cadence_drift_diagnostic_v1.csv"

WINDOWS = [25, 50, 100, 250, 500, 1000]

motifs = [
    "alpha cadence one",
    "beta cadence two",
    "gamma cadence three",
    "delta cadence four",
]

markers = [
    "pseudo_periodic",
    "cadence_interruption",
    "delayed_phase_echo",
    "quiet_carrier",
]

lines = SOURCE.read_text(encoding="utf-8").splitlines()
out_rows = []

def dominant_motif(line):
    for m in motifs:
        if m in line:
            return m
    return "none"

def dominant_marker(line):
    for m in markers:
        if m in line:
            return m
    return "none"

for ws in WINDOWS:
    prior_dom = None

    for start in range(0, len(lines), ws):
        chunk = lines[start:start + ws]
        if not chunk:
            continue

        motif_counts = Counter(dominant_motif(x) for x in chunk)
        marker_counts = Counter(dominant_marker(x) for x in chunk)

        dom_motif, dom_motif_count = motif_counts.most_common(1)[0]
        dom_marker, dom_marker_count = marker_counts.most_common(1)[0]

        motif_share = dom_motif_count / len(chunk)
        marker_share = dom_marker_count / len(chunk)

        if prior_dom is None:
            drift_from_prior = "initial"
        elif prior_dom == dom_motif:
            drift_from_prior = "motif_holds"
        else:
            drift_from_prior = "motif_shifts"

        if dom_marker == "quiet_carrier":
            cadence_class = "quiet_carrier"
        elif marker_share >= 0.75 and motif_share >= 0.5:
            cadence_class = "locally_stable_cadence"
        elif marker_share >= 0.45:
            cadence_class = "mixed_cadence_pressure"
        else:
            cadence_class = "weak_or_fragmented_cadence"

        out_rows.append({
            "terrain": "pseudo_periodic_drift_v1",
            "window_size": ws,
            "line_start": start + 1,
            "line_end": start + len(chunk),
            "dominant_motif": dom_motif,
            "dominant_motif_share": round(motif_share, 4),
            "dominant_marker": dom_marker,
            "dominant_marker_share": round(marker_share, 4),
            "drift_from_prior": drift_from_prior,
            "cadence_class": cadence_class,
            "boundary_note": "cadence_diagnostic_not_residual_admission",
        })

        prior_dom = dom_motif

fieldnames = [
    "terrain",
    "window_size",
    "line_start",
    "line_end",
    "dominant_motif",
    "dominant_motif_share",
    "dominant_marker",
    "dominant_marker_share",
    "drift_from_prior",
    "cadence_class",
    "boundary_note",
]

with OUT.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(out_rows)

print("WROTE", OUT.resolve())
