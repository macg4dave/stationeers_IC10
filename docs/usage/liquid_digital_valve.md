# Liquid Digital Valve setup checklist

## What scripts usually write

- `On` (0/1) as “closed/open”
- Sometimes `Lock` (0/1)

## Minimum to see it change state

- Powered
- In the correct liquid pipe network path (placed where opening/closing matters)
- Connected to the same data network as the IC Housing

## Common gotchas

- If the valve is locked in-game, scripts that only write `On` will appear to do nothing:
  - Ensure `Lock = 0` (or update the script to unlock before writing).
- Many valves expose a `Setting` field but it often does not affect flow:
  - Prefer `On` for “open/close” automation.

