# ADAPTER_021C_ELECTRICITY_HOURLY_AGGREGATE_V0

Status:
banked

## Source

Electricity hourly aggregate time series.

## Member

electricity_hourly_zenodo_001

## Adapter purpose

Expose aggregate hourly load as a line-native temporal terrain.

## Exposed form

Each line contains:

- hour index
- aggregate load value

## What is intentionally not exposed

No client-level interpretation.

No demand interpretation.

No economic interpretation.

No anomaly label.

No seasonality label.

No cycle label.

## Boundary

The adapter exposes aggregate temporal variation only.

It does not explain the source.

It does not promote contact into meaning.
