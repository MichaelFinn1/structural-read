import csv
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001")

SIG = BASE / "grammar_signature_surface_v1.csv"
BAL = BASE / "relational_balance_regimes_v1.csv"

OUT = BASE / "signature_zone_shift_probe_v1.csv"

signatures = list(csv.DictReader(SIG.open("r", encoding="utf-8")))
balances = list(csv.DictReader(BAL.open("r", encoding="utf-8")))

variants = {
    "baseline": {
        "left_max": 750,
        "null_max": 1250
    },
    "variant_a": {
        "left_max": 700,
        "null_max": 1300
    },
    "variant_b": {
        "left_max": 800,
        "null_max": 1200
    }
}

results = []

def classify_zone(center, left_max, null_max):

    c = float(center)

    if c <= left_max:
        return "left_zone"

    if c <= null_max:
        return "null_zone"

    return "right_zone"

baseline_map = {
    r["signature_type"]: r["evidence_strength"]
    for r in signatures
}

target_signatures = [
    "carrier_persistence",
    "local_symmetry_pocket",
    "null_zone_respect"
]

for sig in target_signatures:

    baseline_status = baseline_map.get(sig, "unknown")

    for variant_name, config in variants.items():

        left_max = config["left_max"]
        null_max = config["null_max"]

        supporting_rows = 0

        if sig == "carrier_persistence":

            rows = [
                r for r in balances
                if r.get("carrier_relation") == "persistent_carrier_candidate"
            ]

            for r in rows:

                zone = classify_zone(
                    r["left_center"],
                    left_max,
                    null_max
                )

                if zone == "left_zone":
                    supporting_rows += 1

        elif sig == "local_symmetry_pocket":

            rows = [
                r for r in balances
                if r["spacing_symmetry"] == "tight"
            ]

            for r in rows:

                midpoint = (
                    float(r["left_center"]) +
                    float(r["right_center"])
                ) / 2

                zone = classify_zone(
                    midpoint,
                    left_max,
                    null_max
                )

                if zone == "right_zone":
                    supporting_rows += 1

        elif sig == "null_zone_respect":

            rows = [
                r for r in balances
                if r["centerline_relation"] == "null_spanning"
            ]

            supporting_rows = len(rows)

        if supporting_rows >= 5:
            probe_status = "supported"
        elif supporting_rows >= 2:
            probe_status = "weak_support"
        elif supporting_rows == 1:
            probe_status = "ambiguous"
        else:
            probe_status = "dissolves"

        if probe_status == baseline_status:
            change = "survives"
        elif probe_status in ["weak_support", "ambiguous"] and baseline_status == "supported":
            change = "weakens"
        elif probe_status == "dissolves":
            change = "dissolves"
        else:
            change = "relocates"

        results.append({
            "signature_type": sig,
            "zone_variant": variant_name,
            "baseline_status": baseline_status,
            "probe_status": probe_status,
            "change_class": change,
            "supporting_rows": supporting_rows,
            "boundary_note": "zone shift tests dependence on current zoning, not correctness of zones"
        })

fields = list(results[0].keys())

with OUT.open("w", newline="", encoding="utf-8") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fields
    )

    writer.writeheader()

    for r in results:
        writer.writerow(r)

print("")
print("WROTE")
print(OUT.resolve())
print("")
