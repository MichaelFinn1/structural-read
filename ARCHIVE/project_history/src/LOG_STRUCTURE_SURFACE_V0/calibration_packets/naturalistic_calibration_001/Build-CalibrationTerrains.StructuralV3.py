import random
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/naturalistic_calibration_001/terrains_structural_v3")
BASE.mkdir(parents=True, exist_ok=True)

N = 2000
random.seed(44)

def write(name, rows):
    out = BASE / f"{name}_2k.log"
    out.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print("WROTE", out.resolve())

def unique_word(i):
    return f"uniq_{i:04d}_xray_{(i*37)%997}_node"

stable = [
    "STABLE_CARRIER_ALPHA",
    "STABLE_CARRIER_BETA",
    "STABLE_RETURN_PATH",
]

middle = [
    "MIDDLE_SEAM_LEFT",
    "MIDDLE_SEAM_RIGHT",
    "MIDDLE_PULSE_BRIDGE",
    "MIDDLE_GATE_HOLD",
]

residual = [
    "RESIDUE_FLICKER",
    "RESIDUE_MARK",
    "RESIDUE_EDGE",
]

# white: many uniques, low recurrence
white = []
for i in range(1, N + 1):
    if random.random() < 0.12:
        white.append(random.choice(stable))
    elif random.random() < 0.25:
        white.append(random.choice(middle))
    else:
        white.append(f"WHITE_NOISE_{unique_word(i)}")

# brown: slow regimes with adjacent repeated families
brown = []
regime = 0
regimes = ["BROWN_LOW_DRIFT", "BROWN_MID_DRIFT", "BROWN_HIGH_DRIFT", "BROWN_RETURN_DRIFT"]
for i in range(1, N + 1):
    if i % 180 == 0:
        regime = max(0, min(3, regime + random.choice([-1, 1])))
    if random.random() < 0.08:
        brown.append(f"BROWN_RESIDUAL_{unique_word(i)}")
    else:
        brown.append(regimes[regime])

# periodic: chamber recurrence
periodic = []
cycle = ["PERIOD_A_OPEN", "PERIOD_B_HOLD", "PERIOD_C_CROSS", "PERIOD_B_HOLD"]
for i in range(1, N + 1):
    periodic.append(cycle[(i // 35) % len(cycle)])

# sparse pulse: stable carrier with rare pulse bursts
pulse = []
for i in range(1, N + 1):
    if i % 340 in range(60, 88):
        pulse.append(random.choice(["PULSE_RISE", "PULSE_PEAK", "PULSE_FALL"]))
    elif i % 340 in range(88, 105):
        pulse.append(f"PULSE_RESIDUE_{unique_word(i)}")
    else:
        pulse.append("SPARSE_STABLE_FIELD")

# mixed: stable background plus noisy recomposition zones
mixed = []
for i in range(1, N + 1):
    if i % 420 in range(50, 140):
        if random.random() < 0.55:
            mixed.append(random.choice(middle))
        else:
            mixed.append(f"MIXED_BURST_{unique_word(i)}")
    else:
        mixed.append(random.choice(stable))

# low-frequency drift: broad blocks with edge flicker
drift = []
blocks = ["DRIFT_FIELD_LOW", "DRIFT_FIELD_MID", "DRIFT_FIELD_HIGH", "DRIFT_FIELD_RETURN"]
for i in range(1, N + 1):
    block = blocks[(i // 250) % len(blocks)]
    if i % 250 in range(230, 250):
        drift.append(random.choice(["DRIFT_EDGE_THIN", "DRIFT_EDGE_SHIFT", f"DRIFT_EDGE_{unique_word(i)}"]))
    else:
        drift.append(block)

write("white_noise_structural_v3", white)
write("brown_noise_structural_v3", brown)
write("periodic_signal_structural_v3", periodic)
write("sparse_pulse_structural_v3", pulse)
write("mixed_pulse_noise_structural_v3", mixed)
write("low_frequency_drift_structural_v3", drift)
