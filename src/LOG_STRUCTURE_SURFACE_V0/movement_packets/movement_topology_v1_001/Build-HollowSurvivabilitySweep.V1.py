import csv
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001")

HOLLOW = BASE / "hollow_candidate_surface_v1.csv"
BALANCE = BASE / "relational_balance_regimes_v1.csv"

OUT = BASE / "hollow_survivability_sweep_v1.csv"

hollow_rows = list(csv.DictReader(HOLLOW.open("r", encoding="utf-8")))
balance_rows = list(csv.DictReader(BALANCE.open("r", encoding="utf-8")))

results = []

spacing_rows = [
    r for r in hollow_rows
    if r["candidate_type"] == "spacing_basin"
]

baseline_count = len(spacing_rows)

# Probe 1: constitution density
dense_sizes_present = sorted(
    set(r["constitution_range"] for r in spacing_rows),
    key=lambda x: int(x)
)

if baseline_count >= 7:
    density_result = "survives"
elif baseline_count >= 3:
    density_result = "weakens"
else:
    density_result = "insufficient"

results.append({
    "candidate_type": "spacing_basin",
    "probe_type": "constitution_density_probe",
    "baseline_supporting_rows": baseline_count,
    "probe_supporting_rows": baseline_count,
    "survivability_result": density_result,
    "constitution_range": "|".join(dense_sizes_present),
    "boundary_note": "tests whether spacing basin appears across multiple constitutions already present"
})

# Probe 2: stricter spacing threshold
strict_rows = []

for r in balance_rows:
    if (
        r.get("centerline_relation") == "null_spanning"
        and float(r["pair_separation"]) >= 1000
    ):
        strict_rows.append(r)

strict_count = len(strict_rows)

if strict_count >= 5:
    strict_result = "survives"
elif strict_count >= 2:
    strict_result = "weakens"
else:
    strict_result = "dissolves"

results.append({
    "candidate_type": "spacing_basin",
    "probe_type": "extraction_threshold_probe",
    "baseline_supporting_rows": baseline_count,
    "probe_supporting_rows": strict_count,
    "survivability_result": strict_result,
    "constitution_range": "|".join(sorted(set(r["window_size"] for r in strict_rows), key=lambda x: int(x))) if strict_rows else "",
    "boundary_note": "stricter threshold requires null-spanning separation >= 1000"
})

# Probe 3: zone deformation replay
zone_variants = {
    "baseline": (750, 1250),
    "variant_a": (700, 1300),
    "variant_b": (800, 1200)
}

for name, limits in zone_variants.items():

    left_max, null_max = limits

    support = 0
    sizes = []

    for r in balance_rows:

        midpoint = (float(r["left_center"]) + float(r["right_center"])) / 2.0

        if midpoint > left_max and midpoint <= null_max:
            support += 1
            sizes.append(r["window_size"])

    if support >= 5:
        result = "survives"
    elif support >= 2:
        result = "weakens"
    else:
        result = "dissolves"

    results.append({
        "candidate_type": "spacing_basin",
        "probe_type": f"zone_shift_probe_{name}",
        "baseline_supporting_rows": baseline_count,
        "probe_supporting_rows": support,
        "survivability_result": result,
        "constitution_range": "|".join(sorted(set(sizes), key=lambda x: int(x))) if sizes else "",
        "boundary_note": "zone shift tests spacing basin sensitivity to null boundary placement"
    })

# Probe 4 placeholder: alternate terrain families
results.append({
    "candidate_type": "spacing_basin",
    "probe_type": "terrain_comparison_probe",
    "baseline_supporting_rows": baseline_count,
    "probe_supporting_rows": "",
    "survivability_result": "not_run",
    "constitution_range": "",
    "boundary_note": "requires replay on alternate terrain packets; intentionally not inferred here"
})

fields = [
    "candidate_type",
    "probe_type",
    "baseline_supporting_rows",
    "probe_supporting_rows",
    "survivability_result",
    "constitution_range",
    "boundary_note"
]

with OUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(results)

print("")
print("WROTE")
print(OUT.resolve())
print("")
