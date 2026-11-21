# room_door_open_when_hot

Opens a **Glass Door** when the room gets hot (to let heat out) and closes it again once the room has cooled.

*Previously called `gas_sensor_glass_door_30c`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Gas Sensor |
| `d1` | Glass Door |

## What it does

- Above 30 °C: door OPEN.
- Below 28 °C: door CLOSED.
- 28–30 °C: holds.
- Keeps the door powered and unlocked so it can move.
- No reading: door left as it is, status 9.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `room_door_open_when_hot.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `OPEN_ABOVE_C` | `30` | Open above (°C) |
| `CLOSE_BELOW_C` | `28` | Close below (°C) |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | closed |
| `1` | open |
| `9` | device missing or no reading |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `room_door_open_when_hot.ic10` into the chip and run it.

## Notes

- Device notes: `docs/usage/gas_sensor.md`

## Change history

- 2026-11-21: remade and renamed. Added the 28–30 °C band (it used to flip at exactly 30 °C); status on the housing.

## Status

Functional (author's label from before the remake; re-test in-game).
