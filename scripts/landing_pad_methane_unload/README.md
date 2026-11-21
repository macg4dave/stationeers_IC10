# landing_pad_methane_unload

Unloads pure methane from a **Landingpad Gas Output** into a pipe, with a pressure cutoff and an optional manual override.

*Previously called `landingpad_volatiles_pressure_valve`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Pipe Analyzer (destination pipe) |
| `d1` | Landingpad Gas Output |
| `d2` | Pipe Digital Valve |
| `d3` | (optional) override: any device with `Setting`, e.g. a Dial |

## What it does

- Pad output + valve ON while the pad gas is ≥ 99.9 % methane, or while d3 `Setting` ≥ 1.
- Pressure cutoff: everything OFF above 20 MPa; re-arms only below 19 MPa.
- Unlocks the valve if it is locked.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `landing_pad_methane_unload.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `METHANE_MIN` | `0.999` | Methane ratio counted as pure |
| `CUTOFF_KPA` | `20000` | Cut off above (kPa) |
| `REARM_KPA` | `19000` | Re-arm below (kPa) |
| `OVERRIDE_ON` | `1` | d3 Setting that forces ON |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `10` | unloading |
| `20` | pad gas not pure methane |
| `30` | pressure cutoff |
| `40` | override on |
| `9` | device missing |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `landing_pad_methane_unload.ic10` into the chip and run it.

## Notes

- Device notes: `docs/usage/landingpad_output.md`, `docs/usage/pipe_analyzer.md`

## Change history

- 2026-11-21: remade and renamed. Cutoff now has a 1 MPa re-arm band (it used to re-open as soon as pressure dipped under 20 MPa); status written once per loop instead of up to three times.

## Status

Functional (author's label from before the remake; re-test in-game).
