# ADAPTER_021B_RR_INTERVAL_4000_V0

Status:
banked

## Source

PhysioNet RR interval source member:

4000.txt

## Member

rr_interval_4000_first_137074_001

## Adapter purpose

Expose line-native interval relation from RR intervals.

## Exposed fields

rr bucket:

- rr_short
- rr_mid
- rr_long

delta bucket:

- delta_down
- delta_flat
- delta_up

## What is intentionally not exposed

No physiology interpretation.

No health label.

No stress label.

No recovery label.

No diagnosis.

No subject comparison.

No cycle label.

## Boundary

The adapter exposes interval magnitude and adjacent interval change only.

It does not explain the source.

It does not promote contact into meaning.
