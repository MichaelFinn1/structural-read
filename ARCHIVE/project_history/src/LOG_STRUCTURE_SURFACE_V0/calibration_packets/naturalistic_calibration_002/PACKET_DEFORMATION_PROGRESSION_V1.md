# PACKET_DEFORMATION_PROGRESSION_V1

Status:
observer_surface_open

## Purpose

This surface reads how ordered residual bands change across traversal under one fixed constitution.

Current constitution:

- window_size = 125

## What it tracks

- packet order
- packet width
- width class
- gap from previous
- width delta from prior
- gap delta from prior
- coarse deformation from prior

## What it does not track

This surface does not infer:

- identity
- causality
- semantic meaning
- lifecycle
- true motion
- source process

## Boundary

A later packet that resembles an earlier packet is not treated as the same object.

A width change is not treated as degradation or improvement.

A spacing change is not treated as movement intention.

All reads remain observer-side.

## Hold

Track packet deformation across traversal before naming packet grammar.
