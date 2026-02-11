# Logic Switch (Important Button) setup checklist

## What scripts usually read

- `Activate` (momentary 0->1 pulse when pressed)

## Minimum to work

- Connected to the same data network as the IC Housing
- Assigned to the correct `d0..d5` pin

## Common gotchas

- This is **momentary**:
  - If you want toggle behavior, the script must store state and flip it when `Activate` pulses.
- `Open` is the lid state (not the press).

