# RECEIPT_003A_OPENHERMES_LOCAL_AGENT_ADHERENCE_V0

Status: PROBE
Packet: PACKET_003A_LOCAL_AGENT_ADHERENCE_V0
Capability Source: Ollama / openhermes:latest
Result: PASS_WITH_MINOR_SCHEMA_LOSS

## Movement

Tested whether a local Ollama general model could enter the Master Bench frame and return a bounded response under packet constraints.

## Model response summary

The model entered the requested frame and returned the requested boundary-response structure.

It identified:
- active packet
- frozen floors
- unresolved conclusion boundary

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

Minor schema loss:
- Stop line was omitted.
- Open unresolveds were returned as N/A despite unresolveds being present in the prompt.
- "What cannot be concluded" included a mild interpretive sentence rather than a pure field value.

## What this suggests

openhermes:latest is more suitable than deepseek-coder:6.7b for bench-frame adherence.

For local models, general instruction-following may matter more than coding specialization during orientation tasks.

## Evidence value

Useful positive result.

Local capability can enter Master Bench framing under explicit constraints, but schema adherence remains imperfect.

## Open unresolveds

- Whether a stricter prompt improves schema adherence.
- Whether openhermes can perform a bounded file-content generation task.
- Whether deepseek-coder should be reserved for code-only tasks.

## Stop condition

Packet 003A second probe receipted.

Do not widen into agent infrastructure yet.
