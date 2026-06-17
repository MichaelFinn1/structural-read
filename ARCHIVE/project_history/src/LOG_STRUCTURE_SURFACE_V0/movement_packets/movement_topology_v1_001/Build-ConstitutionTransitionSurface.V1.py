import csv
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001")

REL = BASE / "middle_feature_relation_read_v1.csv"
OUT = BASE / "constitution_transition_surface_v1.csv"

rel_rows = list(csv.DictReader(REL.open("r", encoding="utf-8")))

buckets = {}

for r in rel_rows:
    transition = f'{r["from_window_size"]}->{r["to_window_size"]}'
    buckets.setdefault(transition, {
        "continues": 0,
        "merges": 0,
        "splits": 0,
        "appears": 0,
        "disappears": 0,
        "ambiguous": 0,
        "total": 0
    })

    relation = r["relation_type"]
    if relation in buckets[transition]:
        buckets[transition][relation] += 1
    buckets[transition]["total"] += 1

rows = []

for transition, c in buckets.items():
    recomposition = c["merges"] + c["splits"]
    loss = c["appears"] + c["disappears"] + c["ambiguous"]
    continuity = c["continues"]

    if continuity >= recomposition and continuity >= loss:
        texture = "continuity_friendly"
    elif recomposition >= loss:
        texture = "recomposition_heavy"
    else:
        texture = "fragmentation_prone"

    rows.append({
        "transition": transition,
        "continues": c["continues"],
        "merges": c["merges"],
        "splits": c["splits"],
        "appears": c["appears"],
        "disappears": c["disappears"],
        "ambiguous": c["ambiguous"],
        "total_relations": c["total"],
        "transition_texture": texture,
        "boundary_note": "transition texture describes reread deformation, not quality or truth"
    })

fields = [
    "transition",
    "continues",
    "merges",
    "splits",
    "appears",
    "disappears",
    "ambiguous",
    "total_relations",
    "transition_texture",
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
