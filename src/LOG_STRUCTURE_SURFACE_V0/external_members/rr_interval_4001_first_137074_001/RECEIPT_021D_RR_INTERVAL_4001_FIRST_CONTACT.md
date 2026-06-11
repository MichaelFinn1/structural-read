# RECEIPT_021D_RR_INTERVAL_4001_FIRST_CONTACT

Status:
COMPLETED

Result:
SPARSE_CONTACT

## Movement

Processed a second PhysioNet RR interval member through the same declared temporal ecology adapter and unchanged V57/V58 observer chain.

## Source

PhysioNet RR interval time series from healthy subjects.

Source member:

4001.txt

Bounded member:

rr_interval_4001_first_137074_001

## Adapter

Same adapter class as rr_interval_4000_first_137074_001.

Exposed line-native fields:

- rr_short / rr_mid / rr_long
- delta_down / delta_flat / delta_up

The adapter did not expose:

- physiology meaning
- health labels
- stress labels
- recovery labels
- diagnosis
- subject comparison
- cycle labels

## Pipeline

Unchanged observer chain:

- Build-TraversalWindowsFromLog.V1.py
- Build-FocusLadderSurface.V57A.py
- Build-FocusTransitionSurface.V57B.py
- Build-FocusTransitionLocalization.V57B2.py
- Build-FocusCandidateZones.V57C.py
- Build-InterZoneGeometryObservables.V58G2.py

## Result

Localization:

- quiet: 203
- distributed_low: 72

Candidate types:

- distributed_corridor_candidate: 42

Inter-zone geometry:

- candidate_count: 42
- quiet_gap_count: 41
- candidate_span_ratio: 0.262632
- largest_quiet_gap: 8500

## Observer read

RR interval 4001 produced sparse observer contact.

This replicates temporal ecology contact under the same adapter, but with a stronger contact profile than RR interval 4000.

RR interval 4000:

- candidate_count: 9
- candidate_span_ratio: 0.032829

RR interval 4001:

- candidate_count: 42
- candidate_span_ratio: 0.262632

Current read:

temporal ecology contact is not a one-off artifact, but member-level variation is substantial.

## Boundary

No physiology interpretation.

No health claim.

No diagnosis.

No stress or recovery claim.

No apparatus tuning.

No detector.

No ontology growth.

No claim that this is a heartbeat law.

No subject comparison.

## Current stance

Temporal ecology first contact has now replicated under the same adapter.

Next safe move is a small two-member comparison read before adding more members.
