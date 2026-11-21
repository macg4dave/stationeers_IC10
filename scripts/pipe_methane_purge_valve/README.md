# pipe_methane_purge_valve

Purges methane through a **Pipe Digital Valve** until there is enough oxygen relative to the methane.

*Previously called `volatiles_purge_valve`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Pipe Analyzer |
| `d1` | Pipe Digital Valve |

## What it does

- Valve ON while methane is present **and** `RatioOxygen` < 33 % of `RatioMethane`.
- Otherwise, or on analyzer `Error`: valve OFF.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `pipe_methane_purge_valve.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `O2_PER_CH4` | `0.33` | Oxygen needed per unit of methane |
| `EPS` | `0.000001` | Ratio counted as "no methane" |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | closed |
| `1` | purging |
| `9` | fault or device missing |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `pipe_methane_purge_valve.ic10` into the chip and run it.

## Notes

- Device notes: `docs/usage/pipe_analyzer.md`

## Change history

- 2026-11-21: remade and renamed. Valve now closes on analyzer error (it used to stay as it was). Dropped the Pipe Analyzer prefab check.

## Status

Functional (author's label from before the remake; re-test in-game).
