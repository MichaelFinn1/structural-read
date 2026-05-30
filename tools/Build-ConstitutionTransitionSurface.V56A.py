import argparse
import csv
from pathlib import Path
from collections import defaultdict

def fnum(x):
    try:
        return float(x)
    except Exception:
        return 0.0

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--windows-csv", required=True)
    p.add_argument("--out-csv", required=True)
    args = p.parse_args()

    rows = list(csv.DictReader(Path(args.windows_csv).open("r", encoding="utf-8")))
    by_size = defaultdict(list)

    for r in rows:
        by_size[int(r["window_size"])].append(r)

    sizes = sorted(by_size.keys())

    out_rows = []

    for a, b in zip(sizes, sizes[1:]):
        ra = by_size[a]
        rb = by_size[b]

        avg_a = {
            "stable": sum(fnum(x["stable_share"]) for x in ra) / max(1, len(ra)),
            "middle": sum(fnum(x["middle_share"]) for x in ra) / max(1, len(ra)),
            "residual": sum(fnum(x["residual_share"]) for x in ra) / max(1, len(ra)),
        }

        avg_b = {
            "stable": sum(fnum(x["stable_share"]) for x in rb) / max(1, len(rb)),
            "middle": sum(fnum(x["middle_share"]) for x in rb) / max(1, len(rb)),
            "residual": sum(fnum(x["residual_share"]) for x in rb) / max(1, len(rb)),
        }

        d_stable = avg_b["stable"] - avg_a["stable"]
        d_middle = avg_b["middle"] - avg_a["middle"]
        d_residual = avg_b["residual"] - avg_a["residual"]

        magnitude = abs(d_stable) + abs(d_middle) + abs(d_residual)

        out_rows.append({
            "constitution_from": a,
            "constitution_to": b,
            "stable_from": avg_a["stable"],
            "stable_to": avg_b["stable"],
            "middle_from": avg_a["middle"],
            "middle_to": avg_b["middle"],
            "residual_from": avg_a["residual"],
            "residual_to": avg_b["residual"],
            "delta_stable": d_stable,
            "delta_middle": d_middle,
            "delta_residual": d_residual,
            "deformation_magnitude": magnitude
        })

    out = Path(args.out_csv)
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)

    print("WROTE", out.resolve())

if __name__ == "__main__":
    main()
