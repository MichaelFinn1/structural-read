# RECEIPT_012_FOCUS_CANDIDATE_ZONES_V57C

Status: COMPLETED
Packet: PACKET_012_FOCUS_CANDIDATE_ZONES_V57C
Result: PASS

## Movement

Implemented and ran V57C candidate-zone grouping on OpenStack and Linux.

V57C groups adjacent active localization bins into candidate zones.

## Files created

- tools/Build-FocusCandidateZones.V57C.py
- src/LOG_STRUCTURE_SURFACE_V0/long_duration_packets/openstack_long_horizon_001/measured/focus_candidate_zones_v0.csv
- src/LOG_STRUCTURE_SURFACE_V0/long_duration_packets/linux_long_horizon_001/measured/focus_candidate_zones_v0.csv

## OpenStack output

Candidate zones:
- 53

Observed shape:
- broad distributed deformation geography
- many distributed corridors
- several mixed zones
- scattered localized points

## Linux output

Candidate zones:
- 6

Observed shape:
- fewer, more separated zones
- localized/mixed pockets rather than broad distributed spread

## Evidence value

V57C behaves consistently with V57B2 localization.

OpenStack remains broad/distributed.
Linux remains sparse/localized.

This supports the sequence:

constitution surface
-> deformation surface
-> localization
-> candidate grouping

## Boundary

These are candidate zones, not basins.

No basin claims.
No best-focus claims.
No anomaly or root-cause language.
No UI changes.
No recommendations.

## Open unresolveds

- Candidate type counts should be inspected before widening.
- Whether V57C should run across all terrains.
- Whether small-bin terrains need separate handling.
- Whether candidate-zone grouping should be exposed in UI later.

## Stop condition

V57C OpenStack/Linux probe banked.
Stop before widening.
