# ADAPTER_021D_ELECTRICITY_HOURLY_RELATION_V0

Status:
banked

## Source

electricity_hourly_zenodo_001 aggregate hourly series

## Member

electricity_hourly_relation_001

## Adapter purpose

Expose aggregate temporal variation in line-native relational form.

## Exposed fields

- load band by within-series quantile
- adjacent delta band by within-series delta magnitude and sign

## What is intentionally not exposed

No demand interpretation.
No economic interpretation.
No anomaly label.
No seasonality label.
No cycle label.
No client-level interpretation.

## Boundary

The adapter exposes relative load and adjacent change only.

It does not explain the source.

It does not promote contact into meaning.
