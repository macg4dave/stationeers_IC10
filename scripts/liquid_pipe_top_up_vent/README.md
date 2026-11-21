# liquid_pipe_top_up_vent

Runs an **Active Vent** while a liquid pipe is less than half full.

*Previously called `liquid_pipe_fill_percent_active_vent`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Liquid Pipe Analyzer |
| `d1` | Active Vent |

## What it does

- Fill % = `VolumeOfLiquid` / `Volume`.
- Below 50 %: vent ON + Open.
- Above 55 %: vent OFF.
- In between: holds.
- Vent kept in `VENT_MODE`; locked after each change if `VENT_LOCK` = 1.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `liquid_pipe_top_up_vent.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `ON_BELOW_PCT` | `50` | Start below (%) |
| `OFF_ABOVE_PCT` | `55` | Stop above (%) |
| `VENT_MODE` | `0` | 0 = Outward, 1 = Inward |
| `VENT_LOCK` | `0` | 1 = lock the vent after changes |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | vent off |
| `1` | vent on |
| `9` | device missing or pipe volume 0 |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `liquid_pipe_top_up_vent.ic10` into the chip and run it.

## Notes

- Device notes: `docs/usage/active_vent.md`, `docs/usage/liquid_pipe_analyzer.md`

## Change history

- 2026-11-21: remade and renamed. Added the 50–55 % band (it used to flip at exactly 50 %); guards against a zero pipe volume; status on the housing.

## Status

Functional (author's label from before the remake; re-test in-game).
