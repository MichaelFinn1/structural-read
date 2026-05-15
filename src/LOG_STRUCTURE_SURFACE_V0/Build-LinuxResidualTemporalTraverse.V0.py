import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

SOURCE = Path(r"C:\Users\Admin\Desktop\StructuralRead_FirstUserTest\terrain\loghub_2k_panel\Linux\Linux_2k.log")
OUTDIR = Path("linux_residual_temporal_001_out")
OUTDIR.mkdir(exist_ok=True)

WINDOWS = [100, 250, 500, 1000]

def normalize(line):
    s = line.strip()
    s = re.sub(r"\b[0-9a-fA-F]{8,}\b", "<hex>", s)
    s = re.sub(r"\b\d+\b", "<num>", s)
    s = re.sub(r"\s+", " ", s)
    return s

def rough_family(template):
    parts = template.split()
    return " ".join(parts[:5])

lines = SOURCE.read_text(encoding="utf-8", errors="replace").splitlines()
templates = [normalize(x) for x in lines]
counts = Counter(templates)

regimes = []
for t in templates:
    c = counts[t]
    if c >= 5:
        regimes.append("stable")
    elif c >= 2:
        regimes.append("middle")
    else:
        regimes.append("residual")

summary_rows = []

for window_size in WINDOWS:
    for start in range(0, len(lines), window_size):
        end = min(start + window_size, len(lines))
        idxs = list(range(start, end))
        window_id = f"window_{(start // window_size) + 1:03d}"

        residual_idxs = [i for i in idxs if regimes[i] == "residual"]
        stable_idxs = [i for i in idxs if regimes[i] == "stable"]
        middle_idxs = [i for i in idxs if regimes[i] == "middle"]

        residual_self_adjacent = 0
        residual_near_stable = 0
        residual_near_middle = 0

        family_counts = Counter()

        for i in residual_idxs:
            neighbors = []
            if i > 0:
                neighbors.append(regimes[i - 1])
            if i < len(regimes) - 1:
                neighbors.append(regimes[i + 1])

            if "residual" in neighbors:
                residual_self_adjacent += 1
            if "stable" in neighbors:
                residual_near_stable += 1
            if "middle" in neighbors:
                residual_near_middle += 1

            family_counts[rough_family(templates[i])] += 1

        residual_count = len(residual_idxs)
        dominant_share = 0.0
        dominant_family = ""

        if residual_count > 0:
            dominant_family, dominant_count = family_counts.most_common(1)[0]
            dominant_share = dominant_count / residual_count

        residual_share = residual_count / len(idxs)
        stable_share = len(stable_idxs) / len(idxs)
        middle_share = len(middle_idxs) / len(idxs)

        self_share = residual_self_adjacent / residual_count if residual_count else 0.0
        stable_attach_share = residual_near_stable / residual_count if residual_count else 0.0

        if residual_count == 0:
            posture = "no_residual"
        elif self_share >= 0.70 and stable_attach_share < 0.25:
            posture = "residual_island"
        elif stable_attach_share >= 0.50:
            posture = "stable_attached_residual"
        elif self_share >= 0.40:
            posture = "partial_residual_cluster"
        else:
            posture = "diffuse_residual"

        summary_rows.append({
            "window_size": window_size,
            "window_id": window_id,
            "line_start": start + 1,
            "line_end": end,
            "lines": len(idxs),
            "stable_lines": len(stable_idxs),
            "middle_lines": len(middle_idxs),
            "residual_lines": residual_count,
            "stable_share": round(stable_share, 4),
            "middle_share": round(middle_share, 4),
            "residual_share": round(residual_share, 4),
            "residual_self_adjacent": residual_self_adjacent,
            "residual_near_stable": residual_near_stable,
            "residual_near_middle": residual_near_middle,
            "residual_self_adjacent_share": round(self_share, 4),
            "residual_near_stable_share": round(stable_attach_share, 4),
            "dominant_residual_family_share": round(dominant_share, 4),
            "dominant_residual_family": dominant_family,
            "local_residue_posture": posture,
        })

out = OUTDIR / "linux_residual_temporal_windows_v0.csv"
with out.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
    writer.writeheader()
    writer.writerows(summary_rows)

print("")
print("WROTE")
print(out.resolve())
print("")
