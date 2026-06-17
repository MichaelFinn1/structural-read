import random
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/naturalistic_calibration_001/terrains_structural_v2")
BASE.mkdir(parents=True, exist_ok=True)

N = 2000
random.seed(31)

def write(name, rows):
    out = BASE / f"{name}_2k.log"
    with out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(row + "\n")
    print("WROTE", out.resolve())

families = [
    "alpha gate open",
    "beta gate hold",
    "gamma seam shift",
    "delta carrier stable",
    "epsilon pulse rise",
    "zeta pulse fall",
    "eta drift low",
    "theta drift high",
    "iota boundary thin",
    "kappa residue mark",
    "lambda return path",
    "mu local flicker",
]

# white noise: high family variation
white = []
for i in range(1, N + 1):
    fam = random.choice(families)
    white.append(f"t={i:04d} {fam} token={random.randint(1,999)}")

# brown noise: slow family drift
brown = []
idx = 3
for i in range(1, N + 1):
    if random.random() < 0.08:
        idx += random.choice([-1, 0, 1])
        idx = max(0, min(len(families)-1, idx))
    brown.append(f"t={i:04d} {families[idx]} drift_band={idx}")

# periodic: repeating chambers
periodic = []
cycle = ["alpha gate open", "beta gate hold", "gamma seam shift", "beta gate hold"]
for i in range(1, N + 1):
    fam = cycle[(i // 40) % len(cycle)]
    periodic.append(f"t={i:04d} {fam} phase={(i//40)%4}")

# sparse pulse: stable desert with pulse intrusions
pulse = []
for i in range(1, N + 1):
    if i % 330 in range(40, 72):
        fam = random.choice(["epsilon pulse rise", "zeta pulse fall", "kappa residue mark"])
    else:
        fam = "delta carrier stable"
    pulse.append(f"t={i:04d} {fam} sparse_field")

# mixed pulse noise: carrier plus noisy bursts
mixed = []
for i in range(1, N + 1):
    if i % 420 in range(50, 120):
        fam = random.choice(families)
    else:
        fam = random.choice(["delta carrier stable", "beta gate hold", "lambda return path"])
    mixed.append(f"t={i:04d} {fam} mixed_context")

# low-frequency drift: large regimes
drift = []
regimes = [
    "eta drift low",
    "delta carrier stable",
    "theta drift high",
    "lambda return path",
]
for i in range(1, N + 1):
    fam = regimes[(i // 250) % len(regimes)]
    if random.random() < 0.06:
        fam = random.choice([fam, "iota boundary thin", "mu local flicker"])
    drift.append(f"t={i:04d} {fam} regime={(i//250)%4}")

write("white_noise_structural", white)
write("brown_noise_structural", brown)
write("periodic_signal_structural", periodic)
write("sparse_pulse_structural", pulse)
write("mixed_pulse_noise_structural", mixed)
write("low_frequency_drift_structural", drift)
