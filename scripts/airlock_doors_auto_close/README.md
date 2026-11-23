# airlock_doors_auto_close

Closes any of three airlock doors (outside, middle, inside) within 1 s of it opening,
and turns on the **Active Vents named `AIRLOCK_VENT`** in the direction you choose. The
vents turn off again after 5 s with no door opening or closing.

## Pins

The IC Housing shows these names on its pins once the script is running.

| Pin | Name | Device |
| --- | --- | --- |
| `d0` | `outside` | Door to the outside (e.g. Glass Door) |
| `d1` | `middle` | Middle door |
| `d2` | `inside` | Door to the inside |

**Network devices:** Active Vents named exactly `AIRLOCK_VENT` (case-sensitive). The IC
Housing must be on the same data network as the vents.

## What it does

- Every tick (0.5 s) it reads each door's `Open`. A door seen open on two ticks running
  is closed (`Open` 0), so it closes 0.5–1 s after it opens.
- Each time it closes a door it turns the vents on: `Mode` = `VENT_MODE` (written only
  when the vents are not already in that mode, because changing `Mode` resets an Active
  Vent's pressure limits), one tick later `Open` 1 and `On` 1.
- Any door opening or closing (by hand or by the script) restarts a timer. After
  `OFF_S` seconds with no change, the vents are turned off (`On` 0, `Open` 0).
- If a door pin is not set, the status shows `9` and nothing is closed until it is.

## Settings

Edit the `define` lines at the top of `airlock_doors_auto_close.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `VENT_MODE` | `1` | Vent direction: `0` Outward (pipe → room), `1` Inward (room → pipe) |
| `OFF_S` | `5` | Seconds with no door opening or closing before the vents turn off |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | vents off (waiting) |
| `1` | vents on (a door was closed less than `OFF_S` s ago) |
| `9` | a door pin is not set |

## Setup

1. Build the three doors, the Active Vents and the IC Housing on one powered data network.
2. Rename the vents exactly `AIRLOCK_VENT` (Labeller).
3. In the IC Housing screen, set `d0` to the outside door, `d1` to the middle door and
   `d2` to the inside door.
4. Set `VENT_MODE` for the direction you want, paste `airlock_doors_auto_close.ic10`
   into the chip and run it.

## Notes

- Opening a door by hand still works, but it closes again within 1 s: walk through
  quickly. A door that takes longer than a tick to close is closed again on the next
  tick, which is harmless.
- Device notes: `docs/usage/active_vent.md`.

## Change history

- 2026-11-23: vents turn off after `OFF_S` (5) s with no door opening or closing
  (owner's request). Status `0` now means vents off.
- 2026-11-23: new script (owner's request).

## Status

Functional (author's label). Simulated, not yet run in-game.
