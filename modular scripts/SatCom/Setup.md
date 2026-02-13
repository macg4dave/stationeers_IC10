# SatCom setup (player checklist)

Use this page to get SatCom working in game. You do not need to read script
logic to follow it.

## Build list

- 3x IC Housing + IC Chip
  - SatCom Master
  - SatCom Discover Worker
  - SatCom Cycle Worker
- 5x Logic Memory
  - `cmd_token`
  - `cmd_type`
  - `slot0`
  - `slot1`
  - `slot2`
- 2x Logic Switch (Important Button)
  - Discover
  - Cycle
- 1x Large Satellite Dish

## Setup steps

1. Put all devices on the same data network.
2. Paste scripts into the correct chips:
   - `modular scripts/SatCom/satcom_master.ic10`
   - `modular scripts/SatCom/satcom_worker_discover.ic10`
   - `modular scripts/SatCom/satcom_worker_cycle.ic10`
3. Wire each chip exactly as shown below.
4. Power everything and wait a few ticks.
5. Run a Discover, then use Cycle to move through contacts.

## Wiring map

Wire shared links first (`d0`, `d1`, `d2`...), then buttons and the dish.

### Master chip (`satcom_master.ic10`)

- `d0` = Discover worker IC Housing
- `d1` = Cycle worker IC Housing
- `d2` = Logic Memory `cmd_token`
- `d3` = Logic Memory `cmd_type`
- `d4` = Important Button (Discover)
- `d5` = Important Button (Cycle)

### Discover worker (`satcom_worker_discover.ic10`)

- `d0` = Logic Memory `slot0`
- `d1` = Logic Memory `slot1`
- `d2` = Logic Memory `slot2`
- `d3` = Logic Memory `cmd_token`
- `d4` = Logic Memory `cmd_type`
- `d5` = Large Satellite Dish

### Cycle worker (`satcom_worker_cycle.ic10`)

- `d0` = Logic Memory `slot0`
- `d1` = Logic Memory `slot1`
- `d2` = Logic Memory `slot2`
- `d3` = Logic Memory `cmd_token`
- `d4` = Logic Memory `cmd_type`
- `d5` = Large Satellite Dish

## Controls

- Press Discover: scan and store up to 3 contacts.
- Press Cycle: tune to the next stored contact.
- Press both buttons: clear stored contacts and clear dish filter.
