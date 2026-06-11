# PotatoHarvieTest setup (direct wiring)

Use this page to wire `PotatoHarvieTest` as a compact modular farm test.
This version is intentionally direct-wired so each IC chip stays paste-ready.

## Build list

- 4x IC Housing + IC Chip
  - PotatoHarvieTest Master
  - PotatoHarvieTest Sensor Worker
  - PotatoHarvieTest Actuator Worker
  - PotatoHarvieTest Setup Guard
- 5x Logic Memory
  - `cmd_token`
  - `cmd_type`
  - `slot0`
  - `slot1`
  - `slot2`
- 1x Logic Switch Lever
- 1x Hydroponics Device
- 1x Harvie
- 1x Grow Light

## Name contract

Set these exact names (case-sensitive):

- IC Housing: `master`
- IC Housing: `sensor_worker`
- IC Housing: `actuator_worker`
- IC Housing: `setup_guard`
- Logic Memory: `cmd_token`
- Logic Memory: `cmd_type`
- Logic Memory: `slot0`
- Logic Memory: `slot1`
- Logic Memory: `slot2`

## Setup steps

1. Put the chips, memories, lever, Hydroponics Device, Harvie, and Grow Light on the same
   base data / power network.

2. Paste scripts:

- `modular scripts/PotatoHarvieTest/potato_harvie_test_master.ic10`
- `modular scripts/PotatoHarvieTest/potato_harvie_test_worker_sensor.ic10`
- `modular scripts/PotatoHarvieTest/potato_harvie_test_worker_actuator.ic10`
- `modular scripts/PotatoHarvieTest/potato_harvie_test_setup_guard.ic10`

1. Wire the **master** chip:

- `d0` -> `sensor_worker` housing
- `d1` -> `actuator_worker` housing
- `d2` -> Logic Memory `cmd_token`
- `d3` -> Logic Memory `cmd_type`
- `d4` -> auto lever
- `d5` -> unused

1. Wire the **sensor worker** chip:

- `d0` -> Hydroponics Device
- `d1` -> Logic Memory `slot0`
- `d2` -> Logic Memory `slot1`
- `d3` -> Logic Memory `slot2`
- `d4` -> unused
- `d5` -> unused

1. Wire the **actuator worker** chip:

- `d0` -> Harvie
- `d1` -> Grow Light
- `d2` -> Logic Memory `cmd_type`
- `d3` -> Logic Memory `slot0`
- `d4` -> Logic Memory `slot1`
- `d5` -> Logic Memory `slot2`

1. Wire the **setup guard** chip exactly like the master chip.

1. Power everything and wait until `setup_guard` shows `db Setting = 1`.

1. Turn the lever on to enable **auto** mode.

## Pin label convention

- Master and setup guard alias `d5` as `n5`.
- Sensor worker aliases `d4..d5` as `n4..n5`.
- This keeps in-game pin labels current after updates.

## Controls

- auto lever on master `d4`
  - `0` = module off
  - `1` = module auto

## Setup guard status (`db Setting`)

- `0` boot
- `10` one-time init complete
- `1` setup valid
- `94` wrong control wired to `d4` (expected logic lever)

## Runtime debug snapshot (required for issue reports)

When debugging, capture these values in one screenshot / note:

- `master` (`db Setting`)
- `sensor_worker` (`db Setting`)
- `actuator_worker` (`db Setting`)
- `setup_guard` (`db Setting`)
- `cmd_token`, `cmd_type`, `slot0`, `slot1`, `slot2`

Quick interpretation:

- if `cmd_type` changes with the lever, master wiring is working
- if `sensor_worker = 110`, tray reads are live
- if `actuator_worker = 220`, a plant pulse was sent
- if `actuator_worker = 230`, a harvest pulse was sent
