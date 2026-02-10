# Solar Tracking

## Purpose

Automatically tracks the sun for solar panels using a daylight sensor. At night, panels reset to a morning start position. Supports optional per-panel horizontal offsets based on panel name labels.

## Devices

- Required:
  - Daylight Sensor
  - Solar panels (any mix of standard/dual/reinforced)
- Optional:
  - None

## Device registers

- `d0`: Daylight Sensor (face up)
- `db`: IC housing (for error/status signaling)

## Labels / hashes

If you want per-panel horizontals (free-form placement), name panels by the direction their **POWER** port faces (degrees):

- `Solar Panel 0` (North)
- `Solar Panel 90` (East)
- `Solar Panel 180` (South)
- `Solar Panel 270` (West)

If you label **all** panels this way, you can ignore `PanelPortDirection` in the script (the daylight sensor direction still matters).

## Usage

1. Place and wire the Daylight Sensor to `d0` and ensure it faces up.
2. (Optional) Rename panels using the label names above.
3. Set `SensorPortDirection` to the daylight sensor port orientation.
4. Set `PanelPortDirection` to the panels' POWER port orientation (only needed if you are **not** labeling all panels).
5. Insert the script and run.

## Tuning

- `SensorPortDirection`: 0=North, 1=East, 2=South, 3=West
- `PanelPortDirection`: 0=North, 1=East, 2=South, 3=West

## Status

Functional

## Credit

Based on Tallinu's solar tracking script, with repo-standard formatting.
