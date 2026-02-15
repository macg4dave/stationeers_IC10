# SatCom setup (name auto-naming)

Use exact names and one shared data network. SatCom scripts now target devices
by prefab+name (`lbn`/`sbn`) and do not require per-chip `d0..d5` mapping.

## Build list

### Multi-dish discover workers (current)

- 3x IC Housing + IC Chip
  - Discover worker 1 (`satcom_worker_discover_1.ic10`)
  - Discover worker 2 (`satcom_worker_discover_2.ic10`)
  - Discover worker 3 (`satcom_worker_discover_3.ic10`)
- 3x **Medium Satellite Dish** (one dedicated dish per discover worker)
- 1x LED (optional, local to discover worker 3)
- 1x Dial (optional, local to discover worker 3 eTrade filter)

Per-chip pin map for discover workers:

- `satcom_worker_discover_1.ic10`
  - `d0` -> dedicated Medium Satellite Dish named `dish_1`
- `satcom_worker_discover_2.ic10`
  - `d0` -> dedicated Medium Satellite Dish named `dish_2`
- `satcom_worker_discover_3.ic10`
  - `d0` -> dedicated Medium Satellite Dish named `dish_3`
  - `d1` -> optional LED
  - `d2` -> optional Dial

### Shared-network master/controls stack (optional)

- 4x IC Housing + IC Chip
  - SatCom Master
  - SatCom Controls Worker
  - SatCom Discover Worker (pick one discover variant)
  - SatCom Setup Guard (recommended)
- 2x IC Housing + IC Chip (optional staging)
  - SatCom Discover Worker variant 2
  - SatCom Discover Worker variant 3
- 1x IC Housing + IC Chip (optional)
  - SatCom Display Worker
- 1x IC Housing + IC Chip (optional)
  - SatCom Status LED Worker
- 5x Logic Memory
  - `cmd_token`
  - `cmd_type`
  - `slot0`
  - `slot1`
  - `slot2`
- 2x Logic Switch (Button)
  - Discover
  - Clear (use name `cycle`)
- 1x Logic Switch (Lever)
  - Manual Enable (`manual_enable`)
- 2x Logic Switch (Dial)
  - Horizontal (`dial_h`)
  - Vertical (`dial_v`)
- 1x Medium Satellite Dish
- 3x LED Display (optional)
  - Horizontal (`display_h`)
  - Vertical (`display_v`)
  - Status (`display_status`)

## Name contract

Set these exact names (case-sensitive):

- Button: `discover`
- Button: `cycle` (clear command)
- Lever: `manual_enable`
- Dial: `dial_h`
- Dial: `dial_v`
- IC Housing: `master`
- IC Housing: `setup_guard` (recommended)
- IC Housing: `controls_worker`
- IC Housing: `discover_worker`
- IC Housing: `discover_worker_2` (optional staging)
- IC Housing: `discover_worker_3` (optional staging)
- IC Housing: `display_worker` (optional)
- IC Housing: `status_led_worker` (optional)
- Logic Memory: `slot0`
- Logic Memory: `slot1`
- Logic Memory: `slot2`
- Logic Memory: `cmd_token`
- Logic Memory: `cmd_type`
- Satellite Dish: `dish_1`
- Satellite Dish: `dish_2`
- Satellite Dish: `dish_3`
- Medium Satellite Dish: `dish` (shared master/controls stack)
- LED Display: `display_h` (optional)
- LED Display: `display_v` (optional)
- LED Display: `display_status` (optional)

Prefab tokens/hash used by scripts:

- `StructureLogicMemory`
- `-449434216` (Medium Satellite Dish prefab hash)
- `StructureConsoleLED`
- `StructureConsoleLED5`
- `StructureConsoleLED1x2`
- `StructureConsoleLED1x3`
- `StructureLEDDisplay`

## Setup steps

- Put all devices on one data network.
- For multi-dish discover mode, wire each discover chip directly to its own dish
  on `d0` (and optional local `d1`/`d2` for discover 3).
- Name those dishes exactly: `dish_1`, `dish_2`, `dish_3`.
- Paste scripts:
  - `modular scripts/SatCom/satcom_master.ic10`
  - `modular scripts/SatCom/satcom_worker_controls.ic10`
  - `modular scripts/SatCom/satcom_worker_discover_1.ic10` (active discover worker)
  - `modular scripts/SatCom/satcom_worker_discover_2.ic10` (optional staging)
  - `modular scripts/SatCom/satcom_worker_discover_3.ic10` (optional staging)
  - `modular scripts/SatCom/satcom_setup_guard.ic10` (recommended)
  - `modular scripts/SatCom/satcom_worker_display.ic10` (optional)
  - `modular scripts/SatCom/satcom_worker_status_led.ic10` (optional)
- Apply exact names from **Name contract**.
- Keep the active discover worker housing named `discover_worker`.
- Ensure all SatCom IC housings are the same housing prefab variant.
- Controls worker initializes dial ranges at startup:
  - `dial_h` `Mode=359` (0..359 deg)
  - `dial_v` `Mode=89` (0..89 deg)
- Power devices and wait a few ticks.
- Press Discover.

## Controls

- Press Discover: scan until at least 2 new contacts and store them in `slot0..slot2`.
- Press Clear (`cycle` button): clear stored contacts and clear dish filter lock.
- Toggle lever `manual_enable` ON to allow manual dial mode (`master` state `7`).
- Toggle lever `manual_enable` OFF to block manual dial writes.
- Turn dial `dial_h`: manually set dish horizontal angle when discover is idle.
- Turn dial `dial_v`: manually set dish vertical angle when discover is idle.
- Empty contact slots use sentinel `-1` only (no legacy `0` empty slots).
- Optional display worker mirrors dish `Horizontal` and `Vertical` to LEDs.
- Optional status LED worker writes `display_status` color + master status code.

Status LED colors (`display_status`):

- Blue = discover/scanning
- Green = ready/contacts available
- Red = controls/setup issue
- White = init/manual/clear
- Purple = unclassified state

## Setup guard status (`db Setting`)

- `1` setup valid
- `90` missing/wrong `controls_worker` housing
- `91` missing/wrong `cmd_token`
- `92` missing/wrong `cmd_type`
- `93` missing/wrong `discover_worker` housing
- `94` discover control wrong type/name
- `95` clear control (`cycle`) wrong type/name
- `97` missing/wrong `dish` device
- `98` missing/wrong `slot0/slot1/slot2` memory
- `99` missing/wrong `manual_enable` lever or dial controls
