# TRAVERSAL_STATUS_DISCIPLINE_V0

Status: active_method_note

## Purpose

This note stabilizes traversal status meanings for descent packets.

Traversal statuses describe reread state,
not truth state.

They do not encode:
- correctness
- semantic validity
- operational certainty
- anomaly severity
- interpretation quality

They encode:
- reread continuity
- survivability under descent
- bounded continuation state

## Allowed traversal statuses

### open

Packet exists and reread is still in progress.

No bounded reread conclusion yet.

### banked_reread

Packet completed at least one lawful reread cycle.

A bounded reread outcome exists.

The packet remains revisitable.

### revised

Original higher read weakened or changed under descent.

Packet survived through refinement rather than confirmation.

### stopped

Packet intentionally paused.

Not invalidated.
Not concluded.

Traversal halted without promotion.

### invalidated

Packet failed to survive reread pressure sufficiently
to preserve the original higher read.

Invalidation is lawful.

Invalidation is not error.

Invalidation preserves:
- descent evidence
- reread history
- provenance continuity
- unresolved continuation possibility

## Continuability

A packet may continue lawfully after weakening.

Continuation does not require:
- confirmation
- strengthening
- stable ontology
- semantic closure

Continuation requires:
- preserved provenance
- preserved descent path
- preserved reread recoverability
- explicit unresolved structure

## Current hold

Traversal status tracks lawful reread movement,
not semantic truth.
