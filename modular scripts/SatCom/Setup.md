# SatCom setup (name auto-naming)

Use exact names and one shared data network. Most SatCom scripts target devices
by prefab+name (`lbn`/`sbn`), but discover variants still require local `d0`.

## Build list

### Multi-dish discover workers (current)

- 3x IC Housing + IC Chip
  - Discover worker 1 (`satcom_worker_discover_1.ic10`)
  - Discover worker 2 (`satcom_worker_discover_2.ic10`)
  - Discover worker 3 (`satcom_worker_discover_3.ic10`)
- 3x **Medium Satellite Dish** (one dedicated dish per discover worker)

Per-chip pin map for discover workers:

- `satcom_worker_discover_1.ic10`
  - `d0` -> dedicated Medium Satellite Dish named `dish_1` (sweeps `0..120` deg)
- `satcom_worker_discover_2.ic10`
  - `d0` -> dedicated Medium Satellite Dish named `dish_2` (sweeps `120..240` deg)
- `satcom_worker_discover_3.ic10`
  - `d0` -> dedicated Medium Satellite Dish named `dish_3` (sweeps `240..360` deg)

### Shared-network master/controls stack (optional)

- 4x IC Housing + IC Chip
  - SatCom Master
  - SatCom Controls Worker
  - SatCom Discover Coordinator (`satcom_worker_discover_coordinator.ic10`, housing name `discover_worker`)
  - SatCom Setup Guard (recommended)
- 3x IC Housing + IC Chip
  - SatCom Discover Worker variant 1
  - SatCom Discover Worker variant 2
  - SatCom Discover Worker variant 3
- 5x Logic Memory
  - `cmd_token`
  - `cmd_type`
  - `slot0`
  - `slot1`
  - `slot2`

## Name contract

Set these exact names (case-sensitive):

- IC Housing: `master`
- IC Housing: `setup_guard` (recommended)
- IC Housing: `controls_worker`
- IC Housing: `discover_worker` (SatCom Discover Coordinator)
- IC Housing: `discover_worker_1`
- IC Housing: `discover_worker_2`
- IC Housing: `discover_worker_3`
- Logic Memory: `slot0`
- Logic Memory: `slot1`
- Logic Memory: `slot2`
- Logic Memory: `cmd_token`
- Logic Memory: `cmd_type`
- Satellite Dish: `dish_1`
- Satellite Dish: `dish_2`
- Satellite Dish: `dish_3`

Prefab tokens/hash used by scripts:

- `StructureLogicMemory`
- `-449434216` (Medium Satellite Dish prefab hash)

## Setup steps

- Put all devices on one data network.
- For multi-dish discover mode, wire each discover chip directly to its own dish
  on `d0`.
- Name those dishes exactly: `dish_1`, `dish_2`, `dish_3`.
- Paste scripts:
  - `modular scripts/SatCom/satcom_master.ic10`
  - `modular scripts/SatCom/satcom_worker_controls.ic10`
  - `modular scripts/SatCom/satcom_worker_discover_coordinator.ic10` (active discover_worker)
  - `modular scripts/SatCom/satcom_worker_discover_1.ic10`
  - `modular scripts/SatCom/satcom_worker_discover_2.ic10`
  - `modular scripts/SatCom/satcom_worker_discover_3.ic10`
  - `modular scripts/SatCom/satcom_setup_guard.ic10` (recommended)
- Apply exact names from **Name contract**.
- Keep coordinator housing named `discover_worker`.
- Name discover algorithm workers `discover_worker_1`, `discover_worker_2`,
  `discover_worker_3`.
- Ensure all SatCom IC housings are the same housing prefab variant.
- Power devices and wait a few ticks.
- Auto discover starts when all `slot0..slot2` are `-1`.

## Controls

- Controls worker is automatic (no button/lever/dial required).
- Scan runs when all slots are empty (`slot0=-1`, `slot1=-1`, `slot2=-1`).
- Coordinator collects from `dish_1`, `dish_2`, `dish_3` and writes shared slots.
- To trigger another run, set all three slot memories back to `-1`.
- Empty contact slots use sentinel `-1` only (no legacy `0` empty slots).

## Setup guard status (`db Setting`)

- `1` setup valid
- `90` missing/wrong `controls_worker` housing
- `91` missing/wrong `cmd_token`
- `92` missing/wrong `cmd_type`
- `93` missing/wrong `discover_worker` housing
- `97` missing/wrong `dish_1`/`dish_2`/`dish_3` device
- `98` missing/wrong `slot0/slot1/slot2` memory
