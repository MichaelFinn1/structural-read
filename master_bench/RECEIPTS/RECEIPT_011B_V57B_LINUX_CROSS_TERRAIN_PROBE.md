# RECEIPT_011B_V57B_LINUX_CROSS_TERRAIN_PROBE

Status: COMPLETED
Packet: PACKET_011_FOCUS_TRANSITION_SURFACE_V57B
Result: PASS

## Movement

Ran V57A and V57B on linux_long_horizon_001 as a second real-log terrain.

## Files produced

- src/LOG_STRUCTURE_SURFACE_V0/long_duration_packets/linux_long_horizon_001/measured/focus_ladder_surface_v0.csv
- src/LOG_STRUCTURE_SURFACE_V0/long_duration_packets/linux_long_horizon_001/measured/focus_transition_surface_v0.csv

## Linux output

focus_ladder_surface_v0.csv rows:
- 2647

V57B transition marker counts:
- persisted: 2560
- smoothed: 31
- fragmented: 30

Dominant posture transitions:
- stable -> stable: 2278
- residual -> residual: 148
- middle -> middle: 134
- residual -> stable: 16
- middle -> stable: 13
- stable -> middle: 12
- stable -> residual: 11
- middle -> residual: 7
- residual -> middle: 2

## Cross-terrain comparison

OpenStack transition marker counts:
- persisted: 13782
- fragmented: 227
- smoothed: 22

Linux transition marker counts:
- persisted: 2560
- smoothed: 31
- fragmented: 30

## Read

Both terrains are persistence-dominant.

OpenStack shows a stronger fragmentation tail.

Linux shows a more balanced smoothed / fragmented tail.

## Boundary

This is an observer-side deformation read.

No basin claims.
No candidate-zone grouping.
No best-focus claim.
No anomaly or root-cause language.

## Evidence value

V57B now works across two real-log long-horizon terrains.

The surface is not merely generic: non-persistence profiles differ by terrain.

## Open unresolveds

- Whether V57C should group repeated deformation events now.
- Whether a third terrain should be checked first.
- Whether proportional transition summaries should be generated automatically.
- Whether corridor refinement should precede grouping.

## Stop condition

Second-terrain V57B probe banked.
Stop before V57C.
