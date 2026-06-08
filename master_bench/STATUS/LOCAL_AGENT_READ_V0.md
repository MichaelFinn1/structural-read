# LOCAL_AGENT_READ_V0

Status: PROBE
Packet: PACKET_003A_LOCAL_AGENT_ADHERENCE_V0

## Current local model read

DeepSeek Coder 6.7B:
- Result: FAIL_FRAME_MISMATCH
- Best use: code-only later, not bench-orientation yet

OpenHermes:
- Result: PASS_WITH_MINOR_SCHEMA_LOSS
- Best use: current default local bench-orientation model

Qwen2.5-Coder 3B:
- Result: PASS_WITH_SCHEMA_COMPRESSION
- Best use: possible local code probe; secondary bench option

## Current default

Use OpenHermes for local bench-orientation probes.

## Boundary

Do not install or compare more models until a real packet requires it.

## Current question

Can one local model support bounded bench orientation well enough to reduce reliance on remote models?
