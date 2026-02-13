# SatCom setup (name auto-naming)

Use exact names and one shared data network. SatCom scripts now target devices
by prefab+name (`lbn`/`sbn`) and do not require per-chip `d0..d5` mapping.

## Build list

- 4x IC Housing + IC Chip
  - SatCom Master
  - SatCom Discover Worker
  - SatCom Cycle Worker
  - SatCom Setup Guard (recommended)
- 1x IC Housing + IC Chip (optional)
  - SatCom Display Worker
- 5x Logic Memory
  - `cmd_token`
  - `cmd_type`
  - `slot0`
  - `slot1`
  - `slot2`
- 2x Logic Switch (Button) or Important Button
  - Discover
  - Cycle
- 1x Large Satellite Dish
- 2x LED Display (optional)
  - Horizontal (`display_h`)
  - Vertical (`display_v`)

## Name contract

Set these exact names (case-sensitive):

- Button: `discover`
- Button: `cycle`
- IC Housing: `master`
- IC Housing: `setup_guard` (recommended)
- IC Housing: `discover_worker`
- IC Housing: `cycle_worker`
- IC Housing: `display_worker` (optional)
- Logic Memory: `slot0`
- Logic Memory: `slot1`
- Logic Memory: `slot2`
- Logic Memory: `cmd_token`
- Logic Memory: `cmd_type`
- Large Satellite Dish: `dish`
- LED Display: `display_h` (optional)
- LED Display: `display_v` (optional)

Prefab tokens used by scripts:

- `StructureLogicMemory`
- `StructureLargeSatelliteDish`
- `StructureConsoleLED5`
- `StructureConsoleLED1x2`
- `StructureConsoleLED1x3`

## Setup steps

1. Put all devices on one data network.
2. Paste scripts:
   - `modular scripts/SatCom/satcom_master.ic10`
   - `modular scripts/SatCom/satcom_worker_discover.ic10`
   - `modular scripts/SatCom/satcom_worker_cycle.ic10`
   - `modular scripts/SatCom/satcom_setup_guard.ic10` (recommended)
   - `modular scripts/SatCom/satcom_worker_display.ic10` (optional)
3. Apply exact names from **Name contract**.
4. Ensure all SatCom IC housings are the same housing prefab variant.
5. Power devices and wait a few ticks.
6. Press Discover, then press Cycle.

## Controls

- Press Discover: scan and store up to 3 contacts.
- Press Cycle: tune to the next stored contact.
- Press both buttons: clear stored contacts and clear dish filter.
- Optional display worker mirrors dish `Horizontal` and `Vertical` to LEDs.

## Setup guard status (`db Setting`)

- `1` setup valid
- `91` missing/wrong `cmd_token`
- `92` missing/wrong `cmd_type`
- `93` missing/wrong `discover_worker` housing
- `94` discover control wrong type/name
- `95` cycle control wrong type/name
- `96` missing/wrong `cycle_worker` housing
