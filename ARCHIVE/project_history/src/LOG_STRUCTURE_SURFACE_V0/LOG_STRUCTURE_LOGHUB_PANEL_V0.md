# LOG_STRUCTURE_LOGHUB_PANEL_V0.md

Status: next_external_terrain_panel

## Purpose

Use public operational log datasets to test LOG_STRUCTURE_SURFACE_V0 on recognizable external terrains.

## Recommended first panel

1. Apache
   - small readable server-log terrain
   - useful first external run

2. OpenStack
   - distributed infrastructure terrain
   - likely higher entropy and mixed recurrence

3. Linux or OpenSSH
   - ordinary system-log terrain
   - useful for legibility testing

4. BGL slice
   - supercomputer log terrain
   - useful stress test, but slice first

## Source

Loghub / LogPAI public system log datasets.

## Rule

Start with terrain diversity, not maximum size.

## Boundary

Do not add:
- anomaly scoring
- parser benchmarking
- severity ranking
- incident detection
- root-cause analysis

## Standing read

LOG_STRUCTURE_SURFACE_V0 should be tested as a pre-interpretive structural reduction layer, not as a competitor to anomaly detection systems.

## One-line hold

Use public logs to test portability, not to widen the product claim.
