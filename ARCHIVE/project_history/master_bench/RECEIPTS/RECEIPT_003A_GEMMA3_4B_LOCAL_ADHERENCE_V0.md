# RECEIPT_003A_GEMMA3_4B_LOCAL_ADHERENCE_V0

Status: PROBE
Packet: PACKET_003A_LOCAL_AGENT_ADHERENCE_V0
Capability Source: Ollama / gemma3:4b
Result: PASS_SCHEMA_FAIL_CONTENT_GROUNDING

## Movement

Tested whether gemma3:4b could enter the Master Bench frame and return a bounded response under packet constraints.

## Model response summary

The model preserved the requested output structure cleanly.

It returned:
- Status
- What is active
- What is frozen
- What remains unresolved
- What cannot be concluded
- Stop line

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

Content grounding failure:
- It returned "What is frozen: None" despite frozen floors being supplied.
- It returned "What remains unresolved: None" despite unresolveds being supplied.
- It used "Re-entry outranks recall" as stop line, which was plausible but not grounded in requested stop behavior.

## What this suggests

Schema obedience is not bench adherence.

Bench usefulness requires both:
- boundary obedience
- supplied-context grounding

Gemma3 4B is tidy but under-grounded for this bench task.

## Evidence value

Useful contrast result.

## Stop condition

Gemma final-pass probe receipted.
Stop model shopping.
