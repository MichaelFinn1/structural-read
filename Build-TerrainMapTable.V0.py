import pandas as pd
from pathlib import Path

ROOT = Path("comparison_packets/traversal_comparison_surface_001")
OUT  = Path("comparison_packets/terrain_map_reread_v0")

df = pd.read_csv(
    ROOT / "traversal_comparison_surface_v0.csv"
)

cols = [
    "terrain",
    "avg_residual_share",
    "avg_middle_share",
    "avg_residual_self_adjacent",
    "avg_residual_stable_attachment",
    "dominant_posture"
]

df = df[cols]

df = df.sort_values(
    by="avg_residual_share",
    ascending=True
)

out_path = OUT / "terrain_map_table_v0.csv"

df.to_csv(out_path, index=False)

print("")
print("WROTE")
print(out_path.resolve())
print("")
