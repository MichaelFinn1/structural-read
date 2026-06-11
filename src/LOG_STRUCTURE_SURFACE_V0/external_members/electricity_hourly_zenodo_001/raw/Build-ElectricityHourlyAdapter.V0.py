import csv
from pathlib import Path
import os

in_csv = Path(os.environ["IN_CSV"])
out_log = Path(os.environ["OUT_LOG"])

rows = []

with in_csv.open("r", encoding="utf-8") as f:
    r = csv.DictReader(f)
    for row in r:
        rows.append((int(row["hour_index"]), float(row["aggregate_load"])))

if len(rows) < 2:
    raise SystemExit("Not enough rows.")

loads = [v for _, v in rows]

lo = min(loads)
hi = max(loads)

q1 = sorted(loads)[len(loads) // 3]
q2 = sorted(loads)[(len(loads) * 2) // 3]

deltas = []
for i in range(1, len(loads)):
    deltas.append(loads[i] - loads[i - 1])

abs_deltas = sorted(abs(x) for x in deltas)
d1 = abs_deltas[len(abs_deltas) // 3]
d2 = abs_deltas[(len(abs_deltas) * 2) // 3]

with out_log.open("w", encoding="utf-8") as f:
    prev = None

    for hour_index, load in rows:
        if load <= q1:
            load_bucket = "load_low"
        elif load <= q2:
            load_bucket = "load_mid"
        else:
            load_bucket = "load_high"

        if prev is None:
            direction = "delta_start"
            magnitude = "change_start"
        else:
            delta = load - prev
            if delta < 0:
                direction = "delta_down"
            elif delta > 0:
                direction = "delta_up"
            else:
                direction = "delta_flat"

            ad = abs(delta)
            if ad <= d1:
                magnitude = "change_small"
            elif ad <= d2:
                magnitude = "change_mid"
            else:
                magnitude = "change_large"

        f.write(
            f"hour_{hour_index:06d} "
            f"{load_bucket} "
            f"{direction} "
            f"{magnitude}\n"
        )

        prev = load

print("input_rows", len(rows))
print("load_min", lo)
print("load_max", hi)
print("load_q1", q1)
print("load_q2", q2)
print("delta_abs_q1", d1)
print("delta_abs_q2", d2)
print("adapter_log", out_log)
