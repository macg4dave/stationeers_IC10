# PotatoHarvieTest (modular)

Compact modular potato grow test for one `Hydroponics Device`, one or more `Harvie`
devices, one `Grow Light`, and one `Daylight Sensor`.

Player setup guide: `modular scripts/PotatoHarvieTest/Setup.md`.

## Architecture

- `potato_harvie_test_master.ic10` - reads the auto lever and republishes module mode
- `potato_harvie_test_worker_sensor.ic10` - reads plant state plus daylight availability
- `potato_harvie_test_worker_actuator.ic10` - drives Harvie and Grow Light timing
- `potato_harvie_test_setup_guard.ic10` - validates wiring and initializes memories once

This version is still intentionally compact:

- targets `Hydroponics Device`, not `Hydroponics Station`
- forces the Grow Light on during the active light window and off during dark time
- publishes plant `Efficiency` as a diagnostic memory value

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
- `d4` = Daylight Sensor
- `d5` = `n5`
- `db` = sensor status

### Actuator worker

- `d0` = reference Harvie (used to discover the Harvie prefab hash)
- `d1` = Grow Light
- `d2` = Logic Memory `cmd_type`
- `d3` = Logic Memory `slot0`
- `d4` = `n4`
- `d5` = `n5`
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
  - `16` daylight available (sun above horizon)
- `slot1` - current plant `Growth` value from slot `0`
- `slot2` - current plant `Efficiency` from slot `0` (diagnostic)
  - `-1` empty
  - `1.0` baseline growth efficiency
  - values below `1.0` suggest the plant is under-performing

## Runtime flow

1. `setup_guard` validates the lever and initializes `cmd_token` / `cmd_type` once.
2. `master` reads the auto lever and republishes `cmd_type`.
3. `sensor_worker` reads plant slot `0`, plant `Efficiency`, and daylight state.
4. `actuator_worker` keeps all Harvies on the data network powered in auto mode.
5. If the tray is empty and any Harvie has seed input, it batch-pulses `Plant`.
6. If the tray is mature and all Harvies are idle, it batch-pulses `Harvest`.
7. Grow Light is forced on during the active light window.
8. The module waits for real darkness before crediting the potato dark window.

## Potato assumptions used by this test module

- lighting target: `5 min` light, `3 min 20 sec` dark
- timing uses `yield` ticks and assumes **~2 ticks/sec**
  - `LIGHT_TICKS = 600`
  - `DARK_TICKS = 400`
- the Daylight Sensor is treated as a daylight-available indicator, not a lux meter
- Grow Light is forced on during the light window and off during the dark window
- for best results, mount the Daylight Sensor in the same daylight conditions as the tray

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
- `210` = auto steady / empty tray
- `211` = reserved
- `212` = auto light phase using Grow Light
- `213` = auto dark phase waiting for / accruing darkness
- `220` = plant pulse written
- `221` = Harvie busy after a plant or harvest command
- `230` = harvest pulse written

### Setup guard (`0-99`)

- `0` = boot
- `10` = one-time init complete
- `1` = setup valid
- `94` = wrong control wired to `d4` (expected logic lever)

## Recovery steps

- If `setup_guard != 1`, fix master / setup wiring first.
- If `master` never leaves `1` or `2`, verify the lever is wired to `d4`.
- If `sensor_worker` does not reach `110`, verify `Hydroponics Device` is on `d0`
  and `Daylight Sensor` is on `d4`.
- If `actuator_worker` stays at `210` but never plants, check Harvie import seeds.
- The actuator batch-controls every Harvie on the same data network as the worker.
  Keep unrelated Harvies off that network or split them behind another worker.
- If plants still over-light, remember this module cannot block excess sunlight without a
  separate shutter / blackout system.
