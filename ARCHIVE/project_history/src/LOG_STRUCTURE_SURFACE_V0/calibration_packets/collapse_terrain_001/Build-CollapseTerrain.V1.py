import random
from pathlib import Path

OUT = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/collapse_terrain_001/terrains/collapse_terrain_v1_10k.log")

random.seed(44)

lines = []

stable_tokens = [
    "alpha_sync",
    "alpha_sync",
    "alpha_sync",
    "bridge_hold",
    "bridge_hold",
    "delta_flow"
]

collapse_tokens = [
    "noise_a",
    "noise_b",
    "noise_c",
    "noise_d",
    "scatter_x",
    "scatter_y",
    "scatter_z"
]

reentry_tokens = [
    "alpha_sync",
    "partial_return",
    "bridge_hold",
    "drift_return"
]

# Phase 1
for i in range(2000):
    lines.append(random.choice(stable_tokens))

# Phase 2
for i in range(1500):
    if random.random() < 0.7:
        lines.append(random.choice(collapse_tokens))
    else:
        lines.append(random.choice(stable_tokens))

# Phase 3
for i in range(2000):
    lines.append(random.choice(collapse_tokens))

# Phase 4
for i in range(1500):
    if random.random() < 0.25:
        lines.append(random.choice(reentry_tokens))
    else:
        lines.append(random.choice(collapse_tokens))

# Phase 5
for i in range(3000):
    lines.append(random.choice(collapse_tokens))

OUT.write_text("\n".join(lines), encoding="utf-8")

print("WROTE", OUT.resolve())
print("LINES", len(lines))
