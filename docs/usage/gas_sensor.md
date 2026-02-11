# Gas Sensor setup checklist

## What scripts usually read

- `Pressure` (kPa)
- `Temperature` (Kelvin)
- Gas ratios like `RatioSteam`, `RatioOxygen`, `RatioVolatiles` (0..1)

## Minimum to get valid readings

- Powered (and not in an error state)
- Connected to the same data network as the IC Housing

## Common gotchas

- Temperature is **Kelvin**:
  - Convert with `C = K - 273.15`
- Ratios are floats with noise:
  - Avoid "exactly zero" checks; use a small epsilon like `0.0001`
- Placement matters:
  - It reports the atmosphere where it is placed (room vs pipe is a different device)

## Common patterns that scripts use

- Steam/condensation control often looks like:
  - "If `RatioSteam` is below a small epsilon, allow venting."
