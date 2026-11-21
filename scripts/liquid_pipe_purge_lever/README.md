# liquid_pipe_purge_lever

A **lever** empties a liquid pipe through a valve, a vent and a liquid outlet. An **LED** shows what is going on.

*Previously called `purge_valve`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Lever |
| `d1` | Liquid Pipe Analyzer |
| `d2` | Liquid Digital Valve |
| `d3` | Active Vent |
| `d4` | Active Liquid Outlet |
| `d5` | LED |

## What it does

- Lever ON and pipe pressure > 0.001 kPa: valve, vent and outlet ON.
- Anything else (lever off, pipe empty, analyzer `Error`): all OFF.
- LED: **yellow** = something in the pipe, lever off · **red** = purging · **green** = empty, lever on · **off** = idle.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `liquid_pipe_purge_lever.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `MIN_KPA` | `0.001` | Pressure counted as "something in the pipe" |
| `GREEN/RED/YELLOW` | `2/4/5` | LED colour values |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | idle |
| `1` | purging |
| `2` | has contents, lever off |
| `3` | empty, lever on |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `liquid_pipe_purge_lever.ic10` into the chip and run it.

## Notes

- Device notes: `docs/usage/logic_switch_lever.md`, `docs/usage/liquid_pipe_analyzer.md`, `docs/usage/active_liquid_outlet.md`

## Change history

- 2026-11-21: remade and renamed. Shorter; pins checked in the loop; status on the housing. Behaviour unchanged.

## Status

Functional (author's label from before the remake; re-test in-game).
