# RECEIPT_011F_LOCALIZATION_BINSIZE_SENSITIVITY_V57B2

Status: COMPLETED
Packet: PACKET_011_FOCUS_TRANSITION_SURFACE_V57B
Result: PASS

## Movement

Ran V57B2 bin-size sensitivity check on OpenStack and Linux.

Tested bin sizes:
- 250
- 500
- 1000

## Output created

- src/LOG_STRUCTURE_SURFACE_V0/focus_transition_localization_binsize_sensitivity_v0.csv

## OpenStack read

OpenStack remains broadly active across bin sizes.

Active share:
- 250: 0.3661
- 500: 0.5673
- 1000: 0.7536

Pattern:
- distributed_low remains the dominant active class
- active share rises as bins widen

## Linux read

Linux remains more quiet/localized than OpenStack across bin sizes.

Active share:
- 250: 0.1942
- 500: 0.2692
- 1000: 0.3462

Pattern:
- quiet remains dominant
- localized pockets remain visible
- dense bins appear at 1000, likely due to larger-bin aggregation

## Evidence value

The broad OpenStack/Linux contrast survives bin-size variation.

Bin size affects apparent density and active_share, but does not erase the terrain distinction.

## Boundary

This is sensitivity checking, not candidate-zone grouping.

No basin claims.
No best-focus claims.
No anomaly or root-cause language.
No UI changes.

## Open unresolveds

- Which bin size should be default for V57C if grouping begins.
- Whether V57C should accept bin-size as explicit parameter.
- Whether candidate grouping should preserve bin-size provenance.
- Whether small terrains need separate handling.

## Stop condition

Bin-size sensitivity check banked.
Stop before V57C.
