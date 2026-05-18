import csv
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001")

SIG_ZONE = BASE / "signature_zone_shift_probe_v1.csv"
HOLLOW_SWEEP = BASE / "hollow_survivability_sweep_v1.csv"
REL = BASE / "middle_feature_relation_read_v1.csv"

OUT = BASE / "replay_degradation_surface_v1.csv"

rows = []

sig_rows = list(csv.DictReader(SIG_ZONE.open("r", encoding="utf-8")))
hollow_rows = list(csv.DictReader(HOLLOW_SWEEP.open("r", encoding="utf-8")))
rel_rows = list(csv.DictReader(REL.open("r", encoding="utf-8")))

for r in sig_rows:
    if r["change_class"] in ["weakens", "dissolves", "relocates"]:
        rows.append({
            "degradation_id": f"deg_{len(rows)+1:03}",
            "source_surface": "signature_zone_shift_probe_v1",
            "degradation_type": "signature_drift",
            "affected_item": r["signature_type"],
            "constitution_or_probe": r["zone_variant"],
            "severity": r["change_class"],
            "supporting_detail": f'{r["baseline_status"]}->{r["probe_status"]}; rows={r["supporting_rows"]}',
            "boundary_note": "signature changed under bounded zone reread"
        })

for r in hollow_rows:
    if r["survivability_result"] in ["weakens", "dissolves", "not_run"]:
        rows.append({
            "degradation_id": f"deg_{len(rows)+1:03}",
            "source_surface": "hollow_survivability_sweep_v1",
            "degradation_type": "candidate_survivability_gap",
            "affected_item": r["candidate_type"],
            "constitution_or_probe": r["probe_type"],
            "severity": r["survivability_result"],
            "supporting_detail": f'baseline={r["baseline_supporting_rows"]}; probe={r["probe_supporting_rows"]}',
            "boundary_note": "candidate basin support incomplete under replay variation"
        })

relation_counts = {}
for r in rel_rows:
    k = f'{r["from_window_size"]}->{r["to_window_size"]}'
    relation_counts.setdefault(k, {"total": 0, "loss": 0})
    relation_counts[k]["total"] += 1
    if r["relation_type"] in ["appears", "disappears", "ambiguous"]:
        relation_counts[k]["loss"] += 1

for transition, counts in relation_counts.items():
    total = counts["total"]
    loss = counts["loss"]
    if total == 0:
        continue
    loss_ratio = loss / total
    if loss_ratio >= 0.5:
        severity = "high"
    elif loss_ratio >= 0.25:
        severity = "moderate"
    else:
        severity = "low"

    if severity != "low":
        rows.append({
            "degradation_id": f"deg_{len(rows)+1:03}",
            "source_surface": "middle_feature_relation_read_v1",
            "degradation_type": "transition_loss",
            "affected_item": transition,
            "constitution_or_probe": transition,
            "severity": severity,
            "supporting_detail": f"loss={loss}; total={total}; ratio={round(loss_ratio,3)}",
            "boundary_note": "transition contains high appear/disappear pressure"
        })

fields = [
    "degradation_id",
    "source_surface",
    "degradation_type",
    "affected_item",
    "constitution_or_probe",
    "severity",
    "supporting_detail",
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
