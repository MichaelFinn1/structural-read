# ACQUISITION_021A_TEMPORAL_SOURCE_V0

Status:
selected

## Source

PhysioNet:
RR interval time series from healthy subjects

## Source page

https://physionet.org/content/rr-interval-healthy-subjects/1.0.0/

## Reason selected

This source provides RR interval time series as text files.

It supplies recurrence with internal variation while avoiding ECG waveform complexity.

## Pressure class

cyclicity_with_internal_variation

## What is intentionally ignored

No physiology interpretation.

No health interpretation.

No diagnosis.

No demographic interpretation.

No comparison between subjects.

## Intended first contact

Choose one small ID.txt member.

Adapt RR intervals into line-native morphology.

Run unchanged apparatus.

## Boundary

The adapter may expose interval relation.

The adapter may not import health, stress, recovery, pathology, or cycle labels.
