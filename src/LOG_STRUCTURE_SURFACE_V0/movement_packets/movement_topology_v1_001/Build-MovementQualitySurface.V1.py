import csv
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001")

TRANS = BASE / "constitution_transition_surface_v1.csv"
DEG = BASE / "replay_degradation_surface_v1.csv"
PAUSE = BASE / "pause_basin_surface_v1.csv"
HOLLOW = BASE / "hollow_survivability_sweep_v1.csv"

OUT = BASE / "movement_quality_surface_v1.csv"

trans_rows = list(csv.DictReader(TRANS.open("r", encoding="utf-8")))
deg_rows = list(csv.DictReader(DEG.open("r", encoding="utf-8")))
pause_rows = list(csv.DictReader(PAUSE.open("r", encoding="utf-8")))
hollow_rows = list(csv.DictReader(HOLLOW.open("r", encoding="utf-8")))

rows = []

# Transition movement quality
for r in trans_rows:
    texture = r["transition_texture"]

    if texture == "continuity_friendly":
        quality = "stable_movement"
    elif texture == "recomposition_heavy":
        quality = "recomposition_movement"
    else:
        quality = "fragile_movement"

    rows.append({
        "quality_id": f"mq_{len(rows)+1:03}",
        "source_surface": "constitution_transition_surface_v1",
        "movement_dimension": "transition_texture",
        "scope": r["transition"],
        "movement_quality": quality,
        "supporting_detail": f'texture={texture}; continues={r["continues"]}; appears={r["appears"]}; disappears={r["disappears"]}',
        "boundary_note": "transition quality describes reread movement, not terrain truth"
    })

# Degradation pressure
for r in deg_rows:
    rows.append({
        "quality_id": f"mq_{len(rows)+1:03}",
        "source_surface": "replay_degradation_surface_v1",
        "movement_dimension": "degradation_pressure",
        "scope": r["affected_item"],
        "movement_quality": f'pressure_{r["severity"]}',
        "supporting_detail": r["supporting_detail"],
        "boundary_note": "degradation pressure is inspectable weakening, not failure"
    })

# Pause support
pause_counts = {}
for r in pause_rows:
    pause_counts[r["pause_type"]] = pause_counts.get(r["pause_type"], 0) + 1

for pause_type, count in pause_counts.items():
    rows.append({
        "quality_id": f"mq_{len(rows)+1:03}",
        "source_surface": "pause_basin_surface_v1",
        "movement_dimension": "pause_support",
        "scope": pause_type,
        "movement_quality": "pause_supported",
        "supporting_detail": f"supporting_rows={count}",
        "boundary_note": "pause support marks lawful non-forcing, not inactivity"
    })

# Hollow survivability
for r in hollow_rows:
    rows.append({
        "quality_id": f"mq_{len(rows)+1:03}",
        "source_surface": "hollow_survivability_sweep_v1",
        "movement_dimension": "basin_survivability",
        "scope": r["probe_type"],
        "movement_quality": r["survivability_result"],
        "supporting_detail": f'baseline={r["baseline_supporting_rows"]}; probe={r["probe_supporting_rows"]}',
        "boundary_note": "basin survivability remains candidate evidence only"
    })

fields = [
    "quality_id",
    "source_surface",
    "movement_dimension",
    "scope",
    "movement_quality",
    "supporting_detail",
    "boundary_note"
]

with OUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print("")
print("WROTE")
print(OUT.resolve())
print("")
