# pipe_valve_open_when_clean

Opens a **Pipe Digital Valve** only when the gas has no methane and no steam, e.g. to let clean air through.

*Previously called `no_volatiles_no_steam_valve`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Pipe Analyzer |
| `d1` | Pipe Digital Valve |

## What it does

- Valve ON while methane ≈ 0, steam ≈ 0 and pressure > 1 kPa.
- Anything else, or analyzer `Error`: valve OFF.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `pipe_valve_open_when_clean.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `EPS` | `0.000001` | Ratio counted as "none" |
| `MIN_KPA` | `1` | Minimum pressure to open (kPa) |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | closed |
| `1` | open |
| `9` | fault or device missing |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `pipe_valve_open_when_clean.ic10` into the chip and run it.

## Notes

- Device notes: `docs/usage/pipe_analyzer.md`, `docs/usage/pipe_digital_valve.md`

## Change history

- 2026-11-21: remade and renamed. Valve closes on analyzer error; status on the housing.

## Status

Functional (author's label from before the remake; re-test in-game).
