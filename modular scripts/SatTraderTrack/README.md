# SatTraderTrack (modular)

Compact modular trader tracker split into:

- a direct-wired master for type selection + worker enable
- a direct-wired dish worker for required medium+large scan / interrogate / auto-land
- a direct-wired pad/alert worker for required medium+large gating + alert outputs
- a setup guard that initializes the shared command memories once

Player setup guide: `modular scripts/SatTraderTrack/Setup.md`.

## Architecture

- `sat_trader_track_master.ic10` - reads the trader dial, mirrors it to the type display, and republishes the selected `ContactTypeId`
- `sat_trader_track_worker_dish.ic10` - owns the required medium+large dish pair, interrogation, and final auto-land pulse
- `sat_trader_track_worker_landing.ic10` - gates the required medium+large dish pair by landingpad online state and drives the original alert outputs while landingpad mode is `4`
- `sat_trader_track_setup_guard.ic10` - validates the direct-wired control path and initializes `cmd_token` / `cmd_type` once

## Device mapping per chip

### Master

- `d0` = `dish_worker` housing
- `d1` = `landing_worker` housing
- `d2` = Logic Memory `cmd_token`
- `d3` = Logic Memory `cmd_type`
- `d4` = trader-type dial
- `d5` = trader-type LED display
- `db` = master status

### Dish worker

- `d0` = medium dish
- `d1` = large dish
- `d2` = Logic Memory `cmd_token`
- `d3` = Logic Memory `cmd_type`
- `d4` = auto-land lever
- `d5` = step/status LED display
- `db` = dish runtime status

### Landing worker

- `d0` = medium dish
- `d1` = large dish
- `d2` = trader-type LED display
- `d3` = step/status LED display
- `d4` = `n4`
- `d5` = `n5`
- `db` = landingpad gate / alert status

### Setup guard

- `d0` = `dish_worker` housing
- `d1` = `landing_worker` housing
- `d2` = Logic Memory `cmd_token`
- `d3` = Logic Memory `cmd_type`
- `d4` = trader-type dial
- `d5` = trader-type LED display
- `db` = setup status

Inter-chip links therefore start at `d0` and descend before controls / feature devices, matching the repo’s modular wiring rule.

## Name contract

Set these exact names (case-sensitive):

- IC Housing: `master`
- IC Housing: `dish_worker`
- IC Housing: `landing_worker`
- IC Housing: `setup_guard`
- Medium Satellite Dish: `dish_m`
- Large Satellite Dish: `dish_l`
- Logic Memory: `cmd_token`
- Logic Memory: `cmd_type`

Internal prefab/name tokens referenced by the scripts:

- `Landingpad_DataConnectionPiece`
- `Large_Satellite_Dish`

## Shared memory contract

- `cmd_token` - increments whenever `master` republishes a changed trader selection
- `cmd_type` - selected `ContactTypeId`
  - `0` means "accept any contact type"

## Runtime flow

1. `master` reads the dial and mirrors it to the type LED.
2. When the dial changes, `master` writes that new value to `cmd_type` and increments `cmd_token`.
3. `landing_worker` mirrors landingpad online state to the dish, `type_led`, and `step_led`, matching the original script’s visible idle/off behavior.
4. `dish_worker` keeps the original sine-wave scan, target filter, large-dish handoff, interrogation, and final auto-land pulse.
5. This module now assumes the large dish is always present and wired on `d1`.
6. When the active dish can reach contact watt requirements, the worker pulses `Activate` to interrogate.
7. When interrogation finishes, the worker sends the final landing pulse if the lever is on and the contact type still matches the selected value (or the selected value is `0`).
8. `landing_worker` drives the original flash light / klaxon alert path while landingpad mode is `4`.

## Status protocol (`db Setting`)

### Master (`0-99`)

- `0` = boot
- `1` = healthy / steady
- `10` = published updated dial value

### Dish worker (`100-199`)

- `100` = boot / idle baseline
- `125` = switching to large dish
- `140` = interrogation pulse written
- `150` = auto-land pulse written
- `151` = interrogation finished but lever/type gate blocked landing

### Landing worker (`200-299`)

- `200` = no landing alert active
- `201` = landingpad online, no alert active
- `210` = landing alert active (`Mode = 4`)

### Setup guard (`0-99`)

- `0` = boot
- `10` = one-time init complete
- `1` = setup valid
- `94` = wrong control wired to `d4` (expected trader dial)

## Notes

- This modular version intentionally replaces the original undocumented `peek` mapping with a direct rule: the dial value is the exact `ContactTypeId` to match.
- Set the dial to `0` for "any trader" mode.
- This module no longer supports a medium-only configuration; both `dish_m` and `dish_l` are required.
- The original landingpad alert path is restored in `landing_worker`; keep the flash light and klaxon on the same data network if you want that behavior.

## Recovery steps

- If `setup_guard` is not `1`, fix master/setup direct wiring first.
- If `setup_guard = 97`, one of the required dishes is missing/wrong-name (`dish_m` or `dish_l`).
- If `dish_worker` stays at `100`, the dish is currently gated off by landingpad offline state.
- If `dish_worker = 151`, the interrogation completed but the lever was off or the contact type did not match the dial.
- If `landing_worker = 210`, the module sees landingpad mode `4` and is actively driving the flash light / klaxon outputs.
