import csv
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001")

HOLLOW = BASE / "hollow_candidate_surface_v1.csv"
REL = BASE / "middle_feature_relation_read_v1.csv"
SIG = BASE / "grammar_signature_surface_v1.csv"

OUT = BASE / "pause_basin_surface_v1.csv"

hollow_rows = list(csv.DictReader(HOLLOW.open("r", encoding="utf-8")))
rel_rows = list(csv.DictReader(REL.open("r", encoding="utf-8")))
sig_rows = list(csv.DictReader(SIG.open("r", encoding="utf-8")))

rows = []

for r in hollow_rows:
    if r["candidate_type"] in ["spacing_basin", "low_transition_basin"]:
        rows.append({
            "pause_id": f"pause_{len(rows)+1:03}",
            "pause_type": "spacing_hold",
            "source_surface": "hollow_candidate_surface_v1",
            "constitution_range": r["constitution_range"],
            "zone_or_span": r["zone_or_span"],
            "evidence_strength": r["evidence_strength"],
            "supporting_rows": r["supporting_rows"],
            "boundary_note": "spacing or low-transition behavior may support lawful pause"
        })

for r in rel_rows:
    if r["relation_type"] == "continues" and float(r["overlap_ratio_from"]) >= 0.95:
        rows.append({
            "pause_id": f"pause_{len(rows)+1:03}",
            "pause_type": "continuity_hold",
            "source_surface": "middle_feature_relation_read_v1",
            "constitution_range": f'{r["from_window_size"]}->{r["to_window_size"]}',
            "zone_or_span": r["from_interval"],
            "evidence_strength": "supported",
            "supporting_rows": "1",
            "boundary_note": "high-overlap continuation suggests low-deformation hold"
        })

for r in sig_rows:
    if r["evidence_strength"] in ["mixed", "weak_support"]:
        rows.append({
            "pause_id": f"pause_{len(rows)+1:03}",
            "pause_type": "unresolved_hold",
            "source_surface": "grammar_signature_surface_v1",
            "constitution_range": r["constitution_survivability"],
            "zone_or_span": r["zone"],
            "evidence_strength": r["evidence_strength"],
            "supporting_rows": "1",
            "boundary_note": "weak or mixed support preserved without promotion"
        })

fields = [
    "pause_id",
    "pause_type",
    "source_surface",
    "constitution_range",
    "zone_or_span",
    "evidence_strength",
    "supporting_rows",
    "boundary_note"
]

with OUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print("")
print("WROTE")
print(OUT.resolve())
print("")
