# Structural Read

Structural Read is a local-first structural readability tool.

It helps orient messy logs and data folders before analysis by exposing repeated, middle, and residual structure without assigning causes, severity, incidents, or recommendations.

Current slice:

- LOG_STRUCTURE_SURFACE_V0
- Windows / PowerShell first
- CSV, Markdown, and HTML outputs
- local folder input
- no cloud upload
- no anomaly scoring
- no operational interpretation

## Basic use

Go into the tool folder:

cd .\src\LOG_STRUCTURE_SURFACE_V0

Run the log structure surface on a folder:

.\Run-LogStructureSurface.V0.ps1 -Path "C:\path\to\logs"

Then open the generated read file or HTML cards in the output folder.

## Product boundary

Structural Read provides orientation before analysis.

It does not infer cause, assign identity, rank severity, detect incidents, recommend action, or replace domain expertise.

## Current status

Private V0 release candidate.

Maintainer: Michael Finn
Contact: structuralread@proton.me
