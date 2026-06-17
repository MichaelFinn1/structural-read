import csv
from pathlib import Path
from collections import Counter

PACKET = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/branching_corridor_003")
SRC = PACKET / "raw" / "branching_transport_graph_interrupted.edgelist"
OUT = PACKET / "measured" / "branching_corridor_interruption_surface_v1.csv"

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

    if density >= 10:
        corridor_class = "overload_corridor_pressure"
    elif density >= 7:
        corridor_class = "reroute_corridor_pressure"
    elif density >= 4:
        corridor_class = "weak_branch_pressure"
    else:
        corridor_class = "sparse_or_abandoned"

    if diff >= 5:
        asymmetry_class = "strong_asymmetry"
    elif diff >= 3:
        asymmetry_class = "moderate_asymmetry"
    else:
        asymmetry_class = "balanced"

    nodes = {a,b}

    if any(n.startswith("H") for n in nodes):
        interruption_role = "overload_near_break"
    elif any(n.startswith("R") for n in nodes):
        interruption_role = "reroute_attempt"
    elif any(n.startswith("A") for n in nodes):
        interruption_role = "abandoned_branch"
    elif a.startswith("C") and b.startswith("C"):
        interruption_role = "carrier_fragment"
    else:
        interruption_role = "mixed_contact"

    rows.append({
        "edge_id": i,
        "node_a": a,
        "node_b": b,
        "degree_a": degree[a],
        "degree_b": degree[b],
        "local_density": density,
        "corridor_class": corridor_class,
        "asymmetry_class": asymmetry_class,
        "interruption_role": interruption_role,
        "boundary_note": "observer_side_interrupted_branching_control_no_biological_claim"
    })

with OUT.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print("WROTE", OUT.resolve())
print("ROWS", len(rows))
