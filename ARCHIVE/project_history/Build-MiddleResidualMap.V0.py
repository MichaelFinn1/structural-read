import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path("comparison_packets/traversal_comparison_surface_001")
OUT  = Path("comparison_packets/terrain_map_reread_v0")

df = pd.read_csv(
    ROOT / "traversal_comparison_surface_v0.csv"
)

fig, ax = plt.subplots(figsize=(10, 7))

x = df["avg_middle_share"]
y = df["avg_residual_self_adjacent"]

ax.scatter(x, y)

for _, row in df.iterrows():

    ax.text(
        row["avg_middle_share"] + 0.003,
        row["avg_residual_self_adjacent"] + 0.003,
        row["terrain"],
        fontsize=9
    )

ax.set_xlabel("Middle Share")
ax.set_ylabel("Residual Self Adjacency")

ax.set_title(
    "Middle Participation vs Residual Continuity"
)

ax.grid(True)

out_path = OUT / "middle_vs_residual_continuity_v0.png"

plt.savefig(
    out_path,
    bbox_inches="tight"
)

print("")
print("WROTE")
print(out_path.resolve())
print("")
