import csv
from pathlib import Path
from collections import Counter

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/naturalistic_calibration_003")
SOURCE = BASE / "terrains" / "sparse_misleading_structural_v2_5k.log"
OUT = BASE / "measured_sparse_misleading_structural_v2" / "weak_signal_motif_presence_v1.csv"

WINDOWS = [25, 50, 100, 250, 500, 1000]

markers = [
    "pseudo_cadence",
    "imperfect_echo",
    "reinforcement_candidate",
    "divergence_zone",
]

lines = SOURCE.read_text(encoding="utf-8").splitlines()

out_rows = []

for ws in WINDOWS:
    for start in range(0, len(lines), ws):
        chunk = lines[start:start + ws]
        if not chunk:
            continue

        counts = Counter()
        for line in chunk:
            for marker in markers:
                if marker in line:
                    counts[marker] += 1

        total_marked = sum(counts.values())

        if total_marked == 0:
            weak_class = "quiet"
        elif total_marked < ws * 0.15:
            weak_class = "weak_trace_present"
        elif total_marked < ws * 0.40:
            weak_class = "local_weak_motif_region"
        else:
            weak_class = "dense_weak_motif_region"

        out_rows.append({
            "terrain": "sparse_misleading_structural_v2",
            "window_size": ws,
            "line_start": start + 1,
            "line_end": start + len(chunk),
            "pseudo_cadence": counts["pseudo_cadence"],
            "imperfect_echo": counts["imperfect_echo"],
            "reinforcement_candidate": counts["reinforcement_candidate"],
            "divergence_zone": counts["divergence_zone"],
            "total_marked": total_marked,
            "marked_share": round(total_marked / len(chunk), 4),
            "weak_signal_class": weak_class,
            "boundary_note": "weak_signal_presence_not_residual_admission",
        })

fieldnames = [
    "terrain",
    "window_size",
    "line_start",
    "line_end",
    "pseudo_cadence",
    "imperfect_echo",
    "reinforcement_candidate",
    "divergence_zone",
    "total_marked",
    "marked_share",
    "weak_signal_class",
    "boundary_note",
]

with OUT.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(out_rows)

print("WROTE", OUT.resolve())
