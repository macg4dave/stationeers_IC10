# Pipe Heater setup checklist

## What scripts usually write

- `On` (0/1)

## What scripts usually read

- `Power` (0/1)
- `Error` (0/1)
- `Lock` (0/1)
- `On` (0/1)
- `RequiredPower` (W)

## Minimum to work

- Powered
- Plumbed into the pipe network you want to heat
- Connected to the same data network as the IC Housing

## Common gotchas

- Many simple controllers only toggle `On`:
  - They do not set `Lock` automatically.
- If it appears to do nothing:
  - check the heater has electrical power
  - check it is on the intended pipe network
  - check the Pipe Analyzer is reading the same network you expect to heat
