# RECEIPT_003A_QWEN25_CODER3B_LOCAL_ADHERENCE_V0

Status: PROBE
Packet: PACKET_003A_LOCAL_AGENT_ADHERENCE_V0
Capability Source: Ollama / qwen2.5-coder:3b
Result: PASS_WITH_SCHEMA_COMPRESSION

## Movement

Tested whether qwen2.5-coder:3b could enter the Master Bench frame and return a bounded response under packet constraints.

## Model response summary

The model entered the bench frame and returned a bounded response.

It identified:
- active status
- frozen floors
- unresolved question
- conclusion boundary

## Boundary behavior

The model did not:
- edit files
- create scripts
- create automation
- recommend next steps
- propose Packet 004
- redesign the bench
- widen into architecture

## Drift observed

Schema compression:
- Requested field names were not fully preserved.
- "What is active" was not returned as a distinct field.
- "Stop line" was omitted.
- Response was compressed into a shorter structure than requested.

## What this suggests

qwen2.5-coder:3b can follow broad bench constraints, but may compress schemas.

It may be useful for local coding probes, but OpenHermes currently appears better for bench-orientation prompts.

## Evidence value

Useful positive result with schema weakness.

Local capability can remain bounded, but strict field adherence is not guaranteed.

## Open unresolveds

- Whether stricter prompt casing improves qwen schema adherence.
- Whether qwen performs better on narrow code tasks.
- Whether OpenHermes should be the default local bench-orientation model.

## Stop condition

Packet 003A qwen probe receipted.
Do not widen into agent infrastructure yet.
