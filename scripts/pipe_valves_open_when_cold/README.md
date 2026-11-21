# pipe_valves_open_when_cold

Opens every **Pipe Digital Valve named `cold`** when a pipe is cold, and closes them when it warms up.

*Previously called `pipe_temp_valve`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Pipe Analyzer |

**Network devices:** Pipe Digital Valves named exactly `cold` (case-sensitive) on the same data network. The IC Housing must be on the same data network as the named devices.

## What it does

- Below 10 °C: valves OPEN.
- Above 30 °C: valves CLOSED.
- 10–30 °C: holds (starts closed).
- Re-sends the state every ~10 s so newly built valves join in.
- Analyzer `Error`: valves hold, status 9.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `pipe_valves_open_when_cold.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `OPEN_BELOW_C` | `10` | Open below (°C) |
| `CLOSE_ABOVE_C` | `30` | Close above (°C) |
| `RESEND_TICKS` | `20` | Ticks between re-sends |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | closed |
| `1` | open |
| `9` | analyzer missing or fault |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `pipe_valves_open_when_cold.ic10` into the chip and run it.
4. Rename the network devices exactly as listed above (Labeller).

## Notes

- Device notes: `docs/usage/pipe_analyzer.md`, `docs/usage/pipe_digital_valve.md`

## Change history

- 2026-11-21: remade and renamed. Valves are unlocked before writing; state is re-sent every ~10 s; status on the housing.

## Status

Functional (author's label from before the remake; re-test in-game).
