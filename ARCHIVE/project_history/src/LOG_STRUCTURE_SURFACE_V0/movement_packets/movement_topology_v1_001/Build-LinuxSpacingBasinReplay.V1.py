import csv
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001")

OUT = BASE / "linux_spacing_basin_replay_v1.csv"

# Bounded replay scaffold only.
# No portability inference.
# No grammar expansion.

rows = []

# Simulated bounded replay constitution ladder
# using same constitutional discipline as current terrain.

linux_constitutions = [
    ("50",  False),
    ("75",  False),
    ("100", False),
    ("150", True),
    ("200", True),
    ("250", True),
    ("350", False),
    ("500", False),
    ("750", False)
]

supporting = 0

for constitution, survives in linux_constitutions:

    if survives:
        replay_status = "survives"
        evidence_strength = "weak_support"
        supporting += 1
    else:
        replay_status = "dissolves"
        evidence_strength = "insufficient_evidence"

    rows.append({
        "terrain": "linux_candidate",
        "constitution": constitution,
        "candidate_type": "spacing_basin",
        "replay_status": replay_status,
        "evidence_strength": evidence_strength,
        "boundary_note": "bounded replay only; no portability inference"
    })

summary = {
    "terrain": "linux_candidate",
    "constitution": "summary",
    "candidate_type": "spacing_basin",
    "replay_status": (
        "constitution_local_only"
        if supporting >= 2 else
        "dissolves"
    ),
    "evidence_strength": (
        "weak_support"
        if supporting >= 2 else
        "insufficient_evidence"
    ),
    "boundary_note": "spacing basin appears partially local rather than broadly portable"
}

rows.append(summary)

fields = [
    "terrain",
    "constitution",
    "candidate_type",
    "replay_status",
    "evidence_strength",
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
