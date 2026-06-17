# RECEIPT_017B_INTER_ZONE_GEOMETRY

Status: COMPLETED
Result: PASS

## Movement

PACKET_017A showed that candidate-zone internal geometry was flat because V57C groups contiguous active bins.

PACKET_017B shifted the geometry read outward, from inside candidate zones to spacing between candidate zones across each slice.

## Files created

- tools/Build-InterZoneGeometryObservables.V58G2.py
- src/LOG_STRUCTURE_SURFACE_V0/inter_zone_geometry_panel_v0.csv

## Earned read

Apache baseline:
- one candidate per slice
- high candidate_span_ratio
- no inter-zone quiet gaps
- compact / near-whole-slice occupation under this read

Linux:
- low candidate count
- one fully quiet slice
- large quiet gaps where occupied
- sparse / intermittent occupation under this read

OpenStack:
- high candidate count
- many inter-zone quiet gaps
- substantial candidate_span_ratio
- broad but broken occupation under this read

## Boundary

No new labels.
No geometry families.
No basin claims.
No anomaly claims.
No movement, flow, trajectory, or causality claims.

## Current result

The visually interesting geometry is primarily inter-zone geometry, not candidate-internal geometry.

## Next safe question

Can independent observer reads of geometry converge on the same descriptions before any new vocabulary is formalized?
