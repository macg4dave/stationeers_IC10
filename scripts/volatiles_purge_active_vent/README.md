# volatiles_purge_active_vent

**Purpose:** If Volatiles are present in a pipe, run an **Active Vent** until **Oxygen ratio reaches at least 33%**.

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
- If `RatioVolatiles` is present and `RatioOxygen < O2_TARGET`, vent is **ON**.
- Otherwise (i.e., `RatioOxygen >= O2_TARGET`), vent is **OFF**.

The script also forces the vent `Mode` to **Outward** (`0`) once at startup and keeps
`Open` matched to the desired `On` state.

### Tuning

- `EPS` (default `0.000001`): treat ratios <= EPS as zero to avoid float noise.
- `O2_TARGET` (default `0.33`): oxygen ratio threshold used to stop the purge.

## Setup

1. Put the Pipe Analyzer on the pipe network you want to monitor.
2. Put the Active Vent on the *same* pipe network and connect it to power.
3. Set the vent's `Setting` in-game to a useful manual target for your purge setup.
4. In the IC Housing, set:
   - `d0` to the Pipe Analyzer
   - `d1` to the Active Vent
5. Paste `volatiles_purge_active_vent.ic10` into the chip and run it.

## Status

Functional.
