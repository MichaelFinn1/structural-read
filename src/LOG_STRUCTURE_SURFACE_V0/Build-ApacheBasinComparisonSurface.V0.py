import csv
from collections import Counter
from pathlib import Path

ROOT = Path("comparison_packets/apache_comparison_basin_001")

FILES = {
    "baseline_loghub_apache": ROOT / "baseline_loghub_apache" / "traversal_windows_v0.csv",
    "scan_acunetix": ROOT / "scan_acunetix" / "traversal_windows_v0.csv",
    "scan_netsparker": ROOT / "scan_netsparker" / "traversal_windows_v0.csv",
    "scan_w3af": ROOT / "scan_w3af" / "traversal_windows_v0.csv",
}

OUT = ROOT / "apache_basin_comparison_surface_v0.csv"

rows = []

for source_name, path in FILES.items():

    with path.open("r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    total = len(reader)

    posture_counts = Counter(
        r["local_residue_posture"]
        for r in reader
    )

    families = set(
        r["dominant_residual_family"]
        for r in reader
        if r["dominant_residual_family"].strip()
    )

    rows.append({
        "source": source_name,
        "windows": total,
        "avg_residual_share": round(sum(float(r["residual_share"]) for r in reader) / total, 4),
        "avg_middle_share": round(sum(float(r["middle_share"]) for r in reader) / total, 4),
        "avg_residual_self_adjacent": round(sum(float(r["residual_self_adjacent_share"]) for r in reader) / total, 4),
        "avg_residual_stable_attachment": round(sum(float(r["residual_near_stable_share"]) for r in reader) / total, 4),
        "dominant_posture": posture_counts.most_common(1)[0][0],
        "distinct_postures": len(posture_counts),
        "distinct_dominant_families": len(families),
    })

with OUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print("")
print("WROTE")
print(OUT.resolve())
print("")
