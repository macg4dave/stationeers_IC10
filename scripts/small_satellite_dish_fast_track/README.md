# small_satellite_dish_fast_track

## Purpose

Early-game single-chip tracker for a **Small Satellite Dish**.

It uses just:

- 1× IC Housing + IC Chip
- 1× Small Satellite Dish

Behavior:

- powers the dish on at startup
- sets dish `Setting` to `99999` at startup
- sweeps the sky in `30°` horizontal steps and `15°` vertical rows
- when it sees a contact, locks `BestContactFilter` to that `SignalID`
- locally peaks the contact by nudging horizontal/vertical aim
- pulses `Activate = 1` once when the dish can reach the target

This is meant to be the cheap, no-extra-parts option before building the full
multi-chip `SatCom` setup.

## Devices

Required:

- 1× Small Satellite Dish
- 1× IC Housing + IC Chip

Optional:

- none

## Device registers

- `d0` = Small Satellite Dish
- `db` = IC Housing (status/debug)

Suggested in-game names (optional):

- Small Satellite Dish: `dish_small_1`
- IC Housing: `dish_fast_track_1`

## Usage

1. Place one **Small Satellite Dish** and one **IC Housing** on the same data network.
2. Assign the dish to `d0`.
3. Paste `small_satellite_dish_fast_track.ic10` into the IC.
4. Power the network and wait for the sweep to settle onto a target.

## Tuning

Edit the `define` values near the top of `small_satellite_dish_fast_track.ic10`:

- `WATTS` — power setting written to the dish (default `99999`)
- `STARTV` — sweep start vertical angle (default `15`)
- `SWH` — coarse horizontal sweep step in degrees (default `30`)
- `SWV` — coarse vertical sweep row step in degrees (default `15`)
- `STEP` — fine tracking nudge size in degrees (default `4`)
- `SETTLE` — wait time after coarse moves before reading signals (default `5`)

## Debug / status

The IC Housing `db Setting` shows:

- `100` = coarse sweep mode
- `110` = target found, filter lock written
- `120` = peak tracking step
- `130` = `Activate` pulse sent
- `902` = dish reports `Error = 1`

## Notes

- This script assumes the small dish uses the same logic fields as the large/medium
  dishes in this repo's catalog.
- Trust `SignalID` and `SignalStrength` only when `Idle = 1`.
- `SignalStrength = -1` means no usable reading.
- Bigger `SignalStrength` is better, even when values are negative.
- `MinimumWattsToContact = -1` is treated as "no extra gate available", so the
  script will still pulse `Activate` once.
- If the dish seems inactive, check power, data network connection, and in-game dish
  error state first.
- For general dish gotchas, also see `docs/usage/large_satellite_dish.md`.

## Status

Functional
