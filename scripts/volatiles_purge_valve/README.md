# volatiles_purge_valve

**Purpose:** If Methane is present in a pipe, run a **Pipe Digital Valve** until **Oxygen ratio is >= 33% of Methane ratio**.

This is useful as a simple methane-purge controller when your valve gates a path used to remove or route methane-heavy gas.

## Devices

Required:

- **Pipe Analyzer** (on the target pipe network)
- **Pipe Digital Valve** (on the same gas network path you want to gate)

## Device registers

- `d0` = Pipe Analyzer
- `d1` = Pipe Digital Valve

## Behavior

Each loop the script reads:

- `RatioMethane` from the Pipe Analyzer
- `RatioOxygen` from the Pipe Analyzer

Rules:

- If `RatioMethane` is not present (<= `EPS`), valve is **OFF**.
- If `RatioMethane` is present and `RatioOxygen < (0.33 * RatioMethane)`, valve is **ON**.
- Otherwise (i.e., `RatioOxygen >= 0.33 * RatioMethane`), valve is **OFF**.

### Tuning

- `EPS` (default `0.000001`): treat ratios <= EPS as zero to avoid float noise.
- `O2_PER_VOL` (default `0.33`): oxygen-to-methane multiplier used for valve cutoff.

## Setup

1. Put the Pipe Analyzer on the pipe network you want to monitor.
2. Put a Pipe Digital Valve on the path you want to control.
3. In the IC Housing, set:
   - `d0` to the Pipe Analyzer
   - `d1` to the Pipe Digital Valve
4. Paste `volatiles_purge_valve.ic10` into the chip and run it.

## Status

Functional.
