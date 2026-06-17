# Try Your Own Log

Status: early generic workflow

Structural Read now has a generic focus lens builder:

GENERIC_FOCUS_LENS_V55B.md

This means the focus lens can be built from:

- a generated structure CSV
- a raw log file

Current path:

generated structure CSV + raw log -> focus lens HTML

Important boundary:

The repository does not yet provide a one-command raw-log ingestion wrapper for first-time users.

That means this is not yet:

raw log -> one command -> finished lens

## What is currently possible?

If you already have a compatible structure CSV, you can build a focus lens using V55B.

See:

GENERIC_FOCUS_LENS_V55B.md

## What is not ready yet?

A simple first-user pipeline for arbitrary logs.

This still needs to be built and tested.

## Feedback wanted

If you want to try your own logs, please share:

- log type
- approximate size
- whether lines are timestamped
- what you hoped to investigate
- whether you already have a structured CSV

These attempts will shape the first clean ingestion wrapper.

## Hold

The generic lens floor is ready.

The generic ingestion path is the next packaging task.
