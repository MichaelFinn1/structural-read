import csv
from collections import Counter
from pathlib import Path

ROOT = Path("comparison_packets/traversal_comparison_surface_001")

FILES = {
    "Linux": ROOT / "linux_traversal_windows_v0.csv",
    "Thunderbird": ROOT / "thunderbird_traversal_windows_v0.csv",
}

OUT = ROOT / "traversal_comparison_surface_v0.csv"

rows = []

for terrain, path in FILES.items():

    with path.open("r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    posture_counts = Counter(
        r["local_residue_posture"]
        for r in reader
    )

    total = len(reader)

    avg_residual_share = (
        sum(float(r["residual_share"]) for r in reader)
        / total
    )

    avg_middle_share = (
        sum(float(r["middle_share"]) for r in reader)
        / total
    )

    avg_self_adjacent = (
        sum(float(r["residual_self_adjacent_share"]) for r in reader)
        / total
    )

    avg_stable_attach = (
        sum(float(r["residual_near_stable_share"]) for r in reader)
        / total
    )

    dominant_posture = posture_counts.most_common(1)[0][0]

    rows.append({
        "terrain": terrain,
        "windows": total,
        "avg_residual_share": round(avg_residual_share, 4),
        "avg_middle_share": round(avg_middle_share, 4),
        "avg_residual_self_adjacent": round(avg_self_adjacent, 4),
        "avg_residual_stable_attachment": round(avg_stable_attach, 4),
        "dominant_posture": dominant_posture,
    })

with OUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=list(rows[0].keys())
    )
    writer.writeheader()
    writer.writerows(rows)

print("")
print("WROTE")
print(OUT.resolve())
print("")
