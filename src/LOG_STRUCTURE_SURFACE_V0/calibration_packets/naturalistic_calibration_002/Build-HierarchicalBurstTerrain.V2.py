import random
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/naturalistic_calibration_002/terrains")
BASE.mkdir(parents=True, exist_ok=True)

N = 4000
random.seed(91)

rows = []

stable_carriers = [
    "CARRIER_A_STABLE",
    "CARRIER_B_STABLE",
]

middle_forms = [
    "MID_SEAM_ALPHA",
    "MID_SEAM_BETA",
    "MID_RETURN_GAMMA",
    "MID_HOLD_DELTA",
]

for i in range(1, N + 1):

    # broad stable carrier regimes
    carrier = stable_carriers[(i // 700) % 2]

    # nested burst zone: mostly unique residuals, with occasional middle seams
    if i % 220 in range(40, 82):
        if random.random() < 0.75:
            # unique-ish residual form: should resist stable admission
            line = f"t={i:04d} RESIDUAL_BURST_{i:04d}_{random.randint(1000,9999)} burst_zone"
        else:
            # repeated enough to become middle-ish, not fully carrier-like
            line = f"t={i:04d} {random.choice(middle_forms)} burst_seam"

    # recomposition pockets: repeated middle families
    elif i % 950 in range(480, 620):
        line = f"t={i:04d} {random.choice(middle_forms)} recomposition_pocket"

    # low-rate residual disturbances outside bursts
    elif random.random() < 0.035:
        line = f"t={i:04d} RESIDUAL_EDGE_{i:04d}_{random.randint(1000,9999)} edge_disturbance"

    # stable carrier field
    else:
        line = f"t={i:04d} {carrier} carrier_field"

    rows.append(line)

out = BASE / "hierarchical_burst_structural_v2_4k.log"
out.write_text("\n".join(rows) + "\n", encoding="utf-8")
print("WROTE", out.resolve())
