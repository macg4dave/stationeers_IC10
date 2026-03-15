# PrinterHall setup

Use this page to set up a modular shared-bus **Autolathe hall** with one active
printer at a time.

## Build list

- 6x IC Housing + IC Chip
  - PrinterHall Master
  - PrinterHall Selector Worker
  - PrinterHall Logistics Worker
  - PrinterHall Overflow Worker
  - PrinterHall Idle Worker
  - PrinterHall Setup Guard
- 5x Logic Memory
  - `cmd_token`
  - `cmd_type`
  - `slot0`
  - `slot1`
  - `slot2`
- 4x Logic Switch (Button)
  - select printer 1
  - select printer 2
  - select printer 3
  - flush overflow
- 1x Logic Switch (Switch)
  - hall power
- 4x Autolathe
  - `printer_1`
  - `printer_2`
  - `printer_3`
  - `buffer_printer`
- 1x Sorter
  - shared hall feed sorter
- 1x Proximity Sensor
  - hall presence / idle timer reset

## Name contract

Set these exact names (case-sensitive):

- IC Housing: `master`
- IC Housing: `selector_worker`
- IC Housing: `logistics_worker`
- IC Housing: `overflow_worker`
- IC Housing: `idle_worker`
- IC Housing: `setup_guard`
- Logic Memory: `cmd_token`
- Logic Memory: `cmd_type`
- Logic Memory: `slot0`
- Logic Memory: `slot1`
- Logic Memory: `slot2`
- Logic Switch (Button): `select_1`
- Logic Switch (Button): `select_2`
- Logic Switch (Button): `select_3`
- Logic Switch (Button): `flush_overflow`
- Logic Switch (Switch): `hall_power`
- Autolathe: `printer_1`
- Autolathe: `printer_2`
- Autolathe: `printer_3`
- Autolathe: `buffer_printer`

Internal prefab tokens used by the name-based scripts:

- `StructureLogicMemory`
- `StructureLogicButton`
- `StructureLogicSwitch2`
- `StructureAutolathe`

## Wiring map

### printer_hall_master.ic10

- no local `d0..d5` wiring required

### printer_hall_worker_selector.ic10

- no local `d0..d5` wiring required

### printer_hall_worker_overflow.ic10

- no local `d0..d5` wiring required

### printer_hall_setup_guard.ic10

- no local `d0..d5` wiring required

### printer_hall_worker_logistics.ic10

- `d0` -> shared feed sorter

### printer_hall_worker_idle.ic10

- `d0` -> hall proximity sensor

## Setup steps

- Put all chips, memories, controls, printers, sorter, and sensor on one data network.
- Paste scripts:
  - `modular scripts/PrinterHall/printer_hall_master.ic10`
  - `modular scripts/PrinterHall/printer_hall_worker_selector.ic10`
  - `modular scripts/PrinterHall/printer_hall_worker_logistics.ic10`
  - `modular scripts/PrinterHall/printer_hall_worker_overflow.ic10`
  - `modular scripts/PrinterHall/printer_hall_worker_idle.ic10`
  - `modular scripts/PrinterHall/printer_hall_setup_guard.ic10`
- Apply required names from **Name contract**.
- Wire the logistics worker and idle worker exactly as shown in **Wiring map**.
- Connect sorter `Output 1` to the printer lane and `Output 0` to overflow / reject.
- Wait until `setup_guard` shows `1`.
- Turn `hall_power` on.
- Press one of the select buttons to choose the active printer.

## Controls

- `select_1` / `select_2` / `select_3`: choose the active printer.
- `hall_power`: enables the hall.
- `flush_overflow`: briefly opens the buffer printer and forces sorter traffic to overflow.
- `slot2`: idle timeout in loops; default `300` from setup guard.

## Runtime debug snapshot (required for issue reports)

When debugging, capture these values in one screenshot/note:

- `master` (`db Setting`)
- `selector_worker` (`db Setting`)
- `logistics_worker` (`db Setting`)
- `overflow_worker` (`db Setting`)
- `idle_worker` (`db Setting`)
- `setup_guard` (`db Setting`)
- `cmd_token`, `cmd_type`, `slot0`, `slot1`, `slot2`

Quick interpretation:

- if setup guard is not `1`, fix names before debugging logic
- if master is `11`, the hall power switch is off
- if selector is `101`, no printer is selected yet
- if logistics is `340`, its local sorter mapping is wrong or missing
- if idle is `244`, its local proximity sensor mapping is wrong or missing
