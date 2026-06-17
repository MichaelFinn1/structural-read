# TRAVERSAL_SESSION_SUMMARY_V0

Status:
compact_replay_handoff_surface

## Purpose

This reader summarizes one traversal replay id into a compact handoff row.

It does not interpret the traversal.

It preserves:

- first span
- last span
- movement count
- marker sequence
- relation sequence
- legibility sequence
- one plain summary line

## Boundary

This is not a recommender.

It does not score movement.

It does not infer the best lens.

It only compresses manual traversal provenance into a readable handoff surface.

## Hold

Session summaries preserve movement memory without replacing reread.
