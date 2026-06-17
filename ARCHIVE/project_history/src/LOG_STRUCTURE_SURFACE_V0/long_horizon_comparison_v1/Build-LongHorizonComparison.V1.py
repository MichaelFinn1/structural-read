import csv
from pathlib import Path
from collections import Counter

ROOT = Path("src/LOG_STRUCTURE_SURFACE_V0")

PACKETS = [
    {
        "terrain": "OpenStack_long_normal2",
        "packet": ROOT / "long_duration_packets" / "openstack_long_horizon_001",
    },
]

OUT = ROOT / "long_horizon_comparison_v1"
OUT.mkdir(parents=True, exist_ok=True)

rows = []

for p in PACKETS:
    packet = p["packet"]
    traversal = packet / "measured" / "traversal_windows_v0.csv"
    boundary_v2 = packet / "measured" / "boundary_deformation_surface_v2.csv"

    if not traversal.exists():
        continue

    trows = list(csv.DictReader(traversal.open("r", encoding="utf-8")))

    for r in trows:
        for k in ["window_size","stable_share","middle_share","residual_share"]:
            r[k] = float(r[k])

    sizes = sorted(set(int(r["window_size"]) for r in trows))

    avg_stable = sum(r["stable_share"] for r in trows) / len(trows)
    avg_middle = sum(r["middle_share"] for r in trows) / len(trows)
    avg_residual = sum(r["residual_share"] for r in trows) / len(trows)

    by_size = []
    for s in sizes:
        sr = [r for r in trows if int(r["window_size"]) == s]
        by_size.append({
            "size": s,
            "stable": sum(r["stable_share"] for r in sr) / len(sr),
            "middle": sum(r["middle_share"] for r in sr) / len(sr),
            "residual": sum(r["residual_share"] for r in sr) / len(sr),
            "windows": len(sr),
        })

    min_size = by_size[0]
    max_size = by_size[-1]

    relation_counts = Counter()
    if boundary_v2.exists():
        brows = list(csv.DictReader(boundary_v2.open("r", encoding="utf-8")))
        relation_counts = Counter(r["relation_type"] for r in brows)

    rows.append({
        "terrain": p["terrain"],
        "packet_path": str(packet),
        "min_window_size": min(sizes),
        "max_window_size": max(sizes),
        "window_sizes": " ".join(str(s) for s in sizes),
        "avg_stable_share": round(avg_stable, 4),
        "avg_middle_share": round(avg_middle, 4),
        "avg_residual_share": round(avg_residual, 4),
        "fine_residual_share": round(min_size["residual"], 4),
        "wide_residual_share": round(max_size["residual"], 4),
        "residual_delta_wide_minus_fine": round(max_size["residual"] - min_size["residual"], 4),
        "fine_middle_share": round(min_size["middle"], 4),
        "wide_middle_share": round(max_size["middle"], 4),
        "middle_delta_wide_minus_fine": round(max_size["middle"] - min_size["middle"], 4),
        "many_to_one_absorption": relation_counts.get("many_to_one_absorption", 0),
        "one_to_many_split": relation_counts.get("one_to_many_split", 0),
        "one_to_one_continuation": relation_counts.get("one_to_one_continuation", 0),
        "recolored_overlap": relation_counts.get("recolored_overlap", 0),
        "comparison_note": "long-horizon survivability ecology summary",
    })

fields = [
    "terrain",
    "packet_path",
    "min_window_size",
    "max_window_size",
    "window_sizes",
    "avg_stable_share",
    "avg_middle_share",
    "avg_residual_share",
    "fine_residual_share",
    "wide_residual_share",
    "residual_delta_wide_minus_fine",
    "fine_middle_share",
    "wide_middle_share",
    "middle_delta_wide_minus_fine",
    "many_to_one_absorption",
    "one_to_many_split",
    "one_to_one_continuation",
    "recolored_overlap",
    "comparison_note",
]

out_csv = OUT / "long_horizon_comparison_v1.csv"
with out_csv.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

readme = OUT / "LONG_HORIZON_COMPARISON_V1.md"
readme.write_text("""# LONG_HORIZON_COMPARISON_V1

Status:
comparison_shell_open

## Purpose

Compare long-horizon survivability ecology across operational terrains.

This does not compare semantic meaning or dataset identity.

It compares observer-side reread behavior:

- stable / middle / residual posture across constitutions
- fine-to-wide survivability shifts
- absorption / split / continuation / recoloring pressure
- terrain-level deformation tendency

## Boundary

This surface does not infer:

- cause
- anomaly
- hidden system state
- operational meaning
- object identity

## Hold

Compare survivability ecology, not dataset meaning.
""", encoding="utf-8")

print("WROTE", out_csv.resolve())
print("WROTE", readme.resolve())
