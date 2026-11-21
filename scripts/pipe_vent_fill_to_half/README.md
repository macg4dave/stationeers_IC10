# pipe_vent_fill_to_half

Runs an **Active Vent** to fill a pipe to about half of a target pressure (50 kPa by default).

*Previously called `pipe_half_full_active_vent`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Pipe Analyzer |
| `d1` | Active Vent |

## What it does

- Below 50 % of `TARGET_KPA`: vent ON + Open.
- Above 55 %: vent OFF.
- In between: holds.
- Analyzer `Error`: vent OFF.
- Set the vent's Mode/Setting in its own screen.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `pipe_vent_fill_to_half.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `TARGET_KPA` | `100` | Full pressure (kPa) |
| `ON_BELOW` | `0.50` | Start below this fraction |
| `OFF_ABOVE` | `0.55` | Stop above this fraction |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | vent off |
| `1` | vent on |
| `9` | fault or device missing |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `pipe_vent_fill_to_half.ic10` into the chip and run it.

## Notes

- Device notes: `docs/usage/active_vent.md`, `docs/usage/pipe_analyzer.md`

## Change history

- 2026-11-21: remade and renamed. Shorter; status on the housing. Behaviour unchanged.

## Status

Functional (author's label from before the remake; re-test in-game).
