# RR_ADAPTER_OCCUPANCY_READ_V0

Status:
banked

## Purpose

Record adapter occupancy across the matched 50000-line RR infant/adult panels.

## Surface

rr_adapter_occupancy_surface_v0.csv

## Members

Infant panel:

- 4000
- 4001
- 4002

Adult panel:

- 003
- 005
- 008

## Shared conditions

All members used:

- first 50000 intervals
- same RR interval source family
- same interval-relation adapter
- same V57/V58 observer chain
- no apparatus tuning

## Main result

The infant panel occupied all RR magnitude buckets.

The adult panel almost entirely saturated rr_long.

## RR magnitude occupancy

Infant:

4000:

- rr_short_ratio: 0.36736
- rr_mid_ratio: 0.32250
- rr_long_ratio: 0.31014

4001:

- rr_short_ratio: 0.34050
- rr_mid_ratio: 0.35156
- rr_long_ratio: 0.30794

4002:

- rr_short_ratio: 0.25410
- rr_mid_ratio: 0.21962
- rr_long_ratio: 0.52628

Adult:

003:

- rr_short_ratio: 0.00098
- rr_mid_ratio: 0.00010
- rr_long_ratio: 0.99892

005:

- rr_short_ratio: 0.00040
- rr_mid_ratio: 0.00064
- rr_long_ratio: 0.99896

008:

- rr_short_ratio: 0.00000
- rr_mid_ratio: 0.00004
- rr_long_ratio: 0.99996

## Delta occupancy

The adult panel did not collapse completely.

Delta buckets remained active across adult members.

This means adult records retained adjacent-interval variation, but the RR magnitude axis was nearly constant under the original adapter.

## Observer read

The apparent infant/adult contact difference is confounded by adapter saturation.

The original adapter made adult RR magnitude almost invisible as a differentiating axis.

Current read:

infant panel activated RR magnitude and delta axes.

adult panel activated delta axis but saturated RR magnitude axis.

## Boundary

No age effect claim.

No physiology claim.

No health claim.

No diagnosis.

No subject interpretation.

No claim that adults lack rhythmic variation.

No threshold retuning inside this result.

## Current stance

This is an adapter-fit discovery.

The next lawful move is a new adapter-variant packet, not correction of the original result.

Any new adapter must be declared as a variant and compared against the original adapter.
