# REPEAT_EXPOSURE_BENCH_SKETCH_V0

Status:
draft

## Purpose

Design a minimal bench for observing trace-conditioned behavior across repeated exposures.

This bench is intended to test exposure history.

It is not intended to test learning, memory, autonomy, or capability growth.

## Core question

What changes because lawful contact happened before?

## Experimental structure

Three seed tasks.

For each seed task:

- first exposure
- second exposure
- third exposure

Then:

- two near variants
- one far control

## Candidate task families

Preferred:

- bounded code repair tasks
- Structural Read packet interpretation tasks

Optional:

- Tower of Hanoi
- small procedural puzzles

## Fixed conditions

- same prompt envelope
- same execution procedure
- same comparison method

Where possible:

- same model
- same temperature
- same context discipline

## Candidate observables

- route changes
- compression changes
- stability changes
- recovery changes
- distinction preservation
- transfer behavior
- overgeneralization behavior

## Reads of interest

Repetition:

same task again

Generalization:

near variant

Transfer boundary:

far variant

## Success condition

Not improved performance.

Not better score.

Not faster completion.

Success is the ability to observe whether prior exposure alters later behavior.

## Boundary

Do not create persistent memory.

Do not modify model weights.

Do not create autonomous adaptation.

Do not create promotion rules.

Do not create scoring systems.

Do not infer learning.

Observe only trace-conditioned behavior.

## Deliverable

A comparison read describing:

- what remained stable
- what changed
- what transferred
- what remained bounded
