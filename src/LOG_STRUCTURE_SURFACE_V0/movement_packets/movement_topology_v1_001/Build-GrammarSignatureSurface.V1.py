import csv
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001")

REL = BASE / "middle_feature_relation_read_v1.csv"
DEF = BASE / "local_ecology_deformation_events_v1.csv"
STANCE = BASE / "stance_relation_summary_v1.csv"
BAL = BASE / "relational_balance_regimes_v1.csv"

OUT = BASE / "grammar_signature_surface_v1.csv"

relations = list(csv.DictReader(REL.open("r", encoding="utf-8")))
deformations = list(csv.DictReader(DEF.open("r", encoding="utf-8")))
stances = list(csv.DictReader(STANCE.open("r", encoding="utf-8")))
balances = list(csv.DictReader(BAL.open("r", encoding="utf-8")))

signatures = []

def add(signature_id, signature_type, support, constitution_range, zone, evidence_strength, survivability, volatility, boundary_note):
    signatures.append({
        "signature_id": signature_id,
        "signature_type": signature_type,
        "supporting_rows": support,
        "constitution_range": constitution_range,
        "zone": zone,
        "evidence_strength": evidence_strength,
        "constitution_survivability": survivability,
        "relation_volatility": volatility,
        "boundary_note": boundary_note
    })

# 1 carrier_persistence
carrier_rows = [
    r for r in balances
    if r.get("carrier_relation") == "persistent_carrier_candidate"
]

carrier_sizes = sorted(set(r["window_size"] for r in carrier_rows), key=lambda x: int(x))

if len(carrier_sizes) >= 4:
    strength = "supported"
    survivability = "broad_stable"
elif len(carrier_sizes) >= 2:
    strength = "weak_support"
    survivability = "meso_stable"
else:
    strength = "insufficient_evidence"
    survivability = "local_only"

add(
    "sig_001",
    "carrier_persistence",
    str(len(carrier_rows)),
    "|".join(carrier_sizes),
    "left_zone",
    strength,
    survivability,
    "smoothing_dominant",
    "broad carrier candidate only; not object identity"
)

# 2 convergence_preservation
merge_rows = [
    r for r in deformations
    if r["relation_type"] == "merges"
]

preserved_merges = [
    r for r in merge_rows
    if r["width_preservation_ratio"] not in ["", None]
    and 0.75 <= float(r["width_preservation_ratio"]) <= 1.6
]

if len(preserved_merges) >= 5:
    strength = "supported"
elif len(preserved_merges) >= 2:
    strength = "weak_support"
else:
    strength = "mixed"

add(
    "sig_002",
    "convergence_preservation",
    f"{len(preserved_merges)}/{len(merge_rows)}",
    "adjacent_constitutions",
    "left_zone",
    strength,
    "recomposition_dependent",
    "recomposition_heavy",
    "width preservation is approximate; mass is width proxy only"
)

# 3 seam_handoff_candidate
disappears = [
    r for r in deformations
    if r["relation_type"] == "disappears"
]

appears = [
    r for r in deformations
    if r["relation_type"] == "appears"
]

handoff_candidates = []

for d in disappears:
    d_to = int(d["to_window_size"])
    d_zone = d["from_zone"]

    for a in appears:
        a_from = int(a["from_window_size"])
        a_zone = a["to_zone"]

        if d_to == a_from and d_zone != "none" and a_zone != "none":
            handoff_candidates.append((d, a))

if len(handoff_candidates) >= 5:
    strength = "weak_support"
else:
    strength = "insufficient_evidence"

add(
    "sig_003",
    "seam_handoff_candidate",
    str(len(handoff_candidates)),
    "adjacent_constitutions",
    "mixed_zone",
    strength,
    "constitution_local_only",
    "fragmentation_prone",
    "appearance after disappearance suggests possible reconstitution, not identity transfer"
)

# 4 local_symmetry_pocket
balanced_rows = [
    r for r in balances
    if r["width_symmetry"] == "balanced"
    or r["spacing_symmetry"] == "tight"
]

right_pockets = [
    r for r in balanced_rows
    if float(r["left_center"]) >= 1250
    or float(r["right_center"]) >= 1250
]

if len(right_pockets) >= 5:
    strength = "supported"
elif len(right_pockets) >= 2:
    strength = "weak_support"
else:
    strength = "insufficient_evidence"

add(
    "sig_004",
    "local_symmetry_pocket",
    str(len(right_pockets)),
    "fine_to_meso",
    "right_zone",
    strength,
    "meso_stable",
    "continuity_friendly",
    "local symmetry is spacing/width posture only; not equilibrium"
)

# 5 null_zone_respect
null_spanning = [
    r for r in balances
    if r["centerline_relation"] == "null_spanning"
]

null_direct_activity = [
    r for r in deformations
    if r["from_zone"] == "null_zone"
    or r["to_zone"] == "null_zone"
]

if len(null_spanning) > 0 and len(null_direct_activity) == 0:
    strength = "supported"
elif len(null_spanning) > 0:
    strength = "mixed"
else:
    strength = "insufficient_evidence"

add(
    "sig_005",
    "null_zone_respect",
    f"null_spanning={len(null_spanning)}; direct_null_activity={len(null_direct_activity)}",
    "meso_to_broad",
    "null_zone",
    strength,
    "broad_stable",
    "smoothing_dominant",
    "null zone is low-activity basin; spanning relation is not orbit"
)

fields = list(signatures[0].keys())

with OUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(signatures)

print("")
print("WROTE")
print(OUT.resolve())
print("")
