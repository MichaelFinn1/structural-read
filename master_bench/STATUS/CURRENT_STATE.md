# CURRENT_STATE.md

Current Branch

structural-read / master_bench

Active Packet

PACKET_005_CURRENT_MOTION_ATTRACTOR_V0

Last Completed

PACKET_004_OPENHERMES_ORIENTATION_DRAFT_V0

Recent Probes

PACKET_003A_LOCAL_AGENT_ADHERENCE_V0
PACKET_004_OPENHERMES_ORIENTATION_DRAFT_V0

Current Motion

The bench is shifting from storing current state toward preserving recoverable motion: the paused trajectory of work that lets future re-entry resume without reconstructing the whole field from memory.

Current Attractor

Reduce the amount of project position the human must carry internally while preserving human review authority and preventing the system from becoming an authority source.

Local Model Read

- OpenHermes: default local bench-orientation model
- Qwen2.5-Coder 3B: later narrow code probe candidate
- Gemma3 4B: schema-obedient but under-grounded
- DeepSeek Coder 6.7B: not suitable for bench orientation

Frozen Floors

- CURRENT_FLOORS.md
- BENCH_CONSTITUTION.md
- STATUS.md

Open Unresolveds

- BenchCheck script
- Orientation retrieval validation
- Whether CURRENT_STATE.md should be human-authored or model-drafted
- Whether OpenHermes can ground orientation from bench context reliably
- Later narrow code probe with Qwen2.5-Coder 3B
- What continuity burden can be externalized safely without externalizing judgment
- Whether Current Motion and Current Attractor improve re-entry

Current Question

Can the bench preserve enough recoverable motion that the human can set the work down and return without carrying the whole map internally?

Boundary

CURRENT_STATE.md is an orientation map, not a roadmap.
Current Motion is trajectory support, not instruction.
Current Attractor is tension exposure, not priority assignment.
