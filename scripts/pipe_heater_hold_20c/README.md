# pipe_heater_hold_20c

Keeps a pipe warm: a **Pipe Heater** turns on when a **Pipe Analyzer** reads below 20 °C and off again above 22 °C.

*Previously called `pipe_heater_below_20c`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Pipe Analyzer |
| `d1` | Pipe Heater |

## What it does

- Below 20 °C: heater ON.
- Above 22 °C: heater OFF.
- 20–22 °C: holds.
- Analyzer `Error`, empty pipe or unplugged device: heater OFF, status 9.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `pipe_heater_hold_20c.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `HEAT_ON_BELOW_C` | `20` | Heater on below this (°C) |
| `HEAT_OFF_ABOVE_C` | `22` | Heater off above this (°C) |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | heater off |
| `1` | heater on |
| `9` | fault or device missing |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `pipe_heater_hold_20c.ic10` into the chip and run it.

## Notes

- Device notes: `docs/usage/pipe_analyzer.md`, `docs/usage/pipe_heater.md`

## Change history

- 2026-11-21: remade and renamed. Added the 2 °C band and the empty-pipe check; status on the housing.

## Status

Functional (author's label from before the remake; re-test in-game).
