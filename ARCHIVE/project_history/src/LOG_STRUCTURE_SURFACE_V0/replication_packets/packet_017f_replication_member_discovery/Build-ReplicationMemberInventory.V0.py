import csv
from pathlib import Path

ROOT = Path("src/LOG_STRUCTURE_SURFACE_V0")
OUT_DIR = ROOT / "replication_packets" / "packet_017f_replication_member_discovery"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_CSV = OUT_DIR / "replication_member_inventory_v0.csv"
OUT_MD = OUT_DIR / "replication_member_read_v0.md"

families = ["apache", "openstack", "linux"]

def infer_family(path_text):
    p = path_text.lower()
    for fam in families:
        if fam in p:
            return fam
    return None

def estimate_status(path):
    files = list(path.rglob("*"))
    names = [f.name.lower() for f in files if f.is_file()]

    has_log = any(n.endswith(".log") or ".log." in n for n in names)
    has_csv = any(n.endswith(".csv") for n in names)
    has_html = any(n.endswith(".html") for n in names)
    has_measured = any("measured" in str(f).lower() for f in files)

    if has_log and has_csv and has_html:
        return "ready", "source log plus generated surfaces and visualization present"
    if has_log and (has_csv or has_measured):
        return "partial", "source log and some measured/generated material present"
    if has_log:
        return "partial", "source log present; generated pipeline status unclear"
    if has_csv or has_html or has_measured:
        return "partial", "generated material present; source log unclear"
    return "unknown", "family-like path found; source/generated status unclear"

candidate_dirs = {}

for p in ROOT.rglob("*"):
    if not p.exists():
        continue

    fam = infer_family(str(p))
    if fam is None:
        continue

    if p.is_file():
        parent = p.parent
    else:
        parent = p

    # Prefer meaningful terrain-like folders.
    parts = [x.lower() for x in parent.parts]
    if any(x in parts for x in ["visualizations", "measured", "notes"]):
        parent = parent.parent

    key = str(parent)
    if key not in candidate_dirs:
        candidate_dirs[key] = fam

rows = []

for path_text, fam in sorted(candidate_dirs.items(), key=lambda kv: (families.index(kv[1]), kv[0].lower())):
    path = Path(path_text)

    # Skip very broad roots unless they are clearly terrain-like.
    rel = path.as_posix()
    low = rel.lower()

    if low.endswith("log_structure_surface_v0"):
        continue
    if low.endswith("long_duration_packets"):
        continue
    if low.endswith("calibration_packets"):
        continue

    status, note = estimate_status(path)

    terrain_member = path.name

    rows.append({
        "family_name": fam,
        "terrain_member": terrain_member,
        "source_path": rel,
        "estimated_status": status,
        "notes": note
    })

# De-duplicate while preserving order.
seen = set()
deduped = []
for r in rows:
    k = (r["family_name"], r["terrain_member"], r["source_path"])
    if k in seen:
        continue
    seen.add(k)
    deduped.append(r)

fields = [
    "family_name",
    "terrain_member",
    "source_path",
    "estimated_status",
    "notes"
]

with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(deduped)

by_family = {fam: [] for fam in families}
for r in deduped:
    by_family[r["family_name"]].append(r)

recommended = []
for fam in families:
    ready = [r for r in by_family[fam] if r["estimated_status"] == "ready"]
    partial = [r for r in by_family[fam] if r["estimated_status"] == "partial"]
    recommended.extend((ready + partial)[:3])

lines = []
lines.append("# PACKET_017F_REPLICATION_MEMBER_DISCOVERY")
lines.append("")
lines.append("Status:")
lines.append("discovery_inventory_only")
lines.append("")
lines.append("## Purpose")
lines.append("")
lines.append("This packet inventories additional Apache, OpenStack, and Linux terrain members that may be eligible for existing replication processing.")
lines.append("")
lines.append("It does not create new metrics, observer layers, geometry vocabulary, classifiers, or substrate types.")
lines.append("")
lines.append("## Discovered family members")
lines.append("")

for fam in families:
    lines.append(f"### {fam}")
    lines.append("")
    fam_rows = by_family[fam]

    if not fam_rows:
        lines.append("No candidate members discovered.")
        lines.append("")
        continue

    for r in fam_rows:
        lines.append(f"- {r['terrain_member']}")
        lines.append(f"  - path: `{r['source_path']}`")
        lines.append(f"  - estimated_status: {r['estimated_status']}")
        lines.append(f"  - notes: {r['notes']}")
    lines.append("")

lines.append("## Expected processing effort")
lines.append("")
lines.append("- ready: likely already has enough source/generated material to inspect or route through existing pipeline with minimal work.")
lines.append("- partial: likely needs a small existing-pipeline rerun or source/generated-path check.")
lines.append("- unknown: discovered by family naming only; inspect before processing.")
lines.append("")
lines.append("## Obvious obstacles")
lines.append("")
lines.append("- Some candidates may be generated folders rather than true terrain members.")
lines.append("- Some members may contain surfaces without original source logs.")
lines.append("- Some source logs may need existing traversal scripts rerun before entering 017E replication matrix.")
lines.append("- Current inventory is path-based discovery only; it does not validate geometry readiness.")
lines.append("")
lines.append("## Recommended next 3 members to process")
lines.append("")

if recommended:
    for r in recommended[:3]:
        lines.append(f"1. `{r['family_name']}` / `{r['terrain_member']}`")
        lines.append(f"   - path: `{r['source_path']}`")
        lines.append(f"   - status: {r['estimated_status']}")
        lines.append(f"   - reason: {r['notes']}")
else:
    lines.append("No recommended members yet. Inspect inventory manually.")

lines.append("")
lines.append("## Boundary")
lines.append("")
lines.append("This packet is discovery and inventory only.")
lines.append("")
lines.append("It does not interpret geometry, compare outputs, or promote replication claims.")
lines.append("")
lines.append("## Question served")
lines.append("")
lines.append("Do geometry distinctions replicate across terrain members within the same family under the same observer apparatus?")
lines.append("")

OUT_MD.write_text("\n".join(lines), encoding="utf-8")

print("")
print("WROTE")
print(OUT_CSV)
print(OUT_MD)
print("")
print("ROWS", len(deduped))
