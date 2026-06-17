import csv
from pathlib import Path
from collections import Counter

ROOT = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/collapse_terrain_001")

SRC = ROOT / "terrains" / "collapse_terrain_v1_10k.log"
OUT = ROOT / "measured" / "traversal_windows_v0.csv"

WINDOWS = [25,50,100,250,500,1000]

rows = []

lines = SRC.read_text(encoding="utf-8").splitlines()

for w in WINDOWS:

    segments = []

    for i in range(0, len(lines), w):
        chunk = lines[i:i+w]

        c = Counter(chunk)

        dominant_share = c.most_common(1)[0][1] / len(chunk)

        if dominant_share >= 0.80:
            posture = "stable"
        elif dominant_share >= 0.45:
            posture = "middle"
        else:
            posture = "residual"

        segments.append(posture)

    posture_counts = Counter(segments)

    stable_share = posture_counts["stable"] / len(segments)
    middle_share = posture_counts["middle"] / len(segments)
    residual_share = posture_counts["residual"] / len(segments)

    if stable_share > 0.60:
        phase = "initial_replay"
    elif middle_share > 0.45:
        phase = "partial_restart"
    elif residual_share > 0.70:
        phase = "collapse_dominant"
    else:
        phase = "mixed_fragmentation"

    rows.append({
        "window_size": w,
        "stable_share": round(stable_share,4),
        "middle_share": round(middle_share,4),
        "residual_share": round(residual_share,4),
        "phase_read": phase
    })

with OUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "window_size",
            "stable_share",
            "middle_share",
            "residual_share",
            "phase_read"
        ]
    )

    writer.writeheader()
    writer.writerows(rows)

print("WROTE", OUT.resolve())
print("ROWS", len(rows))
