import csv
from pathlib import Path

ROOT = Path(r"C:\Users\Admin\Desktop\StructuralRead_FirstUserTest\terrain\rootly_logs_dataset\logs-dataset-main\openssh")
OUT = ROOT / "_surface_work" / "temporal_strata_v0"

CSV_PATH = OUT / "temporal_strata_surface.csv"

rows = []

with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        rows.append(r)

cards = []

for r in rows:

    cards.append(f"""
    <div class='window'>

        <div class='title'>
            {r['window']}
        </div>

        <table>
            <tr><td>stable</td><td>{r['stable_count']}</td></tr>
            <tr><td>middle</td><td>{r['middle_count']}</td></tr>
            <tr><td>residual</td><td>{r['residual_count']}</td></tr>
            <tr><td>new rough families</td><td>{r['new_rough_families']}</td></tr>
            <tr><td>returning rough families</td><td>{r['returning_rough_families']}</td></tr>
            <tr><td>disappearing rough families</td><td>{r['disappearing_rough_families']}</td></tr>
            <tr><td>stable-edge forms</td><td>{r['stable_edge_forms']}</td></tr>
        </table>

    </div>
    """)

html = f"""
<html>

<head>

<meta charset='utf-8'>

<style>

body {{
    background:#0b0f14;
    color:#eee;
    font-family:Segoe UI;
    padding:24px;
}}

.window {{
    display:inline-block;
    vertical-align:top;
    width:220px;
    margin-right:12px;
    margin-bottom:12px;
    background:#111820;
    border:1px solid #2c3945;
    border-radius:8px;
    padding:12px;
}}

.title {{
    font-weight:600;
    margin-bottom:10px;
}}

td {{
    padding:3px 10px 3px 0;
}}

.boundary {{
    color:#999;
    margin-bottom:24px;
}}

</style>

</head>

<body>

<h1>Temporal Strata Prototype V0</h1>

<div class='boundary'>
Observer-only sediment exposure across bounded windows.
No causality, prediction, lifecycle, or anomaly inference.
</div>

{''.join(cards)}

</body>
</html>
"""

out_html = OUT / "TEMPORAL_STRATA_V0.html"

with open(out_html, "w", encoding="utf-8") as f:
    f.write(html)

print("")
print("=== TEMPORAL STRATA HTML COMPLETE ===")
print(out_html)
