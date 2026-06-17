import csv
from pathlib import Path

PACKET = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/lynx_hare_cycle_001")
SRC = PACKET / "measured" / "lynx_pulse_comparative_surface_v1.csv"
OUT = PACKET / "measured" / "lynx_pulse_sequence_surface_v1.csv"

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))

def classify(prev, cur):
    if prev is None:
        return "sequence_start"

    if cur["pulse_shape"] in ["unfinished_recovery"]:
        return "open_continuation"

    if cur["recovery_depth"] != prev["recovery_depth"]:
        return "recovery_shift"

    if cur["amplitude_class"] != prev["amplitude_class"]:
        return "amplitude_shift"

    if cur["pulse_shape"] != prev["pulse_shape"]:
        return "shape_shift"

    return "stable_repeat"

out = []

prev = None
for r in rows:
    transition = classify(prev, r)

    out.append({
        "cycle_id": r["cycle_id"],
        "previous_shape": "" if prev is None else prev["pulse_shape"],
        "current_shape": r["pulse_shape"],
        "previous_amplitude": "" if prev is None else prev["amplitude_class"],
        "current_amplitude": r["amplitude_class"],
        "previous_recovery": "" if prev is None else prev["recovery_depth"],
        "current_recovery": r["recovery_depth"],
        "transition_class": transition,
        "boundary_note": "pulse_to_pulse_observer_relation_not_ecological_cause"
    })

    prev = r

with OUT.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
    w.writeheader()
    w.writerows(out)

print("WROTE", OUT.resolve())
print("ROWS", len(out))
