# START_HERE_FOR_OUTSIDERS.md

Status: outsider_entry_note

## What this is

Log Structure Surface V0 is a local-first log readability tool.

It helps you orient inside a log file or folder before deeper analysis.

It reduces logs into:

- stable repeated line structures
- middle recurrence
- residual lines
- compact summary surfaces

## What to run

From this folder:

.\Run-LogStructureSurface.V0.ps1 -Path "<log file or folder>"

Example:

.\Run-LogStructureSurface.V0.ps1 -Path "C:\Users\Admin\Desktop\LogTerrainPanel\Apache"

## What opens first

After running, open:

_surface_work\log_structure_v0\LOG_STRUCTURE_READ_V0.md

Optional visual card:

LOG_STRUCTURE_TERRAIN_CARD_V0.html

## What this does not do

It does not:

- detect incidents
- score anomalies
- rank severity
- recommend action
- explain root cause
- replace operational judgment

## Output format

Outputs are plain:

- Markdown
- CSV
- HTML card

These can be opened in ordinary tools.

## One-line hold

Logs in; structure out; human keeps judgment.
