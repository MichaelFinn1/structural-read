import csv
from pathlib import Path

ROOT = Path(r"C:\Users\Admin\Desktop\New_Dawn_4\structural-read\src\LOG_STRUCTURE_SURFACE_V0")

METRIC_CSV = Path(r"C:\Users\Admin\Desktop\StructuralRead_FirstUserTest\terrain_ecology_compare_v0\terrain_ecology_compare_v0.csv")
POSTURE_CSV = ROOT / "cross_layer_ecology_compare_v0.csv"

out_dir = ROOT / "terrain_visuals_v0"
out_dir.mkdir(exist_ok=True)

# ----------------------------------------------------
# LOAD POSTURE TABLE
# ----------------------------------------------------

postures = {}

with open(POSTURE_CSV, newline="", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        postures[r["terrain"]] = r

# ----------------------------------------------------
# LOAD METRICS
# ----------------------------------------------------

rows = []

with open(METRIC_CSV, newline="", encoding="utf-8-sig") as f:

    for r in csv.DictReader(f):

        terrain = r["terrain"]

        p = postures.get(terrain, {})

        rows.append({
            "terrain": terrain,
            "file": r["file"],

            "stable_posture": p.get("stable_posture", ""),
            "middle_posture": p.get("middle_posture", ""),
            "residual_posture": p.get("residual_posture", ""),
            "observer_notes": p.get("observer_notes", ""),

            "residual_forms": int(float(r["residual_forms"])),
            "rough_residual_families": int(float(r["rough_residual_families"])),

            "largest_residual_family_share":
                float(r["largest_residual_family_share"]),

            "residual_attachment_ratio":
                float(r["residual_attachment_ratio"]),
        })

# ----------------------------------------------------
# NORMALIZATION
# ----------------------------------------------------

max_attach = max(r["residual_attachment_ratio"] for r in rows)
max_share = max(r["largest_residual_family_share"] for r in rows)
max_forms = max(r["residual_forms"] for r in rows)
max_vocab = max(r["rough_residual_families"] for r in rows)

def percent(value, max_value):
    if max_value <= 0:
        return 0
    return round((value / max_value) * 100, 2)

# ----------------------------------------------------
# CARD SECTIONS
# ----------------------------------------------------

summary_rows = []

for r in sorted(rows, key=lambda x: x['terrain']):
    summary_rows.append(f'''
    <tr>
      <td>{r['terrain']}</td>
      <td>{r['stable_posture']}</td>
      <td>{r['middle_posture']}</td>
      <td>{r['residual_posture']}</td>
      <td>{r['residual_attachment_ratio']}%</td>
      <td>{r['largest_residual_family_share']}%</td>
      <td>{r['residual_forms']}</td>
      <td>{r['rough_residual_families']}</td>
    </tr>
    ''')

sections = []

for r in sorted(rows, key=lambda x: x["terrain"]):

    attach_pct = percent(r["residual_attachment_ratio"], max_attach)
    share_pct = percent(r["largest_residual_family_share"], max_share)
    forms_pct = percent(r["residual_forms"], max_forms)
    vocab_pct = percent(r["rough_residual_families"], max_vocab)

    sections.append(f"""

    <div class='card'>

        <h2>{r['terrain']} <span>{r['file']}</span></h2>

        <table class='posture'>
            <tr><td>stable posture</td><td>{r['stable_posture']}</td></tr>
            <tr><td>middle posture</td><td>{r['middle_posture']}</td></tr>
            <tr><td>residual posture</td><td>{r['residual_posture']}</td></tr>
        </table>

        <div class='metric'>
            <div class='label'>
                Residual Attachment ({r['residual_attachment_ratio']}%)
            </div>

            <div class='bar_bg'>
                <div class='bar_fill' style='width:{attach_pct}%'></div>
            </div>
        </div>

        <div class='metric'>
            <div class='label'>
                Largest Residual Family Share ({r['largest_residual_family_share']}%)
            </div>

            <div class='bar_bg'>
                <div class='bar_fill' style='width:{share_pct}%'></div>
            </div>
        </div>

        <div class='metric'>
            <div class='label'>
                Residual Forms ({r['residual_forms']})
            </div>

            <div class='bar_bg'>
                <div class='bar_fill' style='width:{forms_pct}%'></div>
            </div>
        </div>

        <div class='metric'>
            <div class='label'>
                Rough Residual Families ({r['rough_residual_families']})
            </div>

            <div class='bar_bg'>
                <div class='bar_fill' style='width:{vocab_pct}%'></div>
            </div>
        </div>

        <div class='notes'>
            {r['observer_notes']}
        </div>

    </div>
    """)

# ----------------------------------------------------
# HTML
# ----------------------------------------------------

html = f"""
<html>

<head>

<meta charset='utf-8'>

<title>Terrain Ecology Visual Comparison V0</title>

<style>

body {{
    background:#0b0f14;
    color:#eee;
    font-family:Segoe UI, Arial;
    padding:24px;
}}

.card {{
    background:#111820;
    border:1px solid #2c3945;
    border-radius:12px;
    padding:18px;
    margin-bottom:18px;
}}

h1 {{
    margin-bottom:12px;
}}

h2 span {{
    color:#888;
    font-size:13px;
    font-weight:400;
}}

table {{
    margin-bottom:18px;
}}

th {
    color:#aaa;
    text-align:left;
    padding:6px 12px 6px 0;
    border-bottom:1px solid #34414d;
}

td {{
    padding:4px 12px 4px 0;
}}

.metric {{
    margin-bottom:16px;
}}

.label {{
    margin-bottom:6px;
}}

.bar_bg {{
    background:#0d1319;
    border:1px solid #24313a;
    height:24px;
    border-radius:6px;
    overflow:hidden;
}}

.bar_fill {{
    background:#5aa9e6;
    height:100%;
}}

.notes {{
    margin-top:12px;
    color:#aaa;
}}

.boundary {{
    color:#999;
    margin-bottom:24px;
}}

</style>

</head>

<body>

<h1>Terrain Ecology Visual Comparison V0</h1>

<div class='boundary'>
Observer-only comparison.
Parallel dimensions only.
No ranking, anomaly scoring, or unified terrain score.
</div>

<div class='card'>
<h2>Comparison table</h2>
<table class='summary'>
<tr>
<th>terrain</th>
<th>stable</th>
<th>middle</th>
<th>residual</th>
<th>attachment</th>
<th>family share</th>
<th>residual forms</th>
<th>rough families</th>
</tr>
{''.join(summary_rows)}
</table>
</div>

{''.join(sections)}

</body>
</html>
"""

html_path = out_dir / "TERRAIN_ECOLOGY_VISUALS_V0.html"

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print("")
print("=== TERRAIN VISUALS COMPLETE ===")
print(html_path)

