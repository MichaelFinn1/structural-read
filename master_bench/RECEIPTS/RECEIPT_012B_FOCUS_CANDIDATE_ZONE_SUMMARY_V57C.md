# RECEIPT_012B_FOCUS_CANDIDATE_ZONE_SUMMARY_V57C

Status: COMPLETED
Packet: PACKET_012_FOCUS_CANDIDATE_ZONES_V57C
Result: PASS

## Movement

Ran V57C across current terrains and created cross-terrain candidate-zone summary.

## File created

- src/LOG_STRUCTURE_SURFACE_V0/focus_candidate_zone_summary_v0.csv

## Observer read

OpenStack:
- strongest separation
- 53 candidate zones
- mostly distributed_corridor candidates
- several mixed_deformation candidates
- max zone length 9 bins

Linux:
- 6 candidate zones
- localized and mixed only
- max zone length 3 bins

Netsparker:
- 3 candidate zones
- localized and mixed
- max zone length 6 bins

Zero-zone terrains:
- interrupted_replay
- periodic_signal
- apache_acunetix

Single-zone terrains:
- hierarchical_burst
- white_noise
- mixed_pulse_noise
- apache_baseline
- apache_netsparker

## Evidence value

The full V57 observer sequence now differentiates terrains across:

- deformation profile
- localization profile
- candidate-zone profile

This was achieved without UI changes, best-focus claims, anomaly language, basin claims, or recommendations.

## Boundary

Candidate zones are not basins.

Candidate-zone count is not importance.

Distributed corridor is not explanation.

Localized deformation is not anomaly.

Zero zones are not absence of structure.

## Open unresolveds

- Whether candidate zones should be lightly exposed in the UI.
- Whether V57 outputs should be packaged into a read file.
- Whether corridor refinement should be run inside selected OpenStack candidate zones.
- Whether bin-size provenance should be made more visible in summaries.
- Whether focus-size missingness should be addressed upstream.

## Stop condition

V57C cross-terrain summary banked.
Stop before UI or interpretation.
