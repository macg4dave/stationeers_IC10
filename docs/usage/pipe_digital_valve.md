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

## Hashing gotchas (batch scripts)

- Name hashes are exact and case-sensitive.
  - `HASH("cold")` matches only `cold`.
  - `cold_1`, `Cold`, and `COLD` are different names.
- Hash filters combine: prefab hash + name hash means both must match.
- For type filtering, prefer the known Pipe Digital Valve prefab hash: `-1280984102`.
- If hash targeting is correct but valve still does not move, write `Lock=0` before writing `On`.

## Common patterns that scripts use

- Many controllers read current `On` and only write when it changes (reduces data-network spam).
- For hysteresis control, scripts often:
  - force open below a low threshold
  - force close above a high threshold
  - leave the valve unchanged in between
