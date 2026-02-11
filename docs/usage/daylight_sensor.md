# Daylight Sensor setup checklist

## What scripts usually read

- `Horizontal` / `Vertical` angles (sun direction)

## Minimum to work

- Powered
- Connected to the same data network as the IC Housing
- Correct orientation for your build (many tracking scripts assume the sensor "faces up")

## Common gotchas

- If the sensor is rotated relative to "north", the script usually needs a port-direction offset.
- Night detection is typically "sun below horizon":
  - Scripts may use a threshold like abs(`Vertical`) > ~90 to decide "night".

## Common patterns that scripts use

- Some tracking scripts verify they are actually wired to a Daylight Sensor:
  - They read `PrefabHash` and stop / set a status code if the device is wrong.
