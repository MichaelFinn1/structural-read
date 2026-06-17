import csv
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/naturalistic_calibration_002")
MEASURED = BASE / "measured_hierarchical_burst_structural_v2_dense_v1"

SRC = MEASURED / "anchor_survivability_between_constitutions_v1.csv"
OUT = MEASURED / "anchor_handoff_search_v1.csv"

CENTER_FIXED_TOLERANCE = 40
WIDTH_FIXED_TOLERANCE = 80

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))

for r in rows:
    r["from_window"] = int(r["from_window"])
    r["to_window"] = int(r["to_window"])
    r["from_center"] = float(r["from_center"])
    r["to_center"] = float(r["to_center"])
    r["center_delta"] = float(r["center_delta"])
    r["abs_center_delta"] = float(r["abs_center_delta"])
    r["from_width"] = int(r["from_width"])
    r["to_width"] = int(r["to_width"])
    r["width_delta"] = int(r["width_delta"])

def zone(center):
    if center < 1333:
        return "left"
    if center < 2667:
        return "middle"
    return "right"

out_rows = []

pairs = sorted(set((r["from_window"], r["to_window"]) for r in rows))

for fw, tw in pairs:
    pair_rows = [r for r in rows if r["from_window"] == fw and r["to_window"] == tw]

    fixed = [r for r in pair_rows if r["abs_center_delta"] <= CENTER_FIXED_TOLERANCE]
    near = [r for r in pair_rows if CENTER_FIXED_TOLERANCE < r["abs_center_delta"] <= 125]

    if fixed:
        holding = fixed
        anchor_mode = "fixed_anchor_present"
    elif near:
        holding = near
        anchor_mode = "near_anchor_present"
    else:
        holding = []
        anchor_mode = "no_local_anchor"

    if not holding:
        out_rows.append({
            "terrain": "hierarchical_burst_structural_v2",
            "from_window": fw,
            "to_window": tw,
            "anchor_mode": anchor_mode,
            "anchor_count": 0,
            "holding_zones": "",
            "anchor_centers": "",
            "width_behavior": "",
            "handoff_read": "no clear positional anchor under tolerance",
            "boundary_note": "anchor_handoff_not_identity",
        })
        continue

    zones = [zone(r["to_center"]) for r in holding]
    centers = [str(round(r["to_center"], 2)) for r in holding]

    width_fixed = [
        r for r in holding
        if abs(r["width_delta"]) <= WIDTH_FIXED_TOLERANCE
    ]

    if len(width_fixed) == len(holding):
        width_behavior = "center_and_width_hold"
    elif len(width_fixed) > 0:
        width_behavior = "mixed_width_hold_and_change"
    else:
        width_behavior = "center_holds_width_changes"

    zone_text = "|".join(zones)

    if len(set(zones)) == 1:
        handoff = f"{zones[0]} holds field"
    else:
        handoff = f"multi-zone hold: {zone_text}"

    out_rows.append({
        "terrain": "hierarchical_burst_structural_v2",
        "from_window": fw,
        "to_window": tw,
        "anchor_mode": anchor_mode,
        "anchor_count": len(holding),
        "holding_zones": zone_text,
        "anchor_centers": "|".join(centers),
        "width_behavior": width_behavior,
        "handoff_read": handoff,
        "boundary_note": "anchor_handoff_not_identity",
    })

fieldnames = [
    "terrain",
    "from_window",
    "to_window",
    "anchor_mode",
    "anchor_count",
    "holding_zones",
    "anchor_centers",
    "width_behavior",
    "handoff_read",
    "boundary_note",
]

with OUT.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(out_rows)

print("WROTE", OUT.resolve())
