# Large Satellite Dish setup checklist

## What scripts usually read

- `Power` (0/1)
- `Error` (0/1)
- `Idle` (0/1)
- `SignalID`, `SignalStrength`

## What scripts usually write

- `Horizontal`, `Vertical`
- Sometimes `BestContactFilter`

## Minimum to see it move / detect signals

- Powered and connected to the data network
- Wait for `Idle = 1` before trusting signal outputs

## Common gotchas

- While the dish is moving (`Idle = 0`), many outputs are meaningless (often `-1`).
- `SignalStrength` is often negative; “bigger is better”:
  - Example: `-10` is stronger than `-50`.
- If `Error = 1`, fix the in-game error state first; scripts often stop doing anything when errored.

