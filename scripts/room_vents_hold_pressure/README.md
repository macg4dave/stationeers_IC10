# room_vents_hold_pressure

Uses **Active Vents named `ROOM_VENT`** to keep a room between 90 and 120 kPa: blowing air in when it is low, pulling it out when it is high.

*Previously called `room_pressure_active_vent`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Gas Sensor (in the room) |

**Network devices:** Active Vents named exactly `ROOM_VENT`, connected to a supply/exhaust pipe. The IC Housing must be on the same data network as the named devices.

## What it does

- Below 90 kPa: vents Outward (pipe → room) with a 120 kPa limit, until the room reaches 120 kPa.
- Above 120 kPa: vents Inward (room → pipe) with a 90 kPa limit, until the room is down to 90 kPa.
- In between: vents OFF.
- Sets the vents once when the state changes (Mode, then a tick later Setting, Open, On,
  Lock). A vent added or renamed while they run joins at the next change.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `room_vents_hold_pressure.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `LOW_KPA` | `90` | Start filling below (kPa) |
| `HIGH_KPA` | `120` | Start exhausting above (kPa) |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | idle |
| `1` | filling |
| `2` | exhausting |
| `9` | sensor missing |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `room_vents_hold_pressure.ic10` into the chip and run it.
4. Rename the network devices exactly as listed above (Labeller).

## Notes

- Device notes: `docs/usage/active_vent.md`, `docs/usage/gas_sensor.md`

## Change history

- 2026-11-21: removed the re-send every ~6 s. It worked around an old game bug that the
  user says is gone. Vents ran slowly in-game; re-writing `Mode` on running vents is the
  suspected cause (not yet confirmed). Vents are now set once per state change.
- 2026-11-21: remade and renamed. Shorter loop (one fill/exhaust routine); status on the housing.
- 2026-11: removed a "looks like Pa, divide by 1000" guess that made a room above 2 MPa look nearly empty.

## Status

Functional (author's label from before the remake; re-test in-game).
