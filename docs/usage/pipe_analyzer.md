# Pipe Analyzer setup checklist

## What scripts usually read

- `Pressure` (kPa)
- `Temperature` (Kelvin)
- Gas ratios like `RatioVolatiles`, `RatioSteam`, `RatioOxygen` (0..1)
- `Error` (0/1)

## Minimum to get valid readings

- Powered
- Plumbed into the pipe network you want to measure
- Connected to the same data network as the IC Housing

## Common gotchas

- If `Error != 0`, many controllers will treat readings as invalid and force outputs OFF.
- If your Pipe Analyzer has an in-game `On` toggle, ensure it is `On = 1` (scripts often assume it).
- Temperature is **Kelvin**:
  - Convert with `C = K - 273.15`
- Ratios are floats with noise:
  - Use an epsilon (e.g. `0.000001`) instead of exact comparisons.

## Common patterns that scripts use

- "Gate open" logic often combines:
  - ratio checks (with `EPS`) and
  - a minimum `Pressure` (kPa) so the controller doesn't open into vacuum/no pipe content.
