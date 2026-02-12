# Daylight Sensor setup checklist

## What scripts usually read

- `Horizontal` / `Vertical` angles (sun direction)

This sensor does **not** provide a direct `TimeOfDay` clock number; scripts derive time from angles.

## Minimum to work

- Powered
- Connected to the same data network as the IC Housing
- Correct orientation for your build (many tracking scripts assume the sensor "faces up")

## Common gotchas

- If the sensor is rotated relative to "north", the script usually needs a port-direction offset.
- Night detection is typically "sun below horizon":
  - Scripts may use a threshold like abs(`Vertical`) > ~90 to decide "night".

For clock scripts derived from `Horizontal`:

- If noon appears as `00:00`, the phase offset is wrong.
- If time runs backward, invert the horizontal mapping.
- If hour is close but shifted, use a minute-level shift.

Recommended calibration order:

1. `SENSOR_PORT_DIRECTION` (sensor orientation: 0/1/2/3)
2. Invert flag (if available, e.g. `CLOCK_DEG_INVERT=1`)
3. Degree offset (e.g. `CLOCK_DEG_OFFSET`)
4. Fine trim in minutes (e.g. `TIME_SHIFT_MIN`)

## Common patterns that scripts use

- Some tracking scripts verify they are actually wired to a Daylight Sensor:
  - They read `PrefabHash` and stop / set a status code if the device is wrong.

- Clock scripts often quantize values to integers before formatting text output.
