import random
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/naturalistic_calibration_002/terrains")
BASE.mkdir(parents=True, exist_ok=True)

N = 4000
random.seed(71)

def write(name, rows):
    out = BASE / f"{name}_4k.log"
    with out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(row + "\n")
    print("WROTE", out.resolve())

rows = []

major_cycle = [
    "delta carrier stable",
    "delta carrier stable",
    "lambda return path",
    "theta drift high"
]

minor_cycle = [
    "epsilon pulse rise",
    "zeta pulse fall",
    "mu local flicker"
]

for i in range(1, N + 1):

    major = major_cycle[(i // 500) % len(major_cycle)]

    # broad carrier regime
    if i % 700 in range(120, 420):
        carrier = major
    else:
        carrier = "eta drift low"

    # nested burst ecology
    if i % 180 in range(30, 65):

        local = random.choice(minor_cycle)

        # occasional seam disturbance
        if i % 540 in range(40, 90):
            local = random.choice([
                "iota boundary thin",
                "gamma seam shift",
                local
            ])

        line = f"t={i:04d} {carrier} {local} nested_burst"

    # sparse recomposition pocket
    elif i % 950 in range(500, 620):

        line = (
            f"t={i:04d} "
            f"{random.choice(['beta gate hold','gamma seam shift'])} "
            f"recomposition_pocket"
        )

    # stable carrier field
    else:

        line = f"t={i:04d} {carrier} carrier_field"

    rows.append(line)

write("hierarchical_burst_structural_v1", rows)
