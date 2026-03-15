# AutolatheVendStock setup

Use this page to set up a simple fully automatic **Autolathe -> Vending Machine** stocker.

## Build list

- 5x IC Housing + IC Chip
  - AutolatheVendStock Master
  - AutolatheVendStock Stock Worker
  - AutolatheVendStock Machine Worker
  - AutolatheVendStock Logistics Worker
  - AutolatheVendStock Setup Guard
- 4x Logic Memory
  - `cmd_token`
  - `cmd_type`
  - `slot0`
  - `slot1`
- 1x Autolathe
- 1x Vending Machine
  - finished-goods stock vending
- 1x Vending Machine
  - ingot-supply vending
- 1x Sorter

## Name contract

Set these exact names (case-sensitive):

- IC Housing: `master`
- IC Housing: `stock_worker`
- IC Housing: `machine_worker`
- IC Housing: `logistics_worker`
- IC Housing: `setup_guard`
- Logic Memory: `cmd_token`
- Logic Memory: `cmd_type`
- Logic Memory: `slot0`
- Logic Memory: `slot1`

Internal prefab tokens used by the name-based scripts:

- `StructureLogicMemory`

## Wiring map

### autolathe_vend_stock_master.ic10

- no local `d0..d5` wiring required

### autolathe_vend_stock_worker_stock.ic10

- `d0` -> finished-goods vending machine

### autolathe_vend_stock_worker_machine.ic10

- `d0` -> Autolathe

### autolathe_vend_stock_worker_logistics.ic10

- `d0` -> Sorter
- `d1` -> ingot-supply vending machine
- `d2` -> Autolathe

### autolathe_vend_stock_setup_guard.ic10

- `d0` -> Autolathe

## Setup steps

- Put all five chips, the four Logic Memories, the Autolathe, both vending machines, and the sorter on one data network.
- Paste scripts:
  - `modular scripts/AutolatheVendStock/autolathe_vend_stock_master.ic10`
  - `modular scripts/AutolatheVendStock/autolathe_vend_stock_worker_stock.ic10`
  - `modular scripts/AutolatheVendStock/autolathe_vend_stock_worker_machine.ic10`
  - `modular scripts/AutolatheVendStock/autolathe_vend_stock_worker_logistics.ic10`
  - `modular scripts/AutolatheVendStock/autolathe_vend_stock_setup_guard.ic10`
- Apply required names from **Name contract**.
- Wire the stock worker, machine worker, logistics worker, and setup guard exactly as shown in **Wiring map**.
- Connect the ingot-supply vending machine export through the sorter into the Autolathe input path.
- Connect the Autolathe output into the finished-goods vending machine input path.
- Wait until `setup_guard` shows `1`.
- Leave the system running; it will start filling missing stock automatically.

## Controls

There are no buttons or dials in normal use.

The script family is fully automatic:

- the stock worker notices a missing tracked product in the finished-goods vending machine
- the machine worker builds one replacement item
- the logistics worker keeps the Autolathe fed from the ingot-supply vending machine

## Runtime debug snapshot (required for issue reports)

When debugging, capture these values in one screenshot/note:

- `master` (`db Setting`)
- `stock_worker` (`db Setting`)
- `machine_worker` (`db Setting`)
- `logistics_worker` (`db Setting`)
- `setup_guard` (`db Setting`)
- `cmd_token`, `cmd_type`, `slot0`, `slot1`

Quick interpretation:

- if setup guard is not `1`, fix names and local `d0..d2` mappings first
- if stock worker shows a large non-status value, that is the missing product hash currently being restocked
- if machine worker stays at `122`, the Autolathe usually needs more materials or power
- if logistics worker shows a large non-status value, that is the ingot hash currently being requested
