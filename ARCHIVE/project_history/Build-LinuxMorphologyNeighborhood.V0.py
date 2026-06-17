import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent

INPUT = ROOT / "descent_packets" / "linux_residual_temporal_001" / "linux_residual_temporal_windows_v0.csv"
OUTDIR = ROOT / "linux_morphology_neighborhood_v0_out"
OUTDIR.mkdir(exist_ok=True)

rows = []

with open(INPUT, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)

    for r in reader:
        fam = r["dominant_residual_family"].strip()

        if not fam:
            continue

        rows.append({
            "window_size": r["window_size"],
            "window_id": r["window_id"],
            "family": fam,
            "posture": r["local_residue_posture"],
            "dominant_share": r["dominant_residual_family_share"]
        })

pairs = []

for i in range(len(rows)):
    for j in range(i + 1, len(rows)):

        a = rows[i]
        b = rows[j]

        prefix_overlap = 0

        a_tokens = a["family"].split()
        b_tokens = b["family"].split()

        for x, y in zip(a_tokens, b_tokens):
            if x == y:
                prefix_overlap += 1
            else:
                break

        shared_posture = (a["posture"] == b["posture"])

        pairs.append({
            "family_a": a["family"],
            "family_b": b["family"],
            "shared_prefix_depth": prefix_overlap,
            "shared_local_posture": shared_posture,
            "window_a": a["window_id"],
            "window_b": b["window_id"],
            "window_size_a": a["window_size"],
            "window_size_b": b["window_size"]
        })

OUTFILE = OUTDIR / "linux_local_morphology_neighborhood_surface_v0.csv"

with open(OUTFILE, "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "family_a",
            "family_b",
            "shared_prefix_depth",
            "shared_local_posture",
            "window_a",
            "window_b",
            "window_size_a",
            "window_size_b"
        ]
    )

    writer.writeheader()
    writer.writerows(pairs)

print()
print("WROTE")
print(OUTFILE)
print()
