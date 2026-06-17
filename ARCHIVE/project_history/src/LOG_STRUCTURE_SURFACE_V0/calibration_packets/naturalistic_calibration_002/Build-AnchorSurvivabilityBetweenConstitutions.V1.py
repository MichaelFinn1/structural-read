import csv
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/naturalistic_calibration_002")
MEASURED = BASE / "measured_hierarchical_burst_structural_v2_dense_v1"
SRC = MEASURED / "residual_band_sequence_v1.csv"
OUT = MEASURED / "anchor_survivability_between_constitutions_v1.csv"

WINDOWS = [125,150,175,200,250,300,350,400,500,600,700,800,900,1000]
ANCHOR_TOLERANCE = 40

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))

for r in rows:
    r["window_size"] = int(r["window_size"])
    r["band_order"] = int(r["band_order"])
    r["band_center"] = float(r["band_center"])
    r["band_width"] = int(r["band_width"])
    r["gap_from_previous"] = None if r["gap_from_previous"] == "" else int(r["gap_from_previous"])

by_window = {}
for r in rows:
    by_window.setdefault(r["window_size"], []).append(r)

for ws in by_window:
    by_window[ws].sort(key=lambda r: r["band_center"])

out_rows = []

for a,b in zip(WINDOWS, WINDOWS[1:]):
    if a not in by_window or b not in by_window:
        continue

    prior = by_window[a]
    nxt = by_window[b]

    used_next = set()

    for p in prior:
        candidates = []
        for j,n in enumerate(nxt):
            if j in used_next:
                continue
            dist = abs(n["band_center"] - p["band_center"])
            candidates.append((dist,j,n))

        if not candidates:
            continue

        dist,j,n = sorted(candidates, key=lambda x: x[0])[0]

        if dist <= ANCHOR_TOLERANCE:
            relation = "anchor_holds"
            used_next.add(j)
        elif dist <= 125:
            relation = "near_reposition"
        else:
            relation = "reconstitutes_elsewhere"

        out_rows.append({
            "terrain": "hierarchical_burst_structural_v2",
            "from_window": a,
            "to_window": b,
            "from_band": p["band_id"],
            "to_band": n["band_id"],
            "from_center": p["band_center"],
            "to_center": n["band_center"],
            "center_delta": round(n["band_center"] - p["band_center"], 2),
            "abs_center_delta": round(dist, 2),
            "from_width": p["band_width"],
            "to_width": n["band_width"],
            "width_delta": n["band_width"] - p["band_width"],
            "relation": relation,
            "boundary_note": "positional_anchor_not_identity",
        })

fieldnames = [
    "terrain",
    "from_window",
    "to_window",
    "from_band",
    "to_band",
    "from_center",
    "to_center",
    "center_delta",
    "abs_center_delta",
    "from_width",
    "to_width",
    "width_delta",
    "relation",
    "boundary_note",
]

with OUT.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(out_rows)

print("WROTE", OUT.resolve())
