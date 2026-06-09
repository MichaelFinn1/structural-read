# FOCUS_LADDER_AND_BASIN_SURFACE_V0

Status: implementation_brief

## Purpose

Move Structural Read toward continuous-feeling focus exploration without implementing true continuous recomputation.

The goal is not to find the best lens.

The goal is to expose where structure becomes more or less legible as focus constitution changes.

## Core principle

Do not recompute everything live at every mouse-wheel tick.

Use:

coarse ladder
-> dense local ladder
-> corridor refinement

Each evaluated focus size remains explicit, cached, replayable, and constitution-relative.

## First implementation target

Build CSV observer surfaces before touching UI.

Do not build mouse-wheel behavior yet.

Do not build waypoint loading yet.

## Suggested focus ladder

Initial broad ladder:

25
50
75
100
125
150
175
200
225
250
300
375
500
625
750
875
1000

Later corridor refinement example:

If broad pass identifies corridor 250 -> 750, refine as:

250
300
350
400
450
500
550
600
650
700
750

## Surface 1

focus_ladder_surface_v0.csv

One row per focus size and window/span.

Suggested fields:

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

## Surface 2

focus_transition_surface_v0.csv

Compare neighboring focus sizes.

Suggested fields:

- terrain_id
- from_focus_size
- to_focus_size
- span_start
- span_end
- from_posture
- to_posture
- delta_stable
- delta_middle
- delta_residual
- delta_seam_count
- sequence_changed
- transition_marker
- note

Allowed transition markers:

- stayed_smooth
- seam_emerged
- seam_disappeared
- fragmented
- recomposed
- smoothed
- stable_expanded
- residual_expanded
- middle_expanded
- became_mixed
- became_legible
- became_unresolved

## Surface 3

focus_candidate_zones_v0.csv

Group repeated local transition events into candidate zones.

Suggested fields:

- terrain_id
- candidate_id
- span_start
- span_end
- focus_band_start
- focus_band_end
- candidate_type
- persistence_count
- transition_count
- candidate_strength
- boundary_note

Allowed candidate types:

- stable_basin_candidate
- connector_seam_candidate
- fragmentation_threshold_candidate
- recomposition_candidate
- transition_only_candidate

## Calibration labels

For each focus size, classify global terrain posture as one of:

- over_smooth
- over_fragmented
- traversable_mixed
- seam_rich
- unresolved

These are calibration labels, not recommendations.

## Critical boundaries

The system may say:

- this region changes here
- this span persists across neighboring focus sizes
- this corridor contains repeated transition events
- this focus band appears traversable

The system must not say:

- this is the correct basin
- this is the best focus
- this region matters
- this is an anomaly
- this explains the log
- this is root cause

## Implementation sequence

V1A:
Build focus_ladder_surface_v0.csv from existing traversal rows.

V1B:
Build focus_transition_surface_v0.csv by comparing adjacent focus sizes.

V1C:
Build focus_candidate_zones_v0.csv from repeated transition events.

V1D:
Only after CSVs look useful, expose candidate zones lightly in UI.

V1E:
Only after that, make mouse-wheel focus traversal use cached ladder states.

## Current hold

Build the CSV pass first.

If candidate zones look sensible offline, UI integration will be much safer.
