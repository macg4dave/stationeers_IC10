# Autolathe batch runner setup

Use this page to set up a simple modular Autolathe test rig with one start button.

## Build list

- 4x IC Housing + IC Chip
  - Autolathe Batch Master
  - Autolathe Batch Worker
  - Autolathe Batch Logistics Worker
  - Autolathe Batch Setup Guard
- 1x IC Housing + IC Chip (optional)
  - Autolathe Batch Hall Gate Worker
- 4x Logic Memory
  - `cmd_token`
  - `cmd_type`
  - `slot0`
  - `slot1`
- 1x Logic Memory (optional)
  - `cell_index`
- 1x Logic Switch (Button)
  - start button
- 1x Logic Switch (Button)
  - retry ingot button
- 1x Sorter
- 1x Vending Machine
- 1x Autolathe

## Name contract

Set these exact names (case-sensitive):

- IC Housing: `master`
- IC Housing: `machine_worker`
- IC Housing: `logistics_worker`
- IC Housing: `hall_gate` (optional, PrinterHall integration)
- IC Housing: `setup_guard`
- Logic Memory: `cmd_token`
- Logic Memory: `cmd_type`
- Logic Memory: `slot0`
- Logic Memory: `slot1`
- Logic Memory: `cell_index` (optional, PrinterHall integration)
- Logic Memory: `hall_cmd_token` (optional, from PrinterHall)
- Logic Memory: `hall_cmd_type` (optional, from PrinterHall)
- Logic Memory: `hall_slot0` (optional, from PrinterHall)
- Logic Memory: `hall_slot1` (optional, from PrinterHall)
- Logic Switch (Button): `start_batch`
- Logic Switch (Button): `retry_ingot`
- Sorter: `sorter_1`
- Vending Machine: `vend_ingots`
- Autolathe: `autolathe_1`

Internal prefab tokens used by the optional hall-gate script:

- `StructureLogicMemory`

## Wiring map

### autolathe_batch_master.ic10

- `d0` -> worker housing
- `d1` -> `cmd_token`
- `d2` -> `cmd_type`
- `d3` -> `slot0`
- `d4` -> `slot1`
- `d5` -> start button

### autolathe_batch_worker_machine.ic10

- `d0` -> `cmd_token`
- `d1` -> `cmd_type`
- `d2` -> `slot0`
- `d3` -> `slot1`
- `d4` -> Autolathe

### autolathe_batch_setup_guard.ic10

- `d0` -> worker housing
- `d1` -> `cmd_token`
- `d2` -> `cmd_type`
- `d3` -> `slot0`
- `d4` -> `slot1`
- `d5` -> Autolathe

### autolathe_batch_worker_logistics.ic10

- `d0` -> Sorter
- `d1` -> Vending Machine
- `d2` -> retry ingot button
- `d3` -> Autolathe

### autolathe_batch_worker_hall_gate.ic10 (optional)

- `d0` -> `cell_index`
- `d1` -> batch master housing
- `d2` -> machine worker housing
- `d3` -> logistics worker housing

## Setup steps

- Put all four chips, both buttons, the sorter, the vending machine, the Autolathe, and the four Logic Memories on one data network.
- Paste scripts:
  - `modular scripts/AutolatheBatch/autolathe_batch_master.ic10`
  - `modular scripts/AutolatheBatch/autolathe_batch_worker_machine.ic10`
  - `modular scripts/AutolatheBatch/autolathe_batch_worker_logistics.ic10`
  - `modular scripts/AutolatheBatch/autolathe_batch_setup_guard.ic10`
- Apply required names from **Name contract**.
- Wire each chip exactly as shown in **Wiring map**.
- Connect Sorter output `1` to the Autolathe input path and output `0` to your reject/return path.
- Load the Vending Machine with iron ingots for the first test.
- Wait until setup guard shows `1`.
- Set `slot0` to a valid recipe hash and `slot1` to a small count.
- Press the start button once.

Optional PrinterHall integration:

- Put a `PrinterHall` feature on the same data network.
- Set `cell_index` to `1`, `2`, or `3` to match this cell's printer lane.
- Paste `modular scripts/AutolatheBatch/autolathe_batch_worker_hall_gate.ic10`.
- Wire the hall gate as shown above.
- Use `PrinterHall` to select which cell is active; only the selected cell's local chips stay enabled.
- Press `PrinterHall`'s `run_batch` button to start the selected cell automatically.

Recommended first test:

- `slot0 = -487378546` (`Iron Sheets`)
- `slot1 = 3`

## Controls

- Start button: starts one run when the worker is idle.
- Retry ingot button: clears the current pending material request.
- `slot0`: product/recipe hash for the Autolathe.
- `slot1`: target export count for the run.
- `cell_index`: optional hall slot number when integrating with `PrinterHall`.

## Runtime debug snapshot (required for issue reports)

When debugging, capture these values in one screenshot/note:

- `master` (`db Setting`)
- `setup_guard` (`db Setting`)
- `machine_worker` (`db Setting`)
- `logistics_worker` (`db Setting`)
- `hall_gate` (`db Setting`, if used)
- `cmd_token` and `cmd_type`
- `slot0` and `slot1`

Quick interpretation:

- if `cmd_token` increments when the button is pressed, master/input path is working
- if worker stays at `122`, the Autolathe usually needs power or materials
- if `logistics_worker` shows a large non-status value, that is the ingot hash it is requesting
- if `hall_gate` is `261`, another hall printer is selected and this cell is intentionally gated off
- if setup guard is not `1`, fix mappings before debugging the worker
