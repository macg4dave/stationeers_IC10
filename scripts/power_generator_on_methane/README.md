# power_generator_on_methane

Runs a **Gas Fuel Generator** only while its fuel pipe has methane in it.

*Previously called `pipe_volatiles_gas_fuel_generator`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Pipe Analyzer (fuel pipe) |
| `d1` | Gas Fuel Generator |

## What it does

- Generator ON while `RatioMethane` > 0.
- OFF when there is none, or on analyzer `Error`.
- Analyzer switched off: the script switches it on.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `power_generator_on_methane.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `EPS` | `0.000001` | Ratio counted as "no methane" |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | generator off |
| `1` | generator on |
| `3` | analyzer error |
| `4` | analyzer was off |
| `9` | device missing |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `power_generator_on_methane.ic10` into the chip and run it.

## Notes

- Device notes: `docs/usage/pipe_analyzer.md`

## Change history

- 2026-11-21: remade and renamed. Shorter; pins checked in the loop. Behaviour unchanged.

## Status

Functional (author's label from before the remake; re-test in-game).
