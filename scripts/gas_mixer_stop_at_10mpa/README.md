# gas_mixer_stop_at_10mpa

Stops a **Gas Mixer** when its output pipe reaches 10 MPa and restarts it when the pressure drops.

*Previously called `pipe_pressure_gas_mixer`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Pipe Analyzer (mixer output pipe) |
| `d1` | Gas Mixer |

## What it does

- Above 10 MPa: mixer OFF.
- Below 9.5 MPa: mixer ON.
- In between: holds.
- Analyzer switched off: the script switches it on (mixer OFF meanwhile).
- Analyzer `Error`: mixer OFF.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `gas_mixer_stop_at_10mpa.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `STOP_ABOVE_KPA` | `10000` | Stop above (kPa) |
| `RESUME_BELOW_KPA` | `9500` | Restart below (kPa) |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | mixer off |
| `1` | mixer on |
| `3` | analyzer error |
| `4` | analyzer was off |
| `9` | device missing |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `gas_mixer_stop_at_10mpa.ic10` into the chip and run it.

## Notes

- Device notes: `docs/usage/pipe_analyzer.md`

## Change history

- 2026-11-21: remade and renamed. Added the 9.5–10 MPa band (it used to flip at exactly 10 MPa).

## Status

Functional (author's label from before the remake; re-test in-game).
