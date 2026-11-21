# pipe_vents_fill_to_10mpa

Uses **Active Vents named `PIPE_VENT`** to pump room gas into a pipe until it reaches 10 MPa.

*Previously called `pipe_pressure_active_vent`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Pipe Analyzer (the pipe being filled) |

**Network devices:** Active Vents named exactly `PIPE_VENT`. The IC Housing must be on the same data network as the named devices.

## What it does

- Below 9.9 MPa: vents Inward (room → pipe) with a 10 MPa limit.
- At 10 MPa: vents OFF until it drops below 9.9 MPa.
- Analyzer `Error`: vents OFF.
- Re-applies the filling state every ~6 s.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `pipe_vents_fill_to_10mpa.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `TARGET_KPA` | `10000` | Stop at (kPa) |
| `START_BELOW_KPA` | `9900` | Start again below (kPa) |
| `MODE_FILL` | `1` | Vent Mode used to fill (1 = Inward) |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | idle |
| `1` | filling |
| `9` | analyzer missing |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `pipe_vents_fill_to_10mpa.ic10` into the chip and run it.
4. Rename the network devices exactly as listed above (Labeller).

## Notes

- Device notes: `docs/usage/active_vent.md`, `docs/usage/pipe_analyzer.md`

## Change history

- 2026-11-21: remade and renamed. Vents stop on analyzer error; target and restart pressure are now direct kPa settings; status on the housing.

## Status

Functional (author's label from before the remake; re-test in-game).
