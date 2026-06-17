import random
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/naturalistic_calibration_003/terrains")
BASE.mkdir(parents=True, exist_ok=True)

random.seed(117)

N = 5000

rows = []

motifs = [
    ["alpha weak rise", "beta weak fall"],
    ["gamma soft pulse", "delta soft pulse"],
    ["theta slight drift", "lambda slight drift"]
]

for i in range(1, N + 1):

    line = f"t={i:05d} quiet_field"

    # weak local motif regions
    if i % 420 in range(40, 90):

        motif = random.choice(motifs)

        line = (
            f"t={i:05d} "
            f"{motif[0]} "
            f"{motif[1]} "
            f"local_echo"
        )

    # imperfect recurrence later
    if i % 760 in range(210, 255):

        motif = random.choice(motifs)

        line = (
            f"t={i:05d} "
            f"{motif[1]} "
            f"{motif[0]} "
            f"partial_return"
        )

    # sparse misleading reinforcement
    if i % 1100 in range(500, 540):

        line = (
            f"t={i:05d} "
            f"{random.choice(['alpha weak rise','gamma soft pulse'])} "
            f"reinforcement_candidate"
        )

    # collapse regions
    if i % 1500 in range(900, 1250):

        line = f"t={i:05d} sparse_flat_field"

    rows.append(line)

out = BASE / "sparse_misleading_structural_v1_5k.log"

with out.open("w", encoding="utf-8") as f:
    for row in rows:
        f.write(row + "\n")

print("WROTE", out.resolve())
