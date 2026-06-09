# PACKET_010_BUILD_FOCUS_LADDER_SURFACE_V57A

Status: BUILD
Layer: Contact
Primary Mode: Runner
Secondary Mode: Observer

## Purpose

Implement the first CSV-only focus ladder surface.

V57A should produce focus_ladder_surface_v0.csv only.

## Allowed movement

- Create tools/Build-FocusLadderSurface.V57A.py
- Read one existing traversal-window CSV
- Filter explicit focus sizes
- Derive dominant_posture
- Derive posture_mix_count
- Derive simple legibility_class
- Derive simple band_sequence per focus_size
- Write focus_ladder_surface_v0.csv
- Print row count and missing focus sizes

## Forbidden movement

- No UI changes
- No transition surface yet
- No candidate zones yet
- No raw-log parsing unless required
- No changes to V55 or V56 scripts
- No anomaly/root-cause/best-focus language
- No recommendations
- No automatic navigation

## Required input columns

- window_size
- line_start
- line_end
- stable_share
- middle_share
- residual_share

## Output fields

- terrain_id
- focus_size
- window_id
- line_start
- line_end
- stable_share
- middle_share
- residual_share
- dominant_posture
- seam_count
- posture_mix_count
- legibility_class
- band_sequence

## Closure boundary

Script created.
One known traversal-window CSV processed.
Output inspected lightly.
Receipt written.
Stop before V57B.
