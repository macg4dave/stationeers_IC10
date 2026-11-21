# liquid_valves_open_when_cold

Opens **every Liquid Digital Valve** on the network when the liquid is cold, and closes them all when it warms up.

*Previously called `liquid_temp_valve`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Liquid Pipe Analyzer |

**Network devices:** All Liquid Digital Valves on the same data network (no names needed, so **every** one is driven). The IC Housing must be on the same data network as the named devices.

## What it does

- Below 20 °C: valves OPEN.
- Above 30 °C: valves CLOSED.
- 20–30 °C: holds (starts closed).
- Re-sends the state every ~10 s.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `liquid_valves_open_when_cold.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `OPEN_BELOW_C` | `20` | Open below (°C) |
| `CLOSE_ABOVE_C` | `30` | Close above (°C) |
| `RESEND_TICKS` | `20` | Ticks between re-sends |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | closed |
| `1` | open |
| `9` | analyzer missing or no reading |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `liquid_valves_open_when_cold.ic10` into the chip and run it.
4. Rename the network devices exactly as listed above (Labeller).

## Notes

- The valve prefab hash `-517628750` comes from the original working script; it is not the CRC of `StructureLiquidDigitalValve`. If no valve reacts, that hash is the first thing to check.
- Device notes: `docs/usage/liquid_pipe_analyzer.md`, `docs/usage/liquid_digital_valve.md`

## Change history

- 2026-11-21: remade and renamed. Fixed a start-up gap: valves left open from before were not closed until the liquid first went below 20 °C and back above 30 °C. State is now re-sent every ~10 s.

## Status

Functional (author's label from before the remake; re-test in-game).
