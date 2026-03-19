# AutolatheVendStock setup

Use this page to set up a simple fully automatic **Autolathe -> Vending Machine** stocker.

## Build list

- 7x IC Housing + IC Chip
  - AutolatheVendStock Master
  - AutolatheVendStock Stock Worker
  - AutolatheVendStock Machine Prep Worker
  - AutolatheVendStock Machine Worker
  - AutolatheVendStock Logistics Worker
  - AutolatheVendStock Logistics Feeder Worker
  - AutolatheVendStock Setup Guard
- 7x Logic Memory
  - `cmd_token`
  - `cmd_type`
  - `slot0`
  - `slot1`
  - `slot2`
  - `slot3`
  - `slot4`
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
- IC Housing: `machine_prep_worker`
- IC Housing: `machine_worker`
- IC Housing: `logistics_worker`
- IC Housing: `logistics_feeder_worker`
- IC Housing: `setup_guard`
- Logic Memory: `cmd_token`
- Logic Memory: `cmd_type`
- Logic Memory: `slot0`
- Logic Memory: `slot1`
- Logic Memory: `slot2`
- Logic Memory: `slot3`
- Logic Memory: `slot4`

Internal prefab tokens used by the name-based scripts:

- `StructureLogicMemory`

Unused device pins are intentionally labelled in-game as `n0..n5` so stale old pin names are easier to spot after script updates.

## Wiring map

### autolathe_vend_stock_master.ic10

- no local `d0..d5` wiring required

### autolathe_vend_stock_worker_stock.ic10

- `d0` -> finished-goods vending machine (`vend stock` role)

### autolathe_vend_stock_worker_machine.ic10

- `d0` -> Autolathe
- `d1` -> downstream Stacker

### autolathe_vend_stock_worker_machine_prep.ic10

- `d0` -> Autolathe

### autolathe_vend_stock_worker_logistics.ic10

- `d2` -> Autolathe

### autolathe_vend_stock_worker_logistics_feeder.ic10

- `d0` -> Sorter (`feed_sort` in-game pin label)
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

- Put all seven chips, the seven Logic Memories, the Autolathe, the Stacker, both vending machines, and the sorter on one data network.
- Paste scripts:
  - `modular scripts/AutolatheVendStock/autolathe_vend_stock_master.ic10`
  - `modular scripts/AutolatheVendStock/autolathe_vend_stock_worker_stock.ic10`
  - `modular scripts/AutolatheVendStock/autolathe_vend_stock_worker_machine_prep.ic10`
  - `modular scripts/AutolatheVendStock/autolathe_vend_stock_worker_machine.ic10`
  - `modular scripts/AutolatheVendStock/autolathe_vend_stock_worker_logistics.ic10`
  - `modular scripts/AutolatheVendStock/autolathe_vend_stock_worker_logistics_feeder.ic10`
  - `modular scripts/AutolatheVendStock/autolathe_vend_stock_setup_guard.ic10`
- Apply required names from **Name contract**.
- Wire the stock worker, machine prep worker, machine worker, logistics worker, and setup guard exactly as shown in **Wiring map**.
- Leave `slot2`, `slot3`, and `slot4` on the shared data network; `slot2` carries raw ingot requests, `slot3` carries Autolathe-ready state, and `slot4` tells the rest of the module when a machine run is active.
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
- recipe-specific alloy ingots such as `INGOT_STELLITE` are only requested while the active Autolathe recipe still reports that reagent as missing

At the moment, "stock satisfied" means the stock worker sees at least one occupied vending stack for the
tracked item. Exact per-item quantity targets are not implemented yet.

## Runtime debug snapshot (required for issue reports)

When debugging, capture these values in one screenshot/note:

- `master` (`db Setting`)
- `stock_worker` (`db Setting`)
- `machine_prep_worker` (`db Setting`)
- `machine_worker` (`db Setting`)
- `logistics_worker` (`db Setting`)
- `logistics_feeder_worker` (`db Setting`)
- `setup_guard` (`db Setting`)
- `cmd_token`, `cmd_type`, `slot0`, `slot1`
- `slot2`, `slot3`, `slot4`
- downstream Stacker: `Setting`, `ImportCount`, `ExportCount`, `Mode`, `On`

Quick interpretation:

- if setup guard is not `1`, fix names and local `d0..d2` mappings first
- if stock worker shows a large non-status value, that is the missing product hash currently being restocked
- if `machine_prep_worker` stays at `151`..`154`, the Autolathe is still being prepared for the requested recipe
- if machine worker stays at `122`, the Autolathe usually needs more materials or power
- if machine worker stays at `123`, the Stacker is usually still holding the batch or the output path is blocked
- if logistics worker shows a large non-status value, that is the ingot hash currently being requested
- if logistics_feeder_worker shows a large non-status value, that is the ingot hash currently being routed to the Autolathe
- if `slot2`, `logistics_worker`, and `logistics_feeder_worker` all stay pinned to the same alloy ingot hash, check the logistics script for a reagent-vs-item-hash mix-up in `Required[...]`
- verified example: `Stellite` uses reagent hash `-500544800`, while `Ingot (Stellite)` uses item hash `-1897868623`
- if `stock_worker` stays pinned on cable, verify the script is using the current cable item hash
  `2060134443` (`ItemCableCoilHeavy`) from `catalog/recipes/Autolathe/recipes.json`
