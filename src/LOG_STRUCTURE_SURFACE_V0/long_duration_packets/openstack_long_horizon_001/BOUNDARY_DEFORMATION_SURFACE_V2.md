# BOUNDARY_DEFORMATION_SURFACE_V2

Status:
overlap_multiplicity_refinement

## Purpose

V2 refines Boundary Deformation V1 by distinguishing overlap multiplicity.

V1 showed strong boundary attrition pressure, but it could overcount disappearance because best-match overlap compressed absorption, split, partial continuation, and recoloring into a single coarse read.

## What V2 adds

V2 records procedural overlap relations across adjacent constitutions:

- one_to_one_continuation
- many_to_one_absorption
- one_to_many_split
- recolored_overlap
- partial_continuation
- ambiguous_overlap
- unmatched_disappearance
- appears

## Boundary

This surface still does not infer:

- object identity
- causality
- semantic state
- anomaly
- hidden trajectory

It only records observer-side overlap multiplicity under constitution transition.

## Hold

Improve deformation accounting before adding new observer layers.
