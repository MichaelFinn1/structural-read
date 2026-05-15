import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path("comparison_packets/traversal_comparison_surface_001")
OUT  = Path("comparison_packets/terrain_map_reread_v0")

df = pd.read_csv(
    ROOT / "traversal_comparison_surface_v0.csv"
)

fig, ax = plt.subplots(figsize=(10, 7))

x = df["avg_residual_share"]
y = df["avg_residual_stable_attachment"]

ax.scatter(x, y)

for _, row in df.iterrows():

    ax.text(
        row["avg_residual_share"] + 0.01,
        row["avg_residual_stable_attachment"] + 0.01,
        row["terrain"],
        fontsize=9
    )

ax.set_xlabel("Residual Share")
ax.set_ylabel("Residual Stable Attachment")

ax.set_title(
    "Six-Terrain Traversal Field V0"
)

ax.grid(True)

out_path = OUT / "terrain_field_scatter_v0.png"

plt.savefig(
    out_path,
    bbox_inches="tight"
)

print("")
print("WROTE")
print(out_path.resolve())
print("")
