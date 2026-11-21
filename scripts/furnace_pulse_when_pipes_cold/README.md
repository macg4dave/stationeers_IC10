# furnace_pulse_when_pipes_cold

Every 30 seconds, checks a gas pipe and a liquid pipe. If either is cold, it opens a valve and gives an **Advanced Furnace** a short `Activate` pulse.

*Previously called `dual_analyzer_furnace_pulse`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Liquid Pipe Analyzer |
| `d1` | Pipe Analyzer (gas) |
| `d2` | Pipe Digital Valve |
| `d3` | Advanced Furnace |

## What it does

- Cold = gas below 30 °C **or** liquid below 80 °C.
- Cold: valve ON, furnace `Activate` 1 for 2 ticks (~1 s), then both OFF.
- Warm: valve OFF, `Activate` 0.
- Then waits `CYCLE_S` seconds.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `furnace_pulse_when_pipes_cold.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `CHECK` | `0` | 0 = both analyzers, 1 = gas only (d0 not needed), 2 = liquid only (d1 not needed) |
| `GAS_COLD_C` | `30` | Gas counts as cold below (°C) |
| `LIQUID_COLD_C` | `80` | Liquid counts as cold below (°C) |
| `PULSE_TICKS` | `2` | Length of the Activate pulse (ticks, 2 per second) |
| `CYCLE_S` | `30` | Seconds between checks |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | warm, idle |
| `1` | cold, pulsed |
| `9` | device missing |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `furnace_pulse_when_pipes_cold.ic10` into the chip and run it.

## Notes

- Device notes: `docs/usage/advanced_furnace.md`, `docs/usage/liquid_pipe_analyzer.md`, `docs/usage/pipe_analyzer.md`

## Change history

- 2026-11-21: remade and renamed. `CHECK` 1 or 2 no longer needs the unused analyzer plugged in; uses `sleep` instead of tick loops; status on the housing.

## Status

Functional (author's label from before the remake; re-test in-game).
