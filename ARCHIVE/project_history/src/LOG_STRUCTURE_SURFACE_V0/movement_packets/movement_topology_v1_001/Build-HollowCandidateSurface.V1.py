import csv
from pathlib import Path

BASE = Path(
    "src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001"
)

STANCE = BASE / "stance_relation_summary_v1.csv"
DEFORM = BASE / "local_ecology_deformation_events_v1.csv"
GRAMMAR = BASE / "grammar_signature_surface_v1.csv"

OUT = BASE / "hollow_candidate_surface_v1.csv"

stance_rows = list(csv.DictReader(STANCE.open("r", encoding="utf-8")))
deform_rows = list(csv.DictReader(DEFORM.open("r", encoding="utf-8")))
grammar_rows = list(csv.DictReader(GRAMMAR.open("r", encoding="utf-8")))

results = []

candidate_counter = 1

#
# 1. spacing-preservation basin candidates
#

for r in stance_rows:

    separation = float(r["pair_separation"])

    if (
        r["null_zone_relation"] == "circles_null_zone"
        and separation >= 800
    ):

        results.append({
            "candidate_id":
                f"cand_{candidate_counter:03}",
            "candidate_type":
                "spacing_basin",
            "constitution_range":
                r["window_size"],
            "zone_or_span":
                "cross_null_zone",
            "supporting_rows":
                "1",
            "evidence_strength":
                "supported",
            "survivability":
                "broad_stable",
            "boundary_note":
                "spacing preserved across low-participation basin"
        })

        candidate_counter += 1

#
# 2. carrier/background separation candidates
#

for r in stance_rows:

    if (
        r["balance_relation"] == "left_dominant"
        and r["null_zone_relation"] == "circles_null_zone"
    ):

        results.append({
            "candidate_id":
                f"cand_{candidate_counter:03}",
            "candidate_type":
                "carrier_separation_basin",
            "constitution_range":
                r["window_size"],
            "zone_or_span":
                "left_to_right_span",
            "supporting_rows":
                "1",
            "evidence_strength":
                "weak_support",
            "survivability":
                "meso_stable",
            "boundary_note":
                "persistent carrier/background asymmetry candidate"
        })

        candidate_counter += 1

#
# 3. low-transition basin candidates
#

for r in grammar_rows:

    if r["signature_type"] == "null_zone_respect":

        results.append({
            "candidate_id":
                f"cand_{candidate_counter:03}",
            "candidate_type":
                "low_transition_basin",
            "constitution_range":
                "broad",
            "zone_or_span":
                "null_zone",
            "supporting_rows":
                "1",
            "evidence_strength":
                r["evidence_strength"],
            "survivability":
                r["constitution_survivability"],
            "boundary_note":
                "candidate low-transition basin under reread constitution"
        })

        candidate_counter += 1

#
# 4. recomposition corridor candidates
#

recomp_rows = [
    r for r in deform_rows
    if r["relation_type"] in ["merges", "splits"]
]

if len(recomp_rows) >= 10:

    results.append({
        "candidate_id":
            f"cand_{candidate_counter:03}",
        "candidate_type":
            "recomposition_corridor",
        "constitution_range":
            "50_to_250",
        "zone_or_span":
            "left_zone",
        "supporting_rows":
            str(len(recomp_rows)),
        "evidence_strength":
            "supported",
        "survivability":
            "recomposition_dependent",
        "boundary_note":
            "merge/split density suggests recomposition corridor"
    })

    candidate_counter += 1

fields = [
    "candidate_id",
    "candidate_type",
    "constitution_range",
    "zone_or_span",
    "supporting_rows",
    "evidence_strength",
    "survivability",
    "boundary_note"
]

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
