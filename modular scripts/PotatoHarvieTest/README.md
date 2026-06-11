# PotatoHarvieTest (modular)

Compact modular potato grow test for one `Hydroponics Device`, one `Harvie`, and one
`Grow Light`.

Player setup guide: `modular scripts/PotatoHarvieTest/Setup.md`.

## Architecture

- `potato_harvie_test_master.ic10` - reads the auto lever and republishes module mode
- `potato_harvie_test_worker_sensor.ic10` - reads the hydroponics device and plant slot
- `potato_harvie_test_worker_actuator.ic10` - drives Harvie and Grow Light
- `potato_harvie_test_setup_guard.ic10` - validates wiring and initializes memories once

This first version is intentionally a **test module**:

- targets `Hydroponics Device`, not `Hydroponics Station`
- uses a simple always-on light policy while a plant is present
- focuses on reliable plant / harvest behavior before advanced light cycling

## Device mapping per chip

### Master

- `d0` = `sensor_worker` housing
- `d1` = `actuator_worker` housing
- `d2` = Logic Memory `cmd_token`
- `d3` = Logic Memory `cmd_type`
- `d4` = auto lever
- `d5` = `n5`
- `db` = master status

### Sensor worker

- `d0` = Hydroponics Device
- `d1` = Logic Memory `slot0`
- `d2` = Logic Memory `slot1`
- `d3` = Logic Memory `slot2`
- `d4` = `n4`
- `d5` = `n5`
- `db` = sensor status

### Actuator worker

- `d0` = Harvie
- `d1` = Grow Light
- `d2` = Logic Memory `cmd_type`
- `d3` = Logic Memory `slot0`
- `d4` = Logic Memory `slot1`
- `d5` = Logic Memory `slot2`
- `db` = actuator status

### Setup guard

- `d0` = `sensor_worker` housing
- `d1` = `actuator_worker` housing
- `d2` = Logic Memory `cmd_token`
- `d3` = Logic Memory `cmd_type`
- `d4` = auto lever
- `d5` = `n5`
- `db` = setup status

Inter-chip links therefore start at `d0` and descend before player controls, matching the
repo modular wiring rule.

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

## Shared memory contract

- `cmd_token` - increments whenever the master republishes lever mode
- `cmd_type` - `0 = off`, `1 = auto`
- `slot0` - plant flags bitfield
  - `1` occupied
  - `2` mature
  - `4` seeding
  - `8` health above `0.5`
- `slot1` - current plant `Growth` value from slot `0`
- `slot2` - environment flags bitfield
  - `1` temperature in potato ideal range (`20-30 C`)
  - `2` pressure in potato ideal range (`50-100 kPa`)
  - `4` water present
  - `8` carbon dioxide present

## Runtime flow

1. `setup_guard` validates the lever and initializes `cmd_token` / `cmd_type` once.
2. `master` reads the auto lever and republishes `cmd_type`.
3. `sensor_worker` reads plant slot `0` plus tray environment values.
4. `actuator_worker` keeps Harvie powered in auto mode.
5. If the tray is empty and Harvie has seed input, it pulses `Plant`.
6. If the tray is mature and Harvie is idle, it pulses `Harvest`.
7. Grow Light is on while the tray is occupied or seed stock is waiting at Harvie.

## Potato assumptions used by this test module

- ideal air temperature: `20-30 C`
- ideal pressure: `50-100 kPa`
- the test module does **not** implement the full 5-minute light / 3:20 dark cycle yet
- this module is intended to prove device control and slot-reading first

## Status protocol (`db Setting`)

### Master (`0-99`)

- `0` = boot
- `10` = published off mode
- `20` = published auto mode
- `1` = healthy steady off
- `2` = healthy steady auto

### Sensor worker (`100-199`)

- `100` = boot / idle
- `110` = latest tray sample written

### Actuator worker (`200-299`)

- `200` = off mode steady
- `210` = auto steady
- `220` = plant pulse written
- `230` = harvest pulse written

### Setup guard (`0-99`)

- `0` = boot
- `10` = one-time init complete
- `1` = setup valid
- `94` = wrong control wired to `d4` (expected logic lever)

## Recovery steps

- If `setup_guard != 1`, fix master / setup wiring first.
- If `master` never leaves `1` or `2`, verify the lever is wired to `d4`.
- If `sensor_worker` does not reach `110`, verify the Hydroponics Device is on `d0`.
- If `actuator_worker` stays at `210` but never plants, check Harvie import seeds.
- If plants are present but not growing well, remember this V1 module does not yet manage
  advanced lighting schedules or gas conditioning.
