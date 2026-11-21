# pipe_methane_purge_vent

Vents a pipe through an **Active Vent** while it has methane and less than 33 % oxygen.

*Previously called `volatiles_purge_active_vent`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Pipe Analyzer |
| `d1` | Active Vent (on the same pipe) |

## What it does

- Vent ON + Open while methane is present **and** `RatioOxygen` < 33 %.
- Otherwise, or on analyzer `Error`: vent OFF.
- Vent kept in Mode 0 (Outward).
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `pipe_methane_purge_vent.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `O2_TARGET` | `0.33` | Stop once oxygen reaches this ratio |
| `EPS` | `0.000001` | Ratio counted as "no methane" |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | vent off |
| `1` | purging |
| `9` | fault or device missing |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `pipe_methane_purge_vent.ic10` into the chip and run it.

## Notes

- Device notes: `docs/usage/active_vent.md`, `docs/usage/pipe_analyzer.md`

## Change history

- 2026-11-21: remade and renamed. Vent closes on analyzer error; Mode is re-checked every loop, not only at start-up.

## Status

Functional (author's label from before the remake; re-test in-game).
