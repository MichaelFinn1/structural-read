# RECEIPT_011D_FOCUS_TRANSITION_LOCALIZATION_V57B2

Status: COMPLETED
Packet: PACKET_011_FOCUS_TRANSITION_SURFACE_V57B
Result: PASS

## Movement

Implemented and ran V57B2 focus transition localization surface on OpenStack and Linux.

V57B2 localizes non-persisted deformation events into line-territory bins.

## Files created

- tools/Build-FocusTransitionLocalization.V57B2.py
- src/LOG_STRUCTURE_SURFACE_V0/long_duration_packets/openstack_long_horizon_001/measured/focus_transition_localization_v0.csv
- src/LOG_STRUCTURE_SURFACE_V0/long_duration_packets/linux_long_horizon_001/measured/focus_transition_localization_v0.csv

## OpenStack localization

Rows:
- 275

Localization classes:
- distributed_low: 138
- quiet: 119
- localized_deformation: 18

## Linux localization

Rows:
- 52

Localization classes:
- quiet: 38
- localized_deformation: 10
- distributed_low: 4

## Observer read

OpenStack deformation is more distributed across the terrain.

Linux deformation is more sparse, with a higher proportion of localized deformation among non-quiet bins.

## Evidence value

V57B2 confirms that terrain-level deformation profiles are not enough.

Localization distinguishes whether deformation is distributed, quiet, or concentrated.

This supports the sequence:

constitution surface
-> deformation surface
-> deformation localization
-> candidate grouping later

## Boundary

This is an observer-side localization surface.

No candidate zones.
No basin claims.
No best-focus claims.
No anomaly or root-cause language.
No UI changes.

## Open unresolveds

- Whether V57B2 should be run across all terrains.
- Whether bin-size 500 is adequate.
- Whether candidate grouping should operate on localization bins rather than raw transition events.
- Whether corridor refinement should target localized_deformation bins first.

## Stop condition

V57B2 OpenStack/Linux probe banked.
Stop before V57C.
