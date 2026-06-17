# START_HERE_LOG_STRUCTURE_V0.md

Status: log_structure_surface_start_here

## What this is

Log Structure Surface V0 is a bounded operational-log readability tool.

It reduces noisy logs into:

- stable repeated templates
- middle recurrence
- residual lines

It does not detect incidents or recommend action.

## Basic command

Run:

.\Run-LogStructureSurface.V0.ps1 -Path "<log file or folder>"

Example:

.\Run-LogStructureSurface.V0.ps1 -Path "C:\Users\Admin\Desktop\SomeLogs"

## Drag-and-drop

Drag a log file or folder onto:

Run-LogStructure.Drop.bat

## Outputs

Inside the inspected folder:

_surface_work\log_structure_v0\

Or, for a single file:

_surface_work\log_structure_v0\<file_name>\

Open first:

LOG_STRUCTURE_READ_V0.md

CSV outputs:

- log_line_template_index.csv
- log_template_surface.csv
- log_class_summary.csv

## What this does not do

It does not:

- infer cause
- detect incidents
- rank severity
- recommend action
- classify security events
- claim anomaly status

## One-line hold

Run it on logs; get structure out; human keeps judgment.
