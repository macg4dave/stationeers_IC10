# Wall Heater setup checklist

## What scripts usually write

- `On` (0/1)

## Minimum to work

- Powered
- Connected to the same data network as the IC Housing

## Common gotchas

- Many simple controllers only toggle `On`:
  - Any target temperature / mode should be configured in the device UI unless you have a script that explicitly manages those fields.
