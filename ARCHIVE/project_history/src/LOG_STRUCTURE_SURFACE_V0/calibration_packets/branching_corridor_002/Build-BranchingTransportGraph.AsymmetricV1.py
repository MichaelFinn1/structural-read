from pathlib import Path

PACKET = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/branching_corridor_002")
OUT = PACKET / "raw" / "branching_transport_graph_asymmetric.edgelist"

edges = []

# dominant carrier spine
spine = ["C01","C02","C03","C04","C05","C06","C07","C08","C09","C10","C11","C12"]
for a,b in zip(spine, spine[1:]):
    edges.append((a,b))

# reinforced central carrier
edges += [
    ("C03","C05"), ("C04","C06"), ("C05","C07"),
    ("C06","C08"), ("C07","C09"), ("C08","C10"),
    ("C05","C08"), ("C06","C09")
]

# overloaded hub region
edges += [
    ("C06","H01"), ("C06","H02"), ("C06","H03"), ("C06","H04"),
    ("C07","H02"), ("C07","H03"), ("C07","H05"),
    ("H03","H06"), ("H04","H06")
]

# weak abandoned branch
edges += [
    ("C02","A01"),
    ("A01","A02"),
    ("A02","A03")
]

# viable side branch
edges += [
    ("C09","B01"),
    ("B01","B02"),
    ("B02","B03"),
    ("B03","B04"),
    ("B04","C11")
]

# reroute bridge across disturbed section
edges += [
    ("C04","R01"),
    ("R01","R02"),
    ("R02","C10")
]

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(f"{a} {b}" for a,b in edges), encoding="utf-8")

print("WROTE", OUT.resolve())
print("EDGES", len(edges))
