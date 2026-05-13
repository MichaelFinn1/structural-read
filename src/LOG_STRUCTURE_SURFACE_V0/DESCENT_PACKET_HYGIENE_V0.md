# DESCENT_PACKET_HYGIENE_V0

Status: active_method_note

## Purpose

This note defines packet hygiene for bounded reread containers.

Packets are not knowledge objects.
Packets are not incidents.
Packets are not entities.
Packets are not interpretations.

Packets are bounded reread chambers.

## Validator boundary

Test-DescentPacket.V0.ps1 validates traversal conditions only.

It checks:
- packet folder exists
- README exists
- RETURN_READ exists
- evidence files exist
- manifest row exists
- source_read_id exists
- boundary exists
- status is allowed

It does not judge:
- correctness
- meaning
- anomaly
- causality
- importance
- truth
- interpretation quality

## Allowed traversal statuses

open
banked_reread
revised
stopped
invalidated

Graceful invalidation is lawful.

A packet may fail to survive reread without being treated as error.

## Packet index role

DESCENT_PACKET_INDEX_V0.csv is a reread ledger.

It preserves:
- claim before
- claim after
- unresolved scale behavior
- unresolved attachment structure
- unresolved middle distribution
- decision

It is not:
- ontology
- ranking table
- incident list
- semantic registry
- knowledge graph

## Current hold

Validate the corridor, not the conclusion.

Strengthen traversal conditions before sending another read through them.
