# phase_change_cooling_valve

Opens every **Pipe Digital Valve named `cold`** when a phase-change device gets hot, to send coolant through.

*Previously called `phase_change_temp_valve`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | phase_change_device |

**Network devices:** Pipe Digital Valves named exactly `cold` on the same data network. The IC Housing must be on the same data network as the named devices.

## What it does

- Above 30 °C: valves OPEN.
- Below 28 °C: valves CLOSED.
- 28–30 °C: holds (starts closed).
- Unlocks the valves; re-sends the state every ~10 s.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `phase_change_cooling_valve.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `OPEN_ABOVE_C` | `30` | Open above (°C) |
| `CLOSE_BELOW_C` | `28` | Close below (°C) |
| `RESEND_TICKS` | `20` | Ticks between re-sends |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | closed |
| `1` | open |
| `9` | device missing or no reading |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `phase_change_cooling_valve.ic10` into the chip and run it.
4. Rename the network devices exactly as listed above (Labeller).

## Notes

- Device notes: `docs/usage/phase_change_device.md`, `docs/usage/pipe_digital_valve.md`

## Change history

- 2026-11-21: remade and renamed. Added the 28–30 °C band and the periodic re-send; status on the housing.

## Status

Functional (author's label from before the remake; re-test in-game).
