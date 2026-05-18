# SIGNATURE_ZONE_SHIFT_PROBE_V1

Status:
bounded_zone_variation_probe

## Purpose

This probe tests whether selected signatures depend too heavily on the current zone constitution.

It does not attempt to discover the "correct" zones.

It only tests signature survivability under small zone deformation.

## Zone constitutions

baseline:
left 1–750
null 751–1250
right 1251–2000

variant_a:
left 1–700
null 701–1300
right 1301–2000

variant_b:
left 1–800
null 801–1200
right 1201–2000

## Current probe signatures

- carrier_persistence
- local_symmetry_pocket
- null_zone_respect

## Change vocabulary

survives:
signature remains procedurally supported

weakens:
signature support decreases under replay

relocates:
signature shifts constitutionally under zoning

dissolves:
signature loses recoverable support

ambiguous:
support remains insufficient or mixed

## Boundary

Zone shift is not optimization.

Zone shift is not topology discovery.

Zone shift is bounded reread deformation testing.

## Hold

Test whether signatures survive replay variation before extending grammar.
