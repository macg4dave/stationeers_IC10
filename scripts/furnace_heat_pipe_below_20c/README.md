# furnace_heat_pipe_below_20c

Uses an **Advanced Furnace** to heat a pipe when it gets cold, and stops feeding the furnace if the furnace itself gets too hot.

*Previously called `pipe_furnace_valve_below_20c`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Pipe Analyzer (the pipe to keep warm) |
| `d1` | Pipe Digital Valve |
| `d2` | Advanced Furnace |

## What it does

- Pipe below 20 °C: valve ON, furnace `On` + `Activate`, `SettingInput` 5, `SettingOutput` 5.
- While heating and the furnace is above 100 °C: `SettingInput` 0 until it cools.
- Pipe above 22 °C: valve OFF, furnace OFF, `Activate` 0.
- 20–22 °C: holds.
- Analyzer `Error` or empty pipe: everything OFF, status 9.
- Unlocks the valve and furnace if they are locked.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `furnace_heat_pipe_below_20c.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `HEAT_BELOW_C` | `20` | Start heating below (°C) |
| `STOP_ABOVE_C` | `22` | Stop heating above (°C) |
| `FURNACE_MAX_C` | `100` | Furnace temperature that pauses its input (°C) |
| `INPUT_COLD` | `5` | SettingInput while heating |
| `INPUT_HOT` | `0` | SettingInput while the furnace is too hot |
| `OUTPUT_SET` | `5` | SettingOutput while heating |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | idle |
| `1` | heating |
| `2` | heating, furnace input paused (furnace hot) |
| `9` | fault or device missing |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `furnace_heat_pipe_below_20c.ic10` into the chip and run it.

## Notes

- Assumes `Activate` stays at 1 while heating (latched). If your furnace expects a short pulse, use `furnace_pulse_when_pipes_cold` instead.
- Device notes: `docs/usage/advanced_furnace.md`, `docs/usage/pipe_analyzer.md`, `docs/usage/pipe_digital_valve.md`

## Change history

- 2026-11-21: remade and renamed. Rewritten to be shorter; added the 2 °C band, analyzer-error shut-off and status on the housing.

## Status

Functional (author's label from before the remake; re-test in-game).
