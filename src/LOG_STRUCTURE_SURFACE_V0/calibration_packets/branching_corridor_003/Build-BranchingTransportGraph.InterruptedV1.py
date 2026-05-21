from pathlib import Path

PACKET = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/branching_corridor_003")
OUT = PACKET / "raw" / "branching_transport_graph_interrupted.edgelist"

edges = []

# pre-interruption left carrier
edges += [
    ("C01","C02"), ("C02","C03"), ("C03","C04"), ("C04","C05"),
    ("C03","C05"), ("C04","C06")
]

# broken / missing central corridor is represented by absence of C06-C07 and C07-C08

# overload near break
edges += [
    ("C05","H01"), ("C05","H02"), ("C05","H03"),
    ("C06","H02"), ("C06","H03"), ("C06","H04"),
    ("H03","H05")
]

# partial reroute attempt
edges += [
    ("C04","R01"), ("R01","R02"), ("R02","R03"), ("R03","C09")
]

# post-interruption right carrier
edges += [
    ("C09","C10"), ("C10","C11"), ("C11","C12"),
    ("C09","C11"), ("C10","C12")
]

# abandoned viable-looking branch
edges += [
    ("C03","A01"), ("A01","A02"), ("A02","A03"), ("A03","A04")
]

# incomplete recovery bridge
edges += [
    ("A04","R02"),
    ("H04","R01")
]

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(f"{a} {b}" for a,b in edges), encoding="utf-8")

print("WROTE", OUT.resolve())
print("EDGES", len(edges))
