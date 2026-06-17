# ADAPTER_SATURATION_READ_V0

Status:
banked

## Purpose

Record the adapter-fit issue exposed by the matched infant/adult RR panels.

## Current finding

The adult short panel did not simply fail to contact.

The adult records saturated the RR magnitude axis of the adapter.

## Original adapter buckets

rr_short:

- below 410

rr_mid:

- 410 to 450

rr_long:

- above 450

## Observed RR means

Infant panel:

- 4000: mean 433.27
- 4001: mean 437.41
- 4002: mean 451.67

Adult panel:

- 003: mean 703.71
- 005: mean 706.03
- 008: mean 778.48

## Adapter occupancy result

Infant records occupied all three RR buckets.

Adult records occupied almost entirely rr_long.

Adult RR bucket counts:

003:

- rr_short: 49
- rr_mid: 5
- rr_long: 49946

005:

- rr_short: 20
- rr_mid: 32
- rr_long: 49948

008:

- rr_short: 0
- rr_mid: 2
- rr_long: 49998

## Read

The adult records still showed delta variation.

The adult records did not activate the RR magnitude axis under the original adapter.

Therefore the apparent infant/adult contact difference is confounded by adapter saturation.

## Boundary

Do not treat adult non-contact as age effect.

Do not treat adult non-contact as physiology effect.

Do not treat saturation as absence of structure.

Do not retune thresholds inside this result.

Do not erase the original adapter result.

## Current distinction

Source structure is not adapter visibility.

Adapter visibility is not observer admissibility.

The adapter itself has contact geometry.

## Next stance

Create an adapter occupancy surface for the existing six 50000-line members.

Then, if needed, open a new adapter-variant packet with declared thresholds or within-member normalization.
