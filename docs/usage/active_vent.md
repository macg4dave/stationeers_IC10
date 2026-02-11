# Active Vent setup checklist

When a script “sets the vent” but nothing happens, it’s usually because one of these properties wasn’t set.

## Minimum to see movement

- `On = 1`
- `Open = 1`
- `Mode` set correctly for your intent
  - Some scripts use constants like `MODE_INWARD`/`MODE_OUTWARD`. Verify which numeric value maps to which direction in your build.

## Common accompanying properties (script-dependent)

- `Lock = 1` after configuration (optional, but many scripts do it to prevent manual/in-game overrides)
- Pressure / setpoint properties used by that script, e.g.:
  - `Setting`
  - `PressureExternal`
  - `PressureInternal`

## Batch/name-hash gotcha

If using `lbn`/`sbn`, **NameHash is exact**:

- Rename ALL vents in the group to the same exact name (duplicates are fine), e.g. `IN` and `OUT`.
