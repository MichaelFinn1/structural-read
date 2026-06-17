# RUN_CONTACT_PACKET_V0_README

Status:
active

## Purpose

Run a declared Structural Read contact packet through the unchanged V57/V58 chain.

The wrapper reduces orchestration friction and preserves provenance.

It does not make judgments.

## Inputs

- TerrainId
- SourceLog
- MemberRoot
- AdapterId
- ObserverConstitutionId
- TerritoryStart
- TerritoryEnd
- BinSize
- WindowSizes

## Outputs

Under MemberRoot/measured:

- traversal_windows_v0.csv
- focus_ladder_surface_v0.csv
- focus_transition_surface_v0.csv
- focus_transition_localization_v0.csv
- focus_candidate_zones_v0.csv
- inter_zone_geometry_observables_v0.csv

Under MemberRoot:

- CONTACT_PACKET_RUN_RECEIPT_V0.md

## Boundary

The wrapper may execute.

The wrapper may summarize.

The wrapper may preserve provenance.

The wrapper may not:

- choose terrain
- choose adapter
- choose observer settings
- interpret result
- promote distinction
- select next move
- tune apparatus
- widen investigation

## Compression

Runner wrapper, not judgment wrapper.
