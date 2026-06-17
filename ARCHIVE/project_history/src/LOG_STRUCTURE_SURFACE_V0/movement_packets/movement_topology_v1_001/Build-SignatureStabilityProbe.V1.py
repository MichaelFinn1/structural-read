import csv
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001")

SRC = BASE / "grammar_signature_surface_v1.csv"
OUT = BASE / "signature_stability_probe_v1.csv"

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))

probe_rows = []

probes = [
    "zone_shift_probe",
    "constitution_density_probe",
    "extraction_threshold_probe",
    "terrain_comparison_probe",
]

for r in rows:
    for probe in probes:

        if probe == "zone_shift_probe":
            if r["signature_type"] in ["carrier_persistence", "null_zone_respect", "local_symmetry_pocket"]:
                expected = "sensitive"
            else:
                expected = "moderate"

        elif probe == "constitution_density_probe":
            if r["constitution_survivability"] in ["broad_stable", "multiscale"]:
                expected = "likely_stable"
            else:
                expected = "sensitive"

        elif probe == "extraction_threshold_probe":
            if r["signature_type"] in ["convergence_preservation", "seam_handoff_candidate"]:
                expected = "sensitive"
            else:
                expected = "moderate"

        elif probe == "terrain_comparison_probe":
            expected = "unknown_until_replayed"

        probe_rows.append({
            "signature_id": r["signature_id"],
            "signature_type": r["signature_type"],
            "current_evidence_strength": r["evidence_strength"],
            "current_survivability": r["constitution_survivability"],
            "probe_type": probe,
            "expected_stability": expected,
            "probe_status": "not_run",
            "result_after_probe": "",
            "boundary_note": "stability probe only; does not add new grammar"
        })

fields = list(probe_rows[0].keys())

with OUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(probe_rows)

print("")
print("WROTE")
print(OUT.resolve())
print("")
