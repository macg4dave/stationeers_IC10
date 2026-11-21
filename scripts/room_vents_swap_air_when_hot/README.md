# room_vents_swap_air_when_hot

When a room gets hot, swaps its air: **vents named `IN`** blow fresh gas in while **vents named `OUT`** pull room air out.

*Previously called `active_vent_dual_sets`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Gas Sensor (in the room) |

**Network devices:** Active Vents named exactly `IN` (supply pipe side) and `OUT` (exhaust pipe side). The IC Housing must be on the same data network as the named devices.

## What it does

- Above 30 °C: `IN` vents Outward (pipe → room, limit 60 MPa), `OUT` vents Inward (room → pipe, limit 0 kPa), all on and locked.
- Below 28 °C: both groups OFF, closed, unlocked.
- 28–30 °C: holds.
- At start-up it always applies a known state; while running it re-applies every ~60 s.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `room_vents_swap_air_when_hot.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `ON_ABOVE_C` | `30` | Start swapping above (°C) |
| `OFF_BELOW_C` | `28` | Stop below (°C) |
| `IN_SETTING_KPA` | `60000` | IN vents' pressure limit |
| `OUT_SETTING_KPA` | `0` | OUT vents' pressure limit |
| `LOOP_SLEEP_S` | `2` | Seconds between checks |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | off |
| `1` | swapping |
| `9` | sensor missing or no reading |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `room_vents_swap_air_when_hot.ic10` into the chip and run it.
4. Rename the network devices exactly as listed above (Labeller).

## Notes

- Device notes: `docs/usage/active_vent.md`

## Change history

- 2026-11-21: remade and renamed. Added the 28–30 °C band; checks every 2 s instead of 5 s; status on the housing.
- 2026-11: on a cold start both groups are switched off (before, vents left running kept running).

## Status

Functional (author's label from before the remake; re-test in-game).
