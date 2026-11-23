# room_heater_hold_20c

Keeps a room warm: **every Wall Heater on the data network** turns on when a **Gas Sensor** reads below 20 °C and off again above 22 °C.

*Previously called `room_heater_below_20c`.*

## Pins

| Pin | Name | Device |
| --- | --- | --- |
| `d0` | `sensor` | Gas Sensor (in the room) |

**Network devices:** every Wall Heater on the IC Housing's data network, found by type
(prefab hash `24258244`, `StructureWallHeater`). No names needed. `d1` is no longer used.

## What it does

- Below 20 °C: heaters ON.
- Above 22 °C: heaters OFF.
- 20–22 °C: keeps whatever it is doing (no flicker).
- No reading (sensor in vacuum or wrong device): heaters OFF, status 9.
- Heaters are written only when one of them differs from the wanted state, so a heater
  switched by hand is put back on the next tick.
- At start the chip picks up the current state: if any heater is on, it holds "on"
  until the room passes 22 °C.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `room_heater_hold_20c.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `HEAT_ON_BELOW_C` | `20` | Heater turns on below this (°C) |
| `HEAT_OFF_ABOVE_C` | `22` | Heater turns off above this (°C) |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | heaters off |
| `1` | heaters on |
| `9` | device missing or no reading |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
   Every Wall Heater on that network is controlled, so keep heaters for other rooms on
   another network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `room_heater_hold_20c.ic10` into the chip and run it.

## Notes

- Device notes: `docs/usage/gas_sensor.md`, `docs/usage/wall_heater.md`

## Change history

- 2026-11-23: controls every Wall Heater on the network by type (user request) instead of
  the one on `d1`. **Pin change:** `d1` is no longer read; the heater only needs to be on the
  data network.
- 2026-11-21: remade and renamed. On/off now has a 2 °C band (was a single 20 °C threshold). The Gas Sensor prefab check was replaced by a "no reading" check, so any sensor with `Temperature` works. Status on the housing.

## Status

Functional (author's label from before the remake; re-test in-game).
