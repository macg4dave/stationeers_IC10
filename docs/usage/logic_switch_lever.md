# Logic Switch (Lever) setup checklist

## What scripts usually read

- `Open` (0/1) as the lever state

## Minimum to work

- Connected to the same data network as the IC Housing
- Assigned to the correct `d0..d5` pin

## Common gotchas

- The lever value is a simple boolean; scripts often treat it as an enable/disable gate.
- Some builds/devices expose `Setting` as a mirror of `Open` (read-only).

