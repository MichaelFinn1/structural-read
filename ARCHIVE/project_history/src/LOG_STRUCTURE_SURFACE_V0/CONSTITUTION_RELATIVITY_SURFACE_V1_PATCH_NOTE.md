# CONSTITUTION_RELATIVITY_SURFACE_V1_PATCH_NOTE

Status:
compatibility_patch

## What happened

The first constitution relativity surface works for full traversal outputs with:

- window_size
- line_start
- line_end
- stable_share
- middle_share
- residual_share

It correctly failed on lynx_hare_cycle_001 because lynx is not yet a windowed traversal surface.

It also failed on collapse_terrain_001 because that packet currently has summary rows without line_start / line_end.

## Correction

V1 now tolerates summary-only traversal rows by assigning minimal synthetic line bounds.

## Boundary

Lynx still requires a natural-cycle windowing adapter before constitution relativity is lawful.

## Hold

Do not force non-windowed natural data into traversal tools.
Adapt the natural substrate first.
