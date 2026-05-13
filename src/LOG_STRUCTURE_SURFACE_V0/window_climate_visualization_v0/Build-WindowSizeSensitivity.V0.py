import csv
from pathlib import Path

FILES = [
    ("250", "WINDOW_CLIMATE_SEQUENCE_250.csv"),
    ("500", "WINDOW_CLIMATE_SEQUENCE_500.csv"),
    ("1000", "WINDOW_CLIMATE_SEQUENCE_1000.csv"),
]

rows_out = []

for label, path in FILES:
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    pulses = [
        r for r in rows
        if r["local_topology"] == "localized_inversion_basin"
    ]

    max_edge_margin = max(float(r["edge_margin"]) for r in rows)
    max_middle = max(float(r["middle_share"]) for r in rows)
    max_diversity = max(float(r["diversity_share"]) for r in rows)

    pulse_ranges = "; ".join(
        f"{r['line_start']}-{r['line_end']}"
        for r in pulses
    )

    rows_out.append({
        "window_size": label,
        "windows": len(rows),
        "localized_inversion_basins": len(pulses),
        "pulse_line_ranges": pulse_ranges,
        "max_edge_margin": round(max_edge_margin, 3),
        "max_middle_share": round(max_middle, 3),
        "max_diversity_share": round(max_diversity, 3),
    })

out = Path("WINDOW_SIZE_SENSITIVITY_V0.csv")

with open(out, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
    writer.writeheader()
    writer.writerows(rows_out)

print("")
print("=== WINDOW SIZE SENSITIVITY COMPLETE ===")
print(out.resolve())
