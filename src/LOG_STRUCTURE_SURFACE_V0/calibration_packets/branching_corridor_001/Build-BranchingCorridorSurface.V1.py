import csv
from pathlib import Path
from collections import Counter

PACKET = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/branching_corridor_001")

SRC = PACKET / "raw" / "branching_transport_graph.edgelist"
OUT = PACKET / "measured" / "branching_corridor_surface_v1.csv"

edges = []

for line in SRC.read_text(encoding="utf-8").splitlines():
    parts = line.strip().split()

    if len(parts) < 2:
        continue

    a = parts[0]
    b = parts[1]

    edges.append((a,b))

degree = Counter()

for a,b in edges:
    degree[a] += 1
    degree[b] += 1

rows = []

for i,(a,b) in enumerate(edges, start=1):

    local_density = degree[a] + degree[b]

    if local_density >= 16:
        corridor_class = "high_corridor_pressure"
    elif local_density >= 8:
        corridor_class = "mid_corridor_pressure"
    else:
        corridor_class = "sparse_branch"

    if abs(degree[a] - degree[b]) >= 6:
        asymmetry = "strong_asymmetry"
    elif abs(degree[a] - degree[b]) >= 3:
        asymmetry = "moderate_asymmetry"
    else:
        asymmetry = "balanced"

    rows.append({
        "edge_id": i,
        "node_a": a,
        "node_b": b,
        "degree_a": degree[a],
        "degree_b": degree[b],
        "corridor_class": corridor_class,
        "asymmetry_class": asymmetry,
        "boundary_note": "observer_side_branching_surface_not_semantic_network_claim"
    })

with OUT.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print("WROTE", OUT.resolve())
print("ROWS", len(rows))
