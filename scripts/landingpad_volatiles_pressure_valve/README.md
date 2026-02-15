# landingpad_volatiles_pressure_valve

Status: Functional

Turns **ON** both a `Landingpad Gas Output` and a `Pipe Digital Valve` only when:

1. `Landingpad Gas Output` reports **100% Volatiles** (`RatioVolatiles`), and
2. Pipe pressure is at or below the safety limit.

Manual override:

- If an override source on `d3` reports `Setting >= OVERRIDE_LEVEL_ON`, the script requests both outputs **ON**.
- Safety cutoff still applies.

Safety rule:

- If `Pipe Analyzer` pressure is **over 20 MPa** (20000 kPa), the script forces **both devices OFF**.

## Device mapping (`d0..d2`)

- `d0` = `Pipe Analyzer`
- `d1` = `Landingpad Gas Output`
- `d2` = `Pipe Digital Valve`

Optional:

- `d3` = Override source exposing `Setting` (for example, `Logic Memory` or a dial)

## Tuning

In `landingpad_volatiles_pressure_valve.ic10`:

- `VOLATILES_FULL_MIN` (default `0.999`)
  - Treats values this high (or higher) as “100% volatiles”.
- `PRESSURE_CUTOFF_KPA` (default `20000`)
  - 20 MPa cutoff in kPa.
- `OVERRIDE_LEVEL_ON` (default `1`)
  - Manual override is active when `d3 Setting >= OVERRIDE_LEVEL_ON`.

## Behavior summary

- `desired_on = 1` when `RatioVolatiles >= VOLATILES_FULL_MIN`.
- `desired_on = 1` when manual override is active.
- If `Pressure > PRESSURE_CUTOFF_KPA`, script forces OFF.
- Script self-heals valve lock by setting `Lock = 0` on the Pipe Digital Valve.
- Writes to `On` only when state changes (reduces network spam).

Debug status (`db Setting`):

- `10` volatiles condition met (request ON)
- `20` volatiles condition not met (request OFF)
- `30` pressure cutoff active (forced OFF)
- `40` manual override active (request ON)

## Setup notes

- Ensure all three devices are on the same data network.
- Keep the landingpad output powered and unlocked as needed by your base setup.
