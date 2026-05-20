from pathlib import Path
import random

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/pseudo_periodic_drift_001/terrains")
BASE.mkdir(parents=True, exist_ok=True)

random.seed(311)
N = 6000
rows = []

motif = [
    "alpha cadence one",
    "beta cadence two",
    "gamma cadence three",
    "delta cadence four",
]

phase_offset = 0

for i in range(1, N + 1):

    # slow phase drift every 900 lines
    if i % 900 == 1 and i > 1:
        phase_offset += 1

    # pseudo-periodic chamber
    if i % 120 < 80:
        idx = ((i // 20) + phase_offset) % len(motif)
        line = f"t={i:05d} {motif[idx]} pseudo_periodic"

    # local cadence interruption
    elif i % 700 in range(500, 570):
        idx = random.choice([0, 1, 2, 3])
        line = f"t={i:05d} {motif[idx]} cadence_interruption"

    # quiet carrier
    else:
        line = f"t={i:05d} quiet_carrier"

    # delayed echo with slight phase mismatch
    if i % 1300 in range(900, 980):
        idx = ((i // 25) + phase_offset + 2) % len(motif)
        line = f"t={i:05d} {motif[idx]} delayed_phase_echo"

    rows.append(line)

out = BASE / "pseudo_periodic_drift_v1_6k.log"

with out.open("w", encoding="utf-8") as f:
    for row in rows:
        f.write(row + "\n")

print("WROTE", out.resolve())
