# SatCom setup (name auto-naming)

Use exact names and one shared data network. SatCom scripts now target devices
by prefab+name (`lbn`/`sbn`) and do not require per-chip `d0..d5` mapping.

## Build list

- 5x IC Housing + IC Chip
  - SatCom Master
  - SatCom Controls Worker
  - SatCom Discover Worker
  - SatCom Cycle Worker
  - SatCom Setup Guard (recommended)
- 1x IC Housing + IC Chip (optional)
  - SatCom Display Worker
- 1x IC Housing + IC Chip (optional)
  - SatCom Status LED Worker
- 6x Logic Memory
  - `cmd_token`
  - `cmd_type`
  - `slot0`
  - `slot1`
  - `slot2`
  - `filter_status` (optional, cycle verification mirror)
- 2x Logic Switch (Button)
  - Discover
  - Cycle
- 2x Logic Switch (Dial)
  - Horizontal (`dial_h`)
  - Vertical (`dial_v`)
- 1x Large Satellite Dish
- 3x LED Display (optional)
  - Horizontal (`display_h`)
  - Vertical (`display_v`)
  - Status (`display_status`)

## Name contract

Set these exact names (case-sensitive):

- Button: `discover`
- Button: `cycle`
- Dial: `dial_h`
- Dial: `dial_v`
- IC Housing: `master`
- IC Housing: `controls_worker`
- IC Housing: `setup_guard` (recommended)
- IC Housing: `discover_worker`
- IC Housing: `cycle_worker`
- IC Housing: `display_worker` (optional)
- IC Housing: `status_led_worker` (optional)
- Logic Memory: `slot0`
- Logic Memory: `slot1`
- Logic Memory: `slot2`
- Logic Memory: `cmd_token`
- Logic Memory: `cmd_type`
- Logic Memory: `filter_status` (optional)
- Large Satellite Dish: `dish`
- LED Display: `display_h` (optional)
- LED Display: `display_v` (optional)
- LED Display: `display_status` (optional)

Prefab tokens used by scripts:

- `StructureLogicMemory`
- `StructureLargeSatelliteDish`
- `StructureConsoleLED5`
- `StructureConsoleLED1x2`
- `StructureConsoleLED1x3`

## Setup steps

- Put all devices on one data network.
- Paste scripts:
  - `modular scripts/SatCom/satcom_master.ic10`
  - `modular scripts/SatCom/satcom_worker_controls.ic10`
  - `modular scripts/SatCom/satcom_worker_discover.ic10`
  - `modular scripts/SatCom/satcom_worker_cycle.ic10`
  - `modular scripts/SatCom/satcom_setup_guard.ic10` (recommended)
  - `modular scripts/SatCom/satcom_worker_display.ic10` (optional)
  - `modular scripts/SatCom/satcom_worker_status_led.ic10` (optional)
- Apply exact names from **Name contract**.
- Ensure all SatCom IC housings are the same housing prefab variant.
- Controls worker initializes dial ranges at startup:
  - `dial_h` `Mode=359` (0..359 deg)
  - `dial_v` `Mode=89` (0..89 deg)
- Power devices and wait a few ticks.
- Press Discover, then press Cycle.

## Controls

- Press Discover: scan until at least 2 new contacts, then auto-tune the first.
- Press Cycle: blacklist current stored contact (`slotN=-1`) and tune next valid.
- Press both buttons: clear stored contacts and clear dish filter lock.
- Turn dial `dial_h`: manually set dish horizontal angle when discover is idle.
- Turn dial `dial_v`: manually set dish vertical angle when discover is idle.
- Contact filter changes are handled by cycle worker commands only.
- If present, Logic Memory `filter_status` mirrors cycle filter result codes.
- Empty contact slots use sentinel `-1` only (no legacy `0` empty slots).

Cycle verification status hints:

- `220` tune write verified
- `223` tune write mismatch
- `230` clear write verified
- `233` clear write mismatch
- Optional display worker mirrors dish `Horizontal` and `Vertical` to LEDs.
- Optional status LED worker writes `display_status` color + master status code.

Status LED colors (`display_status`):

- Blue = discover/scanning
- Orange = cycle/tuning
- Green = ready/contacts available
- Yellow = no contacts found
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
- `95` cycle control wrong type/name
- `96` missing/wrong `cycle_worker` housing
- `97` missing/wrong `dish` device
- `98` missing/wrong `slot0/slot1/slot2` memory
- `99` missing/wrong `dial_h`/`dial_v` dial controls
