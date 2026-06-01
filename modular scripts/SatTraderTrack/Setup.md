# SatTraderTrack setup (direct wiring)

Use this page to wire `SatTraderTrack` as a compact modular feature.
This version is intentionally direct-wired so each IC chip stays under Stationeers paste limits.

## Build list

- 4x IC Housing + IC Chip
  - SatTraderTrack Master
  - SatTraderTrack Dish Worker
  - SatTraderTrack Landing Worker
  - SatTraderTrack Setup Guard
- 2x Logic Memory
  - `cmd_token`
  - `cmd_type`
- 1x Medium Satellite Dish
- 1x Large Satellite Dish
- 1x Logic Switch Dial
- 1x Logic Switch Lever
- 2x LED Display
- existing landingpad data network pieces
- optional flash light + klaxon speaker on the same data network

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

## Setup steps

1. Put the chips, memories, dishes, dial, lever, and displays on the same base data/power network.

1. Paste scripts:

- `modular scripts/SatTraderTrack/sat_trader_track_master.ic10`
- `modular scripts/SatTraderTrack/sat_trader_track_worker_dish.ic10`
- `modular scripts/SatTraderTrack/sat_trader_track_worker_landing.ic10`
- `modular scripts/SatTraderTrack/sat_trader_track_setup_guard.ic10`

1. Name the dishes exactly `dish_m` and `dish_l`.

1. Wire the **master** chip:

- `d0` -> `dish_worker` housing
- `d1` -> `landing_worker` housing
- `d2` -> Logic Memory `cmd_token`
- `d3` -> Logic Memory `cmd_type`
- `d4` -> trader-type dial
- `d5` -> trader-type LED display

1. Wire the **dish worker** chip:

- `d0` -> medium dish
- `d1` -> large dish
- `d2` -> Logic Memory `cmd_token`
- `d3` -> Logic Memory `cmd_type`
- `d4` -> auto-land lever
- `d5` -> step/status LED display

1. Wire the **setup guard** chip exactly like the master chip.

1. Wire the **landing worker** chip:

- `d0` -> medium dish
- `d1` -> large dish
- `d2` -> trader-type LED display
- `d3` -> step/status LED display
- `d4` -> unused
- `d5` -> unused

1. Power everything and wait until `setup_guard` shows `db Setting = 1`.

1. Set the dial value:

- `0` = accept any `ContactTypeId`
- any other value = exact `ContactTypeId` to match

1. Turn the lever on if you want the final landing pulse after interrogation.

## Pin label convention

- The landing worker aliases `d4..d5` as `n4..n5`.
- The other chips use every local pin explicitly, so their in-game labels should match the wiring map above.

## Controls

- trader dial on master `d4`: selects the exact `ContactTypeId` to chase; `0` means any type
- auto-land lever on dish worker `d4`: enables the final call-down pulse after successful interrogation
- type LED on master `d5`: mirrors the current dial value
- step LED on dish worker `d5`: shows selected type during scan and purple (`11`) during interrogation / landing
- landing worker: no player control; it mirrors landingpad online state to both dishes/displays and drives optional alert outputs on landingpad mode `4`

## Setup guard status (`db Setting`)

- `0` boot
- `10` one-time init complete
- `1` setup valid
- `97` missing/wrong required dish (`dish_m` or `dish_l`)
- `94` wrong control wired to `d4` (expected trader dial)

## Runtime debug snapshot (required for issue reports)

When debugging, capture these values in one screenshot/note:

- `master` (`db Setting`)
- `dish_worker` (`db Setting`)
- `landing_worker` (`db Setting`)
- `setup_guard` (`db Setting`)
- `cmd_token` and `cmd_type`

Quick interpretation:

- if `cmd_token` increments when the dial changes, the master path is working
- if `setup_guard = 97`, fix the `dish_m` / `dish_l` names or missing large-dish wiring first
- if `dish_worker = 125`, the module is handing tracking off to the large dish
- if `dish_worker = 151`, interrogation finished but the lever/type gate blocked landing
- if `landing_worker = 210`, landingpad mode `4` is active and the alert outputs are being driven
