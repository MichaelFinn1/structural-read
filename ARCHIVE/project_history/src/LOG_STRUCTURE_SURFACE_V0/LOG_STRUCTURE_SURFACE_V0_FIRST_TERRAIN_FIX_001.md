# LOG_STRUCTURE_SURFACE_V0_FIRST_TERRAIN_FIX_001.md

Status: first_real_terrain_fix

## Issue

First real terrain run failed with:

Argument types do not match

## Cause

The initial reducer used a generic .NET object list in a way that triggered a PowerShell binder issue during grouping/reduction.

## Fix

Regenerated Run-LogStructureSurface.V0.ps1 using plain PowerShell arrays and explicit scalar casts.

## Boundary

No new analysis.
No interpretation.
No anomaly detection.
No severity scoring.

## One-line hold

Fix the runner; do not widen the product claim.
