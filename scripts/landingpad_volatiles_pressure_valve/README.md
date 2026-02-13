# landingpad_volatiles_pressure_valve

Status: Functional

Turns **ON** both a `Landingpad Liquid Output` and a `Pipe Digital Valve` only when:

1. `Landingpad Liquid Output` reports **100% Liquid Volatiles** (`RatioLiquidVolatiles`), and
2. Pipe pressure is at or below the safety limit.

Safety rule:

- If `Pipe Analyzer` pressure is **over 20 MPa** (20000 kPa), the script forces **both devices OFF**.

## Device mapping (`d0..d2`)

- `d0` = `Pipe Analyzer`
- `d1` = `Landingpad Liquid Output`
- `d2` = `Pipe Digital Valve`

## Tuning

In `landingpad_volatiles_pressure_valve.ic10`:

- `VOLATILES_FULL_MIN` (default `0.999999`)
  - Treats values this high (or higher) as “100% volatiles”.
- `PRESSURE_CUTOFF_KPA` (default `20000`)
  - 20 MPa cutoff in kPa.

## Behavior summary

- `desired_on = 1` only when landingpad reading is valid and `RatioLiquidVolatiles >= VOLATILES_FULL_MIN`.
- If `Pipe Analyzer` reports error, script fails safe to OFF.
- If `Pressure > PRESSURE_CUTOFF_KPA`, script forces OFF.
- Writes to `On` only when state changes (reduces network spam).

## Setup notes

- Ensure all three devices are on the same data network.
- Keep the landingpad output powered and unlocked as needed by your base setup.
