import random
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/naturalistic_calibration_003/terrains")
BASE.mkdir(parents=True, exist_ok=True)

random.seed(219)

N = 5000
rows = []

motif_a = [
    "alpha weak rise",
    "beta weak fall",
    "alpha weak rise",
    "gamma soft pulse",
]

motif_b = [
    "theta slight drift",
    "lambda slight drift",
    "theta slight drift",
    "delta soft pulse",
]

motif_c = [
    "iota boundary hint",
    "kappa boundary hint",
    "iota boundary hint",
    "mu local flicker",
]

motifs = [motif_a, motif_b, motif_c]

for i in range(1, N + 1):

    line = f"t={i:05d} quiet_field carrier"

    # local pseudo-cadence regions
    if i % 500 in range(40, 160):
        motif = motifs[(i // 500) % len(motifs)]
        item = motif[((i % 500) - 40) // 30]
        line = f"t={i:05d} {item} pseudo_cadence"

    # imperfect echo regions, shifted and reordered
    elif i % 725 in range(220, 340):
        motif = motifs[(i // 725 + 1) % len(motifs)]
        item = motif[::-1][((i % 725) - 220) // 30]
        line = f"t={i:05d} {item} imperfect_echo"

    # false reinforcement, repeated enough to tempt basin formation
    elif i % 1100 in range(540, 680):
        item = random.choice([
            "alpha weak rise",
            "alpha weak rise",
            "theta slight drift",
            "iota boundary hint",
        ])
        line = f"t={i:05d} {item} reinforcement_candidate"

    # divergence / collapse stretches
    elif i % 1400 in range(900, 1180):
        item = random.choice([
            "unmatched shard a",
            "unmatched shard b",
            "unmatched shard c",
            "quiet_field carrier",
        ])
        line = f"t={i:05d} {item} divergence_zone"

    rows.append(line)

out = BASE / "sparse_misleading_structural_v2_5k.log"

with out.open("w", encoding="utf-8") as f:
    for row in rows:
        f.write(row + "\n")

print("WROTE", out.resolve())
