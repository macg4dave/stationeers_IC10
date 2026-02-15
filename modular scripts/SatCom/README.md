# SatCom control system (modular)

Name-first SatCom automation for a Satellite Dish using a master + workers.
All active scripts now use exact prefab+name lookup (`lbn`/`sbn`).

Player setup guide: `modular scripts/SatCom/Setup.md`.

## Architecture

- `satcom_master.ic10` - orchestration and status aggregation
- `satcom_setup_guard.ic10` - name/type validation + worker/channel init helper
- `satcom_worker_controls.ic10` - auto command worker (buttonless)
- `satcom_worker_discover_coordinator.ic10` - discover coordinator (`discover_worker`) aggregating worker contacts
- `satcom_worker_discover_1.ic10` - discover variant 1 (legacy compact)
- `satcom_worker_discover_2.ic10` - discover variant 2 (grid + local peak)
- `satcom_worker_discover_3.ic10` - discover variant 3 (track/interrogate)

## Multi-dish discover mode (current)

Each discover chip runs against its own dedicated **Medium Satellite Dish**.

- `satcom_worker_discover_1.ic10` -> its own medium dish (wired to that chip `d0`)
- `satcom_worker_discover_2.ic10` -> its own medium dish (wired to that chip `d0`)
- `satcom_worker_discover_3.ic10` -> its own medium dish (wired to that chip `d0`)

Default horizontal sweep sectors (to reduce overlap):

- `dish_1` / discover 1: `0..120` deg
- `dish_2` / discover 2: `120..240` deg
- `dish_3` / discover 3: `240..360` deg

Important:

- Discovery/targeting logic inside each discover script is intentionally unchanged.
- Integration updates are limited to setup/wiring and device-resolution around workers.

`satcom_master.ic10`/`satcom_worker_controls.ic10` coordinate one named worker
(`discover_worker`). In multi-dish mode, assign that role to
`satcom_worker_discover_coordinator.ic10`.

Coordinator + discover variants:

- Keep `satcom_worker_discover_coordinator.ic10` housing named `discover_worker` (SatCom Discover Coordinator).
- Run discover variants on dedicated chips named:
  - `discover_worker_1`
  - `discover_worker_2`
  - `discover_worker_3`
- Each discover worker uses its own dedicated dish (`dish_1..dish_3`, wired to
  that chip `d0`).
- Coordinator reads `dish_1..dish_3` `SignalID` values, applies slot blacklist
  from prior run, and writes consolidated results to `slot0..slot2`.

## Name contract

Required exact names:

- IC Housing: `discover_worker` (SatCom Discover Coordinator), `controls_worker`
- IC Housing: `discover_worker_1`, `discover_worker_2`, `discover_worker_3`
- Logic Memory: `cmd_token`, `cmd_type`, `slot0`, `slot1`, `slot2`
- Satellite Dish: `dish_1`, `dish_2`, `dish_3` (discover workers)

Implementation notes:

- Workers and channels are targeted by prefab+name, not chip pin mapping.
- Master/setup guard read IC Housing prefab from `db PrefabHash`, so use one
  housing variant across SatCom ICs.

## Shared memory contract

Use Logic Memory `Setting` channels:

- `slot0` - first discovered `SignalID`
- `slot1` - second discovered `SignalID`
- `slot2` - third discovered `SignalID`
- `cmd_token` - incrementing command token
- `cmd_type` - command code
- Empty contact sentinel is `-1` only (`0` is not used as empty).

Command codes:

- `1` = discover (rebuild contact slots)

Workers execute commands only when `cmd_token` changes.

## Wiring

- Put all SatCom devices on one shared data network.
- Name-targeted workers do not require `d0..d5` mapping.
- Discover variants still require local pins:
  - `discover_1`: `d0` -> `dish_1`
  - `discover_2`: `d0` -> `dish_2`
  - `discover_3`: `d0` -> `dish_3`
- Current dish prefab hash used by SatCom scripts: `-449434216` (Medium Satellite).

## Controls

- Controls worker is fully automatic (no button/lever/dial dependencies).
- Auto-discover triggers when `slot0..slot2` are all `-1` and discover is idle.
- While discover is active (`110`/`120`), controls worker stays in ready state.
- To force a new auto discover run, set all `slot0..slot2` back to `-1`.

## Known engine behaviors

- `SignalID=-1` means no contact; SatCom scripts treat only `-1` as empty.
- Dish movement or power state changes can reset acquisition; wait for `Idle=1`.
- Dish control/readback requires the dish and ICs on the same data network.

## Status protocol (`db Setting`)

Each chip writes status to its own housing `Setting`.

### Master status (`0-99`)

- `0` = init
- `1` = idle/ready
- `2` = discover worker busy
- `5` = contacts available
- `10` = discover command sent
- `44` = controls worker reports missing/wrong controls

### Setup guard status (`90-99`)

- `1` = setup valid
- `91` = missing/wrong `cmd_token`
- `92` = missing/wrong `cmd_type`
- `93` = missing/wrong `discover_worker` housing
- `90` = missing/wrong `controls_worker` housing
- `97` = missing/wrong `dish_1`/`dish_2`/`dish_3` device
- `98` = missing/wrong `slot0/slot1/slot2` memory

### Controls worker status (`340-349`)

- `340` = idle/ready
- `341` = discover command sent
- `344` = missing/wrong `discover_worker` housing

### Discover worker status (`100-199`)

- `100` = idle
- `110` = discover start/reset
- `120` = sweeping step / sweep retry
- `130` = complete with 3 new contacts
- `132` = complete with 2 new contacts

Coordinator behavior:

- `discover_worker` status now comes from `satcom_worker_discover_coordinator.ic10`.
- On command `1` (discover), coordinator snapshots prior `slot0..slot2` as run
  blacklist, clears slots to `-1`, and starts collecting new IDs from
  `dish_1..dish_3`.

Discover worker never writes `BestContactFilter`.

Discover flow details:

- on `discover`, current `slot0..slot2` are treated as a blacklist for that run
- worker scans coarse first (`30` deg step), then retries fine (`15` deg step)
- sweep rows are vertical `60` down to `0`, with horizontal full-circle passes
- worker keeps sweeping until it finds at least 2 new contacts
- if a sweep finds fewer than 2 new contacts, it restarts sweeping automatically

## Limits

- Every `.ic10` stays within 128 lines and 90 chars per line.
- Validate with:
  - `python tools/ic10_size_check.py "modular scripts/SatCom" --ext .ic10`
  - `python tools/setup_contract_check.py`
