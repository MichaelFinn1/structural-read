import argparse
import csv
from pathlib import Path

def fnum(x):
    try:
        return float(x)
    except Exception:
        return 0.0

def inum(x):
    try:
        return int(float(x))
    except Exception:
        return 0

def read_rows(path):
    rows = list(csv.DictReader(Path(path).open("r", encoding="utf-8")))
    for r in rows:
        r["_from"] = inum(r["constitution_from"])
        r["_to"] = inum(r["constitution_to"])
        r["_mag"] = fnum(r["deformation_magnitude"])
    return rows

def build_corridors(top_rows):
    ordered = sorted(top_rows, key=lambda r: (r["_from"], r["_to"]))

    corridors = []
    current = []

    for r in ordered:
        if not current:
            current = [r]
            continue

        prev = current[-1]

        if prev["_to"] == r["_from"]:
            current.append(r)
        else:
            corridors.append(current)
            current = [r]

    if current:
        corridors.append(current)

    return corridors

def fmt(x):
    return f"{x:.6f}"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--transition-csv", required=True)
    p.add_argument("--label", default="dataset")
    p.add_argument("--top-k", type=int, default=3)
    args = p.parse_args()

    rows = read_rows(args.transition_csv)

    if not rows:
        raise SystemExit("No rows found")

    ranked = sorted(rows, key=lambda r: r["_mag"], reverse=True)
    top = ranked[:args.top_k]
    peak = ranked[0]
    corridors = build_corridors(top)

    print("")
    print("DATASET")
    print(args.label)
    print("")

    print("PEAK HINGE")
    print(f"{peak['_from']} -> {peak['_to']} deformation={fmt(peak['_mag'])}")
    print("")

    print(f"TOP {args.top_k} HINGES")
    for i, r in enumerate(top, start=1):
        print(f"{i}. {r['_from']} -> {r['_to']} deformation={fmt(r['_mag'])}")
    print("")

    print("HINGE CORRIDORS")
    for i, corridor in enumerate(corridors, start=1):
        start = corridor[0]["_from"]
        end = corridor[-1]["_to"]
        total = sum(r["_mag"] for r in corridor)

        if len(corridor) == 1:
            print(
                f"Isolated {i}: {start} -> {end} "
                f"transitions=1 total_deformation={fmt(total)}"
            )
        else:
            print(
                f"Corridor {i}: {start} -> {end} "
                f"transitions={len(corridor)} total_deformation={fmt(total)}"
            )

            chain = " | ".join(
                f"{r['_from']}->{r['_to']}:{fmt(r['_mag'])}"
                for r in corridor
            )
            print(f"  {chain}")

    print("")

if __name__ == "__main__":
    main()
