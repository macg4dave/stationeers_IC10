# pipe_valve_open_when_methane

Opens a **Pipe Digital Valve** only while the pipe contains methane, e.g. to pass fuel on and stop when the line is empty.

*Previously called `no_volatiles_valve`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Pipe Analyzer |
| `d1` | Pipe Digital Valve |

## What it does

- Valve ON while `RatioMethane` > 0 (above float noise).
- Valve OFF when there is none, or on analyzer `Error`.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `pipe_valve_open_when_methane.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `EPS` | `0.000001` | Ratio counted as "no methane" |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | closed |
| `1` | open |
| `9` | fault or device missing |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `pipe_valve_open_when_methane.ic10` into the chip and run it.

## Notes

- Device notes: `docs/usage/pipe_analyzer.md`, `docs/usage/pipe_digital_valve.md`

## Change history

- 2026-11-21: remade and renamed. Valve closes on analyzer error; status on the housing.

## Status

Functional (author's label from before the remake; re-test in-game).
