# phase_change_device setup checklist

This repo uses the name `phase_change_device` as a placeholder for “a device on the data network that exposes `Temperature` (Kelvin)”.

## What scripts usually read

- `Temperature` (Kelvin)

## Minimum to work

- Powered (if required by that device)
- Connected to the same data network as the IC Housing

## Common gotchas

- Temperature is **Kelvin**:
  - Convert with `C = K - 273.15`

## Common patterns that scripts use

- Controllers often use a single threshold like:
  - "Open when `tempC > X`" (and close otherwise).
