# greenhouse_co2_pressure_vent

Tops up a greenhouse from a CO2-rich pipe: an **Active Vent** runs when CO2 is low or the room pressure is low.

*Previously called `room_co2_below_20pct_active_vent`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Gas Sensor (in the room) |
| `d1` | Active Vent |

## What it does

- Vent ON + Open while CO2 < 20 % **or** room < 100 kPa.
- Vent OFF once CO2 > 22 % **and** room ≥ 100 kPa.
- The vent is kept in `VENT_MODE` with `Setting` = 100 kPa, so it never pushes the room above 100 kPa.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `greenhouse_co2_pressure_vent.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `CO2_LOW` | `0.20` | Start below this CO2 ratio |
| `CO2_OK` | `0.22` | Stop above this CO2 ratio |
| `ROOM_KPA` | `100` | Minimum room pressure and the vent's limit (kPa) |
| `VENT_MODE` | `0` | 0 = Outward (pipe → room), 1 = Inward |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | vent off |
| `1` | vent on |
| `9` | device missing |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `greenhouse_co2_pressure_vent.ic10` into the chip and run it.

## Notes

- Device notes: `docs/usage/active_vent.md`, `docs/usage/gas_sensor.md`

## Change history

- 2026-11-21: remade and renamed. Added the 20–22 % CO2 band; dropped the Gas Sensor prefab check; status on the housing.
- 2026-11: removed the "divide by 1000" pressure guess.

## Status

Functional (author's label from before the remake; re-test in-game).
