import csv
from pathlib import Path
from collections import Counter

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/interrupted_replay_001")
SOURCE = BASE / "terrains" / "interrupted_replay_v1_7k.log"
OUT = BASE / "measured_interrupted_replay_v1" / "interruption_reentry_diagnostic_v1.csv"

WINDOWS = [50, 100, 250, 500, 1000]

markers = [
    "replay_phase_A",
    "interruption_gap",
    "weak_return",
    "replay_phase_B_partial_restart",
    "mixed_reentry",
    "quiet_reentry_field",
    "recomposed_tail",
]

lines = SOURCE.read_text(encoding="utf-8").splitlines()
out_rows = []

for ws in WINDOWS:
    prior_marker = None

    for start in range(0, len(lines), ws):
        chunk = lines[start:start + ws]
        if not chunk:
            continue

        counts = Counter()

        for line in chunk:
            for marker in markers:
                if marker in line:
                    counts[marker] += 1

        dominant_marker, dominant_count = counts.most_common(1)[0]
        dominant_share = dominant_count / len(chunk)

        if prior_marker is None:
            transition = "initial"
        elif prior_marker == dominant_marker:
            transition = "phase_holds"
        else:
            transition = f"{prior_marker}_to_{dominant_marker}"

        if dominant_marker == "interruption_gap":
            replay_class = "gap_dominant"
        elif dominant_marker == "weak_return":
            replay_class = "weak_return_pocket"
        elif dominant_marker == "replay_phase_B_partial_restart":
            replay_class = "partial_restart"
        elif dominant_marker == "mixed_reentry":
            replay_class = "mixed_reentry"
        elif dominant_marker == "recomposed_tail":
            replay_class = "tail_recomposition"
        elif dominant_marker == "replay_phase_A":
            replay_class = "initial_replay"
        else:
            replay_class = "quiet_or_mixed"

        out_rows.append({
            "terrain": "interrupted_replay_v1",
            "window_size": ws,
            "line_start": start + 1,
            "line_end": start + len(chunk),
            "dominant_marker": dominant_marker,
            "dominant_marker_share": round(dominant_share, 4),
            "transition_from_prior": transition,
            "replay_class": replay_class,
            "boundary_note": "interruption_reentry_diagnostic_not_identity_claim",
        })

        prior_marker = dominant_marker

fieldnames = [
    "terrain",
    "window_size",
    "line_start",
    "line_end",
    "dominant_marker",
    "dominant_marker_share",
    "transition_from_prior",
    "replay_class",
    "boundary_note",
]

with OUT.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(out_rows)

print("WROTE", OUT.resolve())
