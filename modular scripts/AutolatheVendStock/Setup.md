# AutolatheVendStock setup

Use this page to set up a simple fully automatic **Autolathe -> Vending Machine** stocker.

## Build list

- 6x IC Housing + IC Chip
  - AutolatheVendStock Master
  - AutolatheVendStock Stock Worker
  - AutolatheVendStock Machine Worker
  - AutolatheVendStock Logistics Worker
  - AutolatheVendStock Logistics Feeder Worker
  - AutolatheVendStock Setup Guard
- 4x Logic Memory
  - `cmd_token`
  - `cmd_type`
  - `slot0`
  - `slot1`
- 1x Autolathe
- 1x Stacker
- 1x Vending Machine
  - finished-goods stock vending (`vend stock` role)
- 1x Vending Machine
  - ingot-supply vending (`vend ingot` role)
- 1x Sorter

## Name contract

Set these exact names (case-sensitive):

- IC Housing: `master`
- IC Housing: `stock_worker`
- IC Housing: `machine_worker`
- IC Housing: `logistics_worker`
- IC Housing: `logistics_feeder_worker`
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

- `d0` -> finished-goods vending machine (`vend stock` role)

### autolathe_vend_stock_worker_machine.ic10

- `d0` -> Autolathe
- `d1` -> downstream Stacker

### autolathe_vend_stock_worker_logistics.ic10

- `d2` -> Autolathe

### autolathe_vend_stock_worker_logistics_feeder.ic10

- `d0` -> Sorter
- `d1` -> ingot-supply vending machine (`vend ingot` role)

Sorter lane note:

- requested ingots go to sorter `Output = 1`
- rejects / other items go to sorter `Output = 0`
- when facing the sorter outputs with the power switch on your right:
  - `Output = 0` exits **right**
  - `Output = 1` exits **left**

### autolathe_vend_stock_setup_guard.ic10

- `d0` -> Autolathe

## Setup steps

- Put all five chips, the four Logic Memories, the Autolathe, the Stacker, both vending machines, and the sorter on one data network.
- Put all six chips, the four Logic Memories, the Autolathe, the Stacker, both vending machines, and the sorter on one data network.
- Paste scripts:
  - `modular scripts/AutolatheVendStock/autolathe_vend_stock_master.ic10`
  - `modular scripts/AutolatheVendStock/autolathe_vend_stock_worker_stock.ic10`
  - `modular scripts/AutolatheVendStock/autolathe_vend_stock_worker_machine.ic10`
  - `modular scripts/AutolatheVendStock/autolathe_vend_stock_worker_logistics.ic10`
  - `modular scripts/AutolatheVendStock/autolathe_vend_stock_worker_logistics_feeder.ic10`
  - `modular scripts/AutolatheVendStock/autolathe_vend_stock_setup_guard.ic10`
- Apply required names from **Name contract**.
- Wire the stock worker, machine worker, logistics worker, and setup guard exactly as shown in **Wiring map**.
- Connect the ingot-supply vending machine export through the sorter into the Autolathe input path.
- Make sure the sorter lane to the Autolathe is the `Output = 1` lane.
- Set the downstream Stacker `Setting` to the batch size you want for each product restock run.
- Connect the Autolathe output into the Stacker input path.
- Connect the Stacker output into the finished-goods vending machine input path.
- Wait until `setup_guard` shows `1`.
- Leave the system running; it will start filling missing stock automatically.

## Controls

There are no buttons or dials in normal use.

The script family is fully automatic:

- the finished-goods vending machine (`vend stock`) is the thing being monitored for stock
- the stock worker notices a missing tracked product there and requests it
- the machine worker builds until the downstream Stacker exports one full batch
- the downstream Stacker `Setting` is the per-item batch size
- the ingot-supply vending machine (`vend ingot`) only keeps the Autolathe fed,
  refilling any tracked reagent that drops below `50` back toward `200`

At the moment, "stock satisfied" means the stock worker sees at least one occupied vending stack for the
tracked item. Exact per-item quantity targets are not implemented yet.

## Runtime debug snapshot (required for issue reports)

When debugging, capture these values in one screenshot/note:

- `master` (`db Setting`)
- `stock_worker` (`db Setting`)
- `machine_worker` (`db Setting`)
- `logistics_worker` (`db Setting`)
- `logistics_feeder_worker` (`db Setting`)
- `setup_guard` (`db Setting`)
- `cmd_token`, `cmd_type`, `slot0`, `slot1`
- downstream Stacker: `Setting`, `ImportCount`, `ExportCount`, `Mode`, `On`

Quick interpretation:

- if setup guard is not `1`, fix names and local `d0..d2` mappings first
- if stock worker shows a large non-status value, that is the missing product hash currently being restocked
- if machine worker stays at `122`, the Autolathe usually needs more materials or power
- if machine worker stays at `123`, the Stacker is usually still holding the batch or the output path is blocked
- if logistics worker shows a large non-status value, that is the ingot hash currently being requested
- if logistics_feeder_worker shows a large non-status value, that is the ingot hash currently being routed to the Autolathe
