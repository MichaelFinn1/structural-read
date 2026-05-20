import csv
import argparse
from pathlib import Path
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument("--source", required=True)
parser.add_argument("--out", required=True)
parser.add_argument("--terrain", required=True)
args = parser.parse_args()

src = Path(args.source)
out = Path(args.out)
out.parent.mkdir(parents=True, exist_ok=True)

rows = list(csv.DictReader(src.open("r", encoding="utf-8")))

for r in rows:
    r["window_size"] = int(float(r["window_size"]))
    r["line_start"] = int(float(r["line_start"]))
    r["line_end"] = int(float(r["line_end"]))
    r["stable_share"] = float(r["stable_share"])
    r["middle_share"] = float(r["middle_share"])
    r["residual_share"] = float(r["residual_share"])

def dominant_posture(r):
    vals = {
        "stable": r["stable_share"],
        "middle": r["middle_share"],
        "residual": r["residual_share"],
    }
    return max(vals, key=vals.get)

def continuity_strength(r):
    return max(r["stable_share"], r["middle_share"], r["residual_share"])

def region_key(r, region_width=1000):
    mid = (r["line_start"] + r["line_end"]) / 2
    return int((mid - 1) // region_width) + 1

by_ws_region = defaultdict(list)

for r in rows:
    key = (r["window_size"], region_key(r))
    by_ws_region[key].append(r)

summary = []

for (ws, region), local in sorted(by_ws_region.items()):
    stable = sum(r["stable_share"] for r in local) / len(local)
    middle = sum(r["middle_share"] for r in local) / len(local)
    residual = sum(r["residual_share"] for r in local) / len(local)

    fake = {
        "stable_share": stable,
        "middle_share": middle,
        "residual_share": residual,
    }

    summary.append({
        "terrain": args.terrain,
        "window_size": ws,
        "local_region": f"R{region:03d}",
        "line_start": min(r["line_start"] for r in local),
        "line_end": max(r["line_end"] for r in local),
        "dominant_posture": dominant_posture(fake),
        "continuity_strength": round(continuity_strength(fake), 4),
        "stable_share": round(stable, 4),
        "middle_share": round(middle, 4),
        "residual_share": round(residual, 4),
    })

prior_by_region = {}
out_rows = []

for s in summary:
    region = s["local_region"]
    prior = prior_by_region.get(region)

    if prior is None:
        transition_pressure = "initial"
        survival_class = "initial"
    else:
        delta = s["continuity_strength"] - prior["continuity_strength"]

        if s["dominant_posture"] != prior["dominant_posture"]:
            transition_pressure = "posture_changes"
        elif abs(delta) < 0.05:
            transition_pressure = "posture_holds"
        elif delta > 0:
            transition_pressure = "strengthens"
        else:
            transition_pressure = "weakens"

        if transition_pressure == "posture_holds":
            survival_class = "holds"
        elif transition_pressure == "strengthens":
            survival_class = "recomposes"
        elif transition_pressure == "weakens":
            survival_class = "weakens"
        elif transition_pressure == "posture_changes":
            if s["continuity_strength"] < 0.55:
                survival_class = "dissolves"
            else:
                survival_class = "reappears_or_recolors"
        else:
            survival_class = "ambiguous"

    row = dict(s)
    row["transition_pressure"] = transition_pressure
    row["survival_class"] = survival_class
    row["boundary_note"] = "constitution_relative_observer_surface_no_identity_claim"

    out_rows.append(row)
    prior_by_region[region] = s

fieldnames = [
    "terrain",
    "window_size",
    "local_region",
    "line_start",
    "line_end",
    "dominant_posture",
    "continuity_strength",
    "stable_share",
    "middle_share",
    "residual_share",
    "transition_pressure",
    "survival_class",
    "boundary_note",
]

with out.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(out_rows)

print("WROTE", out.resolve())
