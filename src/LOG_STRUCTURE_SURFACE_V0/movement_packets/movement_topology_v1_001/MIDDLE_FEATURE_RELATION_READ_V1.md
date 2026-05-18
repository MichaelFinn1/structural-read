# MIDDLE_FEATURE_RELATION_READ_V1

Status:
merge_split_aware_relation_surface

## Purpose

This surface compares middle feature intervals across adjacent observational constitutions.

It replaces nearest-center motion with interval-overlap relations.

## Core correction

The surface does not prove feature identity.

It records whether middle intervals:

- continue
- widen
- thin
- split
- merge
- appear
- disappear
- reconstitute
- remain ambiguous

under constitution change.

## Method

Each middle feature is treated as an interval:

middle_start → middle_end

Adjacent constitutions are compared by overlap:

50→75
75→100
100→150
150→200
200→250
250→350
350→500
500→750
750→1000

## Boundary

A relation is not an object trajectory.

A relation is not a semantic event.

A relation is not a causal explanation.

Large movement without overlap should be treated as reconstitution or ambiguity, not identity.

## Hold

Track recomposition before claiming motion.
