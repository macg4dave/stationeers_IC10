# volatiles_purge_active_vent

**Purpose:** If Volatiles are present in a pipe, run an **Active Vent** until **Oxygen ratio is greater than or equal to Volatiles ratio**.

This is useful as a simple “purge volatiles” controller when you expect the pipe mixture to become oxygen-dominant again.

## Devices

Required:

- **Pipe Analyzer** (on the target pipe network)
- **Active Vent** (connected to the same pipe network)

## Device registers

- `d0` = Pipe Analyzer
- `d1` = Active Vent

## Behavior

Each loop the script reads:

- `RatioVolatiles` from the Pipe Analyzer
- `RatioOxygen` from the Pipe Analyzer

Rules:

- If `RatioVolatiles` is not present (<= `EPS`), vent is **OFF**.
- If `RatioVolatiles` is present and `RatioOxygen < RatioVolatiles`, vent is **ON**.
- Otherwise (i.e., `RatioOxygen >= RatioVolatiles`), vent is **OFF**.

The script also forces the vent `Mode` to **Outward** (`1`) once at startup.

### Tuning

- `EPS` (default `0.000001`): treat ratios <= EPS as zero to avoid float noise.

## Setup

1. Put the Pipe Analyzer on the pipe network you want to monitor.
2. Put the Active Vent on the *same* pipe network and connect it to power.
3. In the IC Housing, set:
   - `d0` to the Pipe Analyzer
   - `d1` to the Active Vent
4. Paste `volatiles_purge_active_vent.ic10` into the chip and run it.

## Status

Functional.
