from pathlib import Path
import csv
import os
import sys

ts_path = Path(os.environ["TS_PATH"])
out_csv = Path(os.environ["OUT_CSV"])
out_log = Path(os.environ["OUT_LOG"])

print("reading", ts_path)

series = []
bad_lines = []

with ts_path.open("r", encoding="utf-8", errors="replace") as f:
    for line_no, line in enumerate(f, start=1):
        raw = line.rstrip("\n")
        line = raw.strip()

        if not line:
            continue

        if line.startswith("@"):
            continue

        if ":" in line:
            values_raw = line.split(":")[-1]
        else:
            values_raw = line

        vals = []
        ok = True

        for x in values_raw.split(","):
            x = x.strip()

            if x in ("?", "", "NaN", "nan"):
                vals.append(0.0)
            else:
                try:
                    vals.append(float(x))
                except Exception:
                    ok = False
                    bad_lines.append((line_no, raw[:200]))
                    break

        if ok and vals:
            series.append(vals)

print("parsed_series", len(series))
print("bad_lines", len(bad_lines))

if bad_lines:
    print("FIRST BAD LINES")
    for item in bad_lines[:5]:
        print(item[0], item[1])

if not series:
    raise SystemExit("No series parsed from TS.")

n = min(len(s) for s in series)
print("min_series_length", n)
print("max_series_length", max(len(s) for s in series))

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

print("hour_count", n)
print("csv", out_csv)
print("log", out_log)
print("min", min(agg))
print("max", max(agg))
print("mean", sum(agg) / len(agg))
