# Structural Read - Getting Started

## What is this?

Structural Read is an investigatory workbench for exploring large log terrains while preserving orientation.

It is not:

- anomaly detection
- root-cause analysis
- AI interpretation
- automatic diagnosis

Instead it helps you:

- survey large terrains
- compare regions
- move between scales
- preserve investigation paths
- return to unfinished work

The goal is to preserve investigability while understanding is still forming.

## Prerequisites

Required:

- Windows
- PowerShell
- Python 3.x
- Git

Recommended:

- Visual Studio Code
- Modern web browser

## Clone the Repository

Run:

git clone https://github.com/MichaelFinn1/structural-read.git

cd structural-read

## Start With an Included Terrain

For a first session, use one of the included long-horizon terrains:

- OpenStack
- Linux
- Netsparker

These already contain generated traversal surfaces and visualizations.

## Open a Visualization

Current stable preview:

OpenStack Global Focus Lens V54

Navigate to:

src/LOG_STRUCTURE_SURFACE_V0/long_duration_packets/openstack_long_horizon_001/visualizations/

Open:

openstack_global_focus_lens_v54g3c_final_alignment.html

or whichever version is currently marked stable in the repository.

## Suggested First Session

Do not try to understand everything.

Instead:

1. Survey the terrain.
2. Pick a region.
3. Inspect locally.
4. Open raw lines.
5. Save a card.
6. Move elsewhere.
7. Return using the card.

This simple loop demonstrates the core workbench behavior.

## What To Pay Attention To

Useful observations:

- regions that change under different constitutions
- continuity that weakens
- continuity that survives
- transitions between neighboring regions
- unresolved areas worth revisiting

Less useful:

- trying to identify a hidden truth immediately
- forcing one explanation
- assuming a single correct scale

## Current Status

This repository is an active research and development workbench.

Some components are stable.

Others are exploratory.

The most useful feedback currently is:

- Was orientation preserved?
- Could you return to unfinished work?
- What was confusing?
- What was helpful?
- What information was missing?
- What felt unnecessary?

## Providing Feedback

Please read FEEDBACK_REQUEST.md and include:

- what terrain you explored
- what task you attempted
- where you became lost
- where the workbench helped
- what you expected to happen
- what actually happened

The goal is not to measure correctness.

The goal is to improve investigability.
