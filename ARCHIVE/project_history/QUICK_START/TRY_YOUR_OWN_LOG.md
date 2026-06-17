# TRY YOUR OWN LOG

Current tested path:

1. Start with a text log file.

2. Build traversal windows:

python ".\tools\Build-TraversalWindowsFromLog.V0.py"

This produces:

traversal_windows_v0.csv

3. Build a focus lens:

python ".\src\LOG_STRUCTURE_SURFACE_V0\long_duration_packets\openstack_long_horizon_001\Build-OpenStackGlobalFocusLens.V55B_GenericLabels.py" `
  --structure-csv ".\generated\traversal_windows_v0.csv" `
  --raw-log ".\raw_log.txt" `
  --out-html ".\focus_lens.html"

4. Open:

focus_lens.html

Suggested first session:

- survey terrain
- choose a region
- descend locally
- save a card
- move elsewhere
- return using the card
