import csv
from pathlib import Path
from collections import Counter

PACKET = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/branching_corridor_002")
SRC = PACKET / "raw" / "branching_transport_graph_asymmetric.edgelist"
OUT = PACKET / "measured" / "branching_corridor_surface_v1.csv"

edges = []

for line in SRC.read_text(encoding="utf-8").splitlines():
    parts = line.strip().split()
    if len(parts) < 2:
        continue
    edges.append((parts[0], parts[1]))

degree = Counter()
for a,b in edges:
    degree[a] += 1
    degree[b] += 1

rows = []

for i,(a,b) in enumerate(edges, start=1):
    density = degree[a] + degree[b]
    diff = abs(degree[a] - degree[b])

    if density >= 12:
        corridor_class = "high_corridor_pressure"
    elif density >= 7:
        corridor_class = "mid_corridor_pressure"
    else:
        corridor_class = "sparse_branch"

    if diff >= 5:
        asymmetry_class = "strong_asymmetry"
    elif diff >= 3:
        asymmetry_class = "moderate_asymmetry"
    else:
        asymmetry_class = "balanced"

    if degree[a] >= 6 or degree[b] >= 6:
        node_role = "hub_contact"
    elif corridor_class == "high_corridor_pressure":
        node_role = "carrier_contact"
    elif corridor_class == "sparse_branch":
        node_role = "branch_contact"
    else:
        node_role = "corridor_contact"

    rows.append({
        "edge_id": i,
        "node_a": a,
        "node_b": b,
        "degree_a": degree[a],
        "degree_b": degree[b],
        "local_density": density,
        "corridor_class": corridor_class,
        "asymmetry_class": asymmetry_class,
        "node_role": node_role,
        "boundary_note": "observer_side_asymmetric_branching_control_no_biological_claim"
    })

with OUT.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print("WROTE", OUT.resolve())
print("ROWS", len(rows))
