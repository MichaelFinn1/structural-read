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

def fmt(x):
    return f"{x:.6f}"

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

        if current[-1]["_to"] == r["_from"]:
            current.append(r)
        else:
            corridors.append(current)
            current = [r]

    if current:
        corridors.append(current)

    return corridors

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--transition-csv", required=True)
    p.add_argument("--out-csv", required=True)
    p.add_argument("--dataset-label", default="dataset")
    p.add_argument("--source-ladder", default="")
    p.add_argument("--top-k", type=int, default=3)
    args = p.parse_args()

    rows = read_rows(args.transition_csv)
    if not rows:
        raise SystemExit("No transition rows found")

    ranked = sorted(rows, key=lambda r: r["_mag"], reverse=True)
    top = ranked[:args.top_k]
    peak = ranked[0]
    corridors = build_corridors(top)

    out_rows = []

    out_rows.append({
        "waypoint_id": "peak_001",
        "waypoint_type": "peak",
        "dataset_label": args.dataset_label,
        "from_constitution": peak["_from"],
        "to_constitution": peak["_to"],
        "transition_count": 1,
        "total_deformation": fmt(peak["_mag"]),
        "peak_deformation": fmt(peak["_mag"]),
        "rank": 1,
        "source_ladder": args.source_ladder,
        "transition_chain": f"{peak['_from']}->{peak['_to']}:{fmt(peak['_mag'])}",
        "label": f"Peak hinge {peak['_from']}->{peak['_to']}"
    })

    for i, corridor in enumerate(corridors, start=1):
        start = corridor[0]["_from"]
        end = corridor[-1]["_to"]
        total = sum(r["_mag"] for r in corridor)
        peak_mag = max(r["_mag"] for r in corridor)
        chain = " | ".join(
            f"{r['_from']}->{r['_to']}:{fmt(r['_mag'])}"
            for r in corridor
        )

        if len(corridor) == 1:
            wtype = "isolated"
            label = f"Isolated hinge {start}->{end}"
        else:
            wtype = "corridor"
            label = f"Hinge corridor {start}->{end}"

        out_rows.append({
            "waypoint_id": f"{wtype}_{i:03d}",
            "waypoint_type": wtype,
            "dataset_label": args.dataset_label,
            "from_constitution": start,
            "to_constitution": end,
            "transition_count": len(corridor),
            "total_deformation": fmt(total),
            "peak_deformation": fmt(peak_mag),
            "rank": i,
            "source_ladder": args.source_ladder,
            "transition_chain": chain,
            "label": label
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
