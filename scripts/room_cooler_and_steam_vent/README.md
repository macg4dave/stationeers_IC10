# room_cooler_and_steam_vent

Two jobs from one **Gas Sensor**: a **Wall Cooler** runs while the room is hot, and an **Active Vent** runs while the room has no steam.

*Previously called `room_cooler_steamless_vent`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Gas Sensor (in the room) |
| `d1` | Wall Cooler |
| `d2` | Active Vent |

## What it does

- Cooler ON above 30 °C, OFF below 28 °C.
- Vent ON + Open while `RatioSteam` < 0.01 %, OFF once it is above 0.1 %.
- The vent's direction and pressure limit are **not** changed: set Mode/Setting in the vent's own screen.
- No reading: both OFF, status 9.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `room_cooler_and_steam_vent.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `COOL_ON_ABOVE_C` | `30` | Cooler on above (°C) |
| `COOL_OFF_BELOW_C` | `28` | Cooler off below (°C) |
| `STEAM_NONE_BELOW` | `0.0001` | Steam ratio counted as "none" |
| `STEAM_SEEN_ABOVE` | `0.001` | Steam ratio that stops the vent |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | both off |
| `1` | cooler on |
| `2` | vent on |
| `3` | both on |
| `9` | device missing or no reading |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `room_cooler_and_steam_vent.ic10` into the chip and run it.

## Notes

- Device notes: `docs/usage/gas_sensor.md`, `docs/usage/wall_cooler.md`, `docs/usage/active_vent.md`

## Change history

- 2026-11-21: remade and renamed. Added bands for the cooler (28–30 °C) and the steam check; both outputs off on a bad reading; status on the housing.

## Status

Functional (author's label from before the remake; re-test in-game).
