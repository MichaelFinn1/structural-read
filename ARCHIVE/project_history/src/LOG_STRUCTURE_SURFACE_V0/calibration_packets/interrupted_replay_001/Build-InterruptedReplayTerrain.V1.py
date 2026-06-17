from pathlib import Path
import random

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/interrupted_replay_001/terrains")
BASE.mkdir(parents=True, exist_ok=True)

random.seed(421)

N = 7000
rows = []

cycle_a = [
    "alpha replay carrier",
    "beta replay carrier",
    "gamma replay carrier",
    "delta replay carrier",
]

cycle_b = [
    "alpha replay carrier",
    "beta replay carrier",
    "epsilon altered carrier",
    "delta replay carrier",
]

for i in range(1, N + 1):

    # Phase 1: coherent replay
    if i <= 1800:
        item = cycle_a[(i // 40) % len(cycle_a)]
        line = f"t={i:05d} {item} replay_phase_A"

    # Phase 2: interruption gap / quiet discontinuity
    elif i <= 2600:
        if i % 90 < 15:
            line = f"t={i:05d} gap_echo weak_return"
        else:
            line = f"t={i:05d} interruption_gap quiet"

    # Phase 3: partial restart, similar but altered
    elif i <= 4300:
        item = cycle_b[(i // 45) % len(cycle_b)]
        line = f"t={i:05d} {item} replay_phase_B_partial_restart"

    # Phase 4: unstable re-entry / mixed old-new echoes
    elif i <= 5600:
        if i % 160 < 70:
            item = random.choice(cycle_a + cycle_b)
            line = f"t={i:05d} {item} mixed_reentry"
        else:
            line = f"t={i:05d} quiet_reentry_field"

    # Phase 5: broad recomposed carrier
    else:
        item = random.choice([
            "alpha replay carrier",
            "delta replay carrier",
            "lambda recomposed carrier",
        ])
        line = f"t={i:05d} {item} recomposed_tail"

    rows.append(line)

out = BASE / "interrupted_replay_v1_7k.log"

with out.open("w", encoding="utf-8") as f:
    for row in rows:
        f.write(row + "\n")

print("WROTE", out.resolve())
