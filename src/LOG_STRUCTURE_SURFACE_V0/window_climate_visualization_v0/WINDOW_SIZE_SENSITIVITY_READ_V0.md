# WINDOW_SIZE_SENSITIVITY_READ_V0

Status: observer_read_banked

## Summary

Window climate inversion is scale-sensitive.

At window size 250:
two localized inversion basins are visible.

At window size 500:
one localized inversion basin remains visible.

At window size 1000:
no localized inversion basin remains visible.

## Shared region

The strongest cross-scale region is:

37501-37750 at size 250
37501-38000 at size 500

This indicates that the late permeability event survives reslicing from 250 to 500.

## Fine-scale-only region

The region:

28001-28250

appears as a localized inversion basin at size 250 only.

Treat as fine-scale-local unless later evidence shows otherwise.

## Large-scale smoothing

At size 1000:

max_edge_margin = -0.202

So enclosure remains dominant at the larger window size.

This does not negate the smaller-scale basins.

It indicates that the inversion structure is locally strong but globally non-dominant.

## Boundary

This read describes scale-sensitive emitted participation climates.

It does not infer:
- object movement
- lifecycle
- hidden cause
- anomaly
- system intent

## Hold

Compare by source-line region, not window label.
Scale-local structure may be real without becoming globally dominant.
