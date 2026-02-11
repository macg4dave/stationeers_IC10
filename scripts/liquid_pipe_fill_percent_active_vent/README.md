# liquid_pipe_fill_percent_active_vent

## Purpose

Turn on an **Active Vent** when a **Liquid Pipe Analyzer** reports the pipe is below a configurable liquid fill percentage.

## Devices

- **Required**
  - Liquid Pipe Analyzer
  - Active Vent

## Device registers

- `d0` = Liquid Pipe Analyzer
- `d1` = Active Vent

## Usage

1. Place and connect the Liquid Pipe Analyzer to the liquid pipe network you want to monitor.
2. Place the Active Vent and connect it to power and the gas network it should control.
3. Assign devices:
   - `d0` → Liquid Pipe Analyzer
   - `d1` → Active Vent
4. Set `LIQUID_THRESHOLD_PERCENT` in the script (default 50).
5. Set `VENT_MODE` in the script (0 = Outward/exhaust, 1 = Inward/intake; confirm in UI).
6. (Optional) Set `VENT_LOCK` to `1` if you want the vent locked after updates.
7. Paste `liquid_pipe_fill_percent_active_vent.ic10` into an IC chip and run it.

## Tuning

- `LIQUID_THRESHOLD_PERCENT` — Liquid fill percentage ($0$–$100$) below which the vent turns on.
- `VENT_MODE` — `0` for Outward (exhaust) or `1` for Inward (intake).
- `VENT_LOCK` — `0` to leave the vent unlocked, `1` to lock after updates.

## Status

Functional
