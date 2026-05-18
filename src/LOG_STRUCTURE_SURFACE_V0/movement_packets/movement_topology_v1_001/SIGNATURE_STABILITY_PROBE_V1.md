# SIGNATURE_STABILITY_PROBE_V1

Status:
planned_stability_probe_surface

## Purpose

This surface does not add new grammar.

It defines bounded reread probes for testing whether existing grammar signatures remain recoverable under procedural variation.

## Current probes

zone_shift_probe:
Does the signature survive slight zone boundary movement?

constitution_density_probe:
Does the signature survive denser or sparser constitution ladders?

extraction_threshold_probe:
Does the signature survive slightly different interval extraction assumptions?

terrain_comparison_probe:
Does the signature appear in other terrains under the same reread law?

## Boundary

This is not a classifier.
This is not optimization.
This is not automatic grammar discovery.

A signature may weaken, fail, or remain constitution-local.

## Hold

Strengthen signatures through replay variation, not conceptual expansion.
