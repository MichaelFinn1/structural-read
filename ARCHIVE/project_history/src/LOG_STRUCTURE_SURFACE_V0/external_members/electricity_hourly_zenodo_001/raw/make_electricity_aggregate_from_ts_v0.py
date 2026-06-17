from pathlib import Path
import csv
import os

ts_path = Path(os.environ["TS_PATH"])
out_csv = Path(os.environ["OUT_CSV"])
out_log = Path(os.environ["OUT_LOG"])

series = []

with ts_path.open("r", encoding="utf-8", errors="replace") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        if line.startswith("@"):
            continue

        parts = line.split(":")
        values_raw = parts[-1]

        vals = []
        for x in values_raw.split(","):
            x = x.strip()
            if x in ("?", "", "NaN", "nan"):
                vals.append(0.0)
            else:
                vals.append(float(x))

        if vals:
            series.append(vals)

if not series:
    raise SystemExit("No series parsed from TS.")

n = min(len(s) for s in series)
agg = []

for i in range(n):
    agg.append(sum(s[i] for s in series))

out_csv.parent.mkdir(parents=True, exist_ok=True)

with out_csv.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["hour_index", "aggregate_load"])
    for i, val in enumerate(agg):
        w.writerow([i, f"{val:.6f}"])

with out_log.open("w", encoding="utf-8") as f:
    for i, val in enumerate(agg):
        f.write(f"hour_{i:06d} aggregate_load {val:.6f}\n")

print("ts", ts_path)
print("parsed_series", len(series))
print("hour_count", n)
print("csv", out_csv)
print("log", out_log)
print("min", min(agg))
print("max", max(agg))
print("mean", sum(agg) / len(agg))
