# STATUS.md

Status: V0

The Master Bench uses status to prevent task-list collapse.

## Status grammar

BUILD
- Something is being formed.
- Evidence is not yet expected to be mature.

PROBE
- A bounded test is underway.
- Evidence conditions must be declared.

HOLD
- The packet remains present but is not active.
- Unresolvedness is preserved.

USE
- The packet is stable enough for ordinary reuse.
- Still subject to reread.

FROZEN
- The floor is banked and should not be modified casually.
- Branch from it rather than editing it.

ARCHIVED
- Preserved for inheritance or history.
- Not active.

## Required packet declarations

Each packet should eventually declare:
- current status
- layer
- primary mode
- secondary mode
- allowed movement
- forbidden movement
- evidence signals
- closure boundary
- unresolveds

## Boundary

Status is not authority.
Status preserves continuity posture.
