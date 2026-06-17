import random
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/naturalistic_calibration_001/terrains")
BASE.mkdir(parents=True, exist_ok=True)

N = 2000
random.seed(17)

def write(name, values):
    out = BASE / f"{name}_2k.log"
    with out.open("w", encoding="utf-8") as f:
        for i, v in enumerate(values, start=1):
            bucket = int(max(0, min(9, v)))
            f.write(f"tick={i:04d} terrain={name} value_bucket={bucket} signal={'#' * bucket}\n")
    print("WROTE", out.resolve())

# white noise
white = [random.randint(0, 9) for _ in range(N)]

# brown-ish random walk
x = 5
brown = []
for _ in range(N):
    x += random.choice([-1, 0, 1])
    x = max(0, min(9, x))
    brown.append(x)

# periodic
periodic = [int(5 + 4 * ((i % 80) / 80)) if (i % 80) < 40 else int(9 - 4 * (((i % 80)-40) / 40)) for i in range(N)]

# sparse pulse
pulse = [0 for _ in range(N)]
for start in range(120, N, 330):
    for j in range(start, min(start + 24, N)):
        pulse[j] = 8

# mixed pulse + noise
mixed = []
for i in range(N):
    base = random.randint(1, 3)
    if i % 420 in range(40, 90):
        base += 5
    mixed.append(min(9, base))

# low-frequency drift
drift = []
for i in range(N):
    phase = (i // 250) % 4
    if phase == 0:
        v = 2
    elif phase == 1:
        v = 5
    elif phase == 2:
        v = 8
    else:
        v = 4
    if random.random() < 0.08:
        v += random.choice([-1, 1])
    drift.append(max(0, min(9, v)))

write("white_noise", white)
write("brown_noise", brown)
write("periodic_signal", periodic)
write("sparse_pulse", pulse)
write("mixed_pulse_noise", mixed)
write("low_frequency_drift", drift)
