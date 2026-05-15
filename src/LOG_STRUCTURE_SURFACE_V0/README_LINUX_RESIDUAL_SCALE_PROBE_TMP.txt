import csv
from pathlib import Path

src = Path("linux_residual_temporal_001_out/linux_residual_temporal_windows_v0.csv")

# This builder expects the existing Build-LinuxResidualTemporalTraverse.V0.py
# to be temporarily expanded by changing WINDOWS there.
# So here we only bank the scale probe note after rerun.

print("Use the next command block to update WINDOWS in the builder, rerun it, then inspect output.")
