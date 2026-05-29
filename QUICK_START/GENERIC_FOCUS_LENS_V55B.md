# GENERIC_FOCUS_LENS_V55B

Status: usable_generic_focus_lens_builder

## Purpose

V55B is the first generic focus lens builder.

It no longer presents itself as an OpenStack-only viewer.

It accepts generic input paths and labels while preserving the current focus-lens workbench behavior.

## Current builder

src/LOG_STRUCTURE_SURFACE_V0/long_duration_packets/openstack_long_horizon_001/Build-OpenStackGlobalFocusLens.V55B_GenericLabels.py

## Example usage

Replace the input paths with your own generated structure CSV and raw log file.

python .\src\LOG_STRUCTURE_SURFACE_V0\long_duration_packets\openstack_long_horizon_001\Build-OpenStackGlobalFocusLens.V55B_GenericLabels.py --structure-csv .\path\to\traversal_windows_v0.csv --raw-log .\path\to\raw_log.txt --out-html .\path\to\focus_lens.html

## Important boundary

This is not yet a complete raw-log ingestion workflow.

The structure CSV must already exist.

Current path:

generated structure CSV + raw log -> focus lens HTML

Not yet fully documented:

raw log -> structure CSV -> focus lens HTML

## Hold

V55B is the generic lens floor.

The next packaging need is a simple wrapper that produces the required structure CSV from a raw log.
