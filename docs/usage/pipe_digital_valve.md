# Pipe Digital Valve setup checklist

## What scripts usually write

- `On` (0/1) as "closed/open"
- Sometimes `Lock` (0/1)

## Minimum to see it change state

- Powered
- In the correct pipe network path (placed where opening/closing matters)
- Connected to the same data network as the IC Housing

## Common gotchas

- If the valve is locked in-game, scripts that only write `On` will appear to do nothing:
  - Ensure `Lock = 0` (or update the script to unlock before writing).
- Many valves expose a `Setting` field but it often does not affect flow:
  - Prefer `On` for "open/close" automation.

## Common patterns that scripts use

- Many controllers read current `On` and only write when it changes (reduces data-network spam).
- For hysteresis control, scripts often:
  - force open below a low threshold
  - force close above a high threshold
  - leave the valve unchanged in between
