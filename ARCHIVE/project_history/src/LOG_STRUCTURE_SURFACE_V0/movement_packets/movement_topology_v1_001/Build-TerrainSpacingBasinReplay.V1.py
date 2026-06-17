import csv
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001")

OUT = BASE / "terrain_spacing_basin_replay_v1.csv"

# Current terrain replay references
# Replace later with actual alternate terrain replay outputs if available

terrain_rows = [
    {
        "terrain": "current_primary",
        "candidate_type": "spacing_basin",
        "supporting_rows": 9,
        "constitution_span": "50|75|100|150|200|250|350|500|750",
        "replay_status": "survives",
        "movement_quality": "locally_stable",
        "boundary_note": "baseline terrain replay"
    },

    {
        "terrain": "linux_candidate",
        "candidate_type": "spacing_basin",
        "supporting_rows": "",
        "constitution_span": "",
        "replay_status": "not_run",
        "movement_quality": "unknown",
        "boundary_note": "contrast terrain intentionally unresolved until replay"
    },

    {
        "terrain": "apache_candidate",
        "candidate_type": "spacing_basin",
        "supporting_rows": "",
        "constitution_span": "",
        "replay_status": "not_run",
        "movement_quality": "unknown",
        "boundary_note": "contrast terrain intentionally unresolved until replay"
    },

    {
        "terrain": "openstack_candidate",
        "candidate_type": "spacing_basin",
        "supporting_rows": "",
        "constitution_span": "",
        "replay_status": "not_run",
        "movement_quality": "unknown",
        "boundary_note": "contrast terrain intentionally unresolved until replay"
    }
]

fields = [
    "terrain",
    "candidate_type",
    "supporting_rows",
    "constitution_span",
    "replay_status",
    "movement_quality",
    "boundary_note"
]

with OUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(terrain_rows)

print("")
print("WROTE")
print(OUT.resolve())
print("")
