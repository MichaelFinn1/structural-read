# ADAPTER_021E_ELECTRICITY_HOURLY_COARSE_RELATION_V0

Status:
banked

## Purpose

Create a middle adapter between raw numeric under-exposure and fine relational quantile over-exposure.

## Exposed fields

- coarse load side: lower / upper
- coarse adjacent change: small / up_large / down_large

## Boundary

No demand interpretation.
No seasonality label.
No cycle label.
No anomaly label.
No ontology growth.

This adapter tests whether temporal relation can be exposed without full-span saturation.
