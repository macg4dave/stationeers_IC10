# Liquid Pipe Analyzer setup checklist

## What scripts usually read

- `Pressure` (kPa)
- `Temperature` (Kelvin)
- `Volume` and `VolumeOfLiquid` (if supported in your build)
- `Error` (0/1)

## Minimum to get valid readings

- Powered
- Plumbed into the liquid pipe network you want to measure
- Connected to the same data network as the IC Housing

## Common gotchas

- If `Error != 0`, many controllers will treat readings as invalid and force outputs OFF.
- Temperature is **Kelvin**:
  - Convert with `C = K - 273.15`
- `Volume` / `VolumeOfLiquid` availability varies by device/build:
  - If your script relies on them and they read as `0`, verify the device supports those outputs in your Stationeers version.

