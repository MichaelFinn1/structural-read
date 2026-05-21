from pathlib import Path

PACKET = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/branching_corridor_001")
OUT = PACKET / "raw" / "branching_transport_graph.edgelist"

edges = []

# main carrier corridor
carrier = ["N01","N02","N03","N04","N05","N06","N07","N08","N09","N10"]
for a, b in zip(carrier, carrier[1:]):
    edges.append((a,b))

# reinforced central corridor
edges += [
    ("N03","N05"),
    ("N04","N06"),
    ("N05","N07"),
    ("N06","N08"),
]

# left branch cluster
edges += [
    ("N03","L01"),
    ("L01","L02"),
    ("L02","L03"),
    ("L02","L04"),
    ("L04","L05"),
]

# right branch cluster
edges += [
    ("N07","R01"),
    ("R01","R02"),
    ("R02","R03"),
    ("R02","R04"),
    ("R04","R05"),
    ("R05","R06"),
]

# abandoned / sparse branch
edges += [
    ("N02","A01"),
    ("A01","A02"),
]

# reroute bridge
edges += [
    ("L04","N06"),
    ("R03","N08"),
    ("L05","R01"),
]

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(f"{a} {b}" for a,b in edges), encoding="utf-8")

print("WROTE", OUT.resolve())
print("EDGES", len(edges))
