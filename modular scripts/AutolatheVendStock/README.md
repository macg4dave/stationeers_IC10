# AutolatheVendStock (modular)

A simplified modular **single-Autolathe vending stocker**.

Goal: keep one finished-goods **Vending Machine** stocked with one occupied stack of each
currently hash-backed Autolathe recipe item, using one **Autolathe**, one ingot-supply
**Vending Machine**, and one **Sorter**.

Player setup guide: `modular scripts/AutolatheVendStock/Setup.md`.

## Why this exists

This merges the useful parts of `PrinterHall` and `AutolatheBatch` into one smaller,
fully automatic feature:

- no buttons
- no hall selection
- no per-cell gating
- one shared finished-goods vending target
- one local Autolathe that auto-restocks missing products

## Architecture

- `autolathe_vend_stock_master.ic10` - ensures workers stay enabled and publishes simple summary status
- `autolathe_vend_stock_worker_stock.ic10` - scans the finished-goods vending machine and requests missing products
- `autolathe_vend_stock_worker_machine.ic10` - runs the Autolathe for the requested recipe/count
- `autolathe_vend_stock_worker_logistics.ic10` - keeps Autolathe reagents topped up from an ingot vending machine
- `autolathe_vend_stock_setup_guard.ic10` - validates named shared memories / workers and initializes memory state once

## Device mapping per chip

### Master

- no local `d0..d5` wiring required
- `db` = master status

### Stock worker

- `d0` = finished-goods vending machine
- `db` = stock worker status / current missing product hash

### Machine worker

- `d0` = Autolathe
- `db` = machine worker status

### Logistics worker

- `d0` = Sorter
- `d1` = ingot-supply vending machine
- `d2` = Autolathe
- `db` = logistics status / current ingot request

### Setup guard

- `d0` = Autolathe
- `db` = setup status

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

## Shared memory contract

- `cmd_token` - incrementing command token
- `cmd_type` - command code
- `slot0` - current recipe hash request
- `slot1` - current batch count request

Command codes:

- `1` = start one Autolathe run using `slot0` / `slot1`

## Automatic stock behavior

The stock worker currently tracks the **23 Autolathe recipes with usable item hashes** in the
local catalog and tries to keep **one occupied vending stack** for each of them.

When one tracked item is missing from the finished-goods vending machine:

1. stock worker writes the product hash to `slot0`
2. stock worker writes `1` to `slot1`
3. stock worker emits command `1`
4. machine worker builds one item
5. finished goods should be routed into the vending machine
6. stock worker advances to the next tracked product only after it sees that stack exist

## Status protocol (`db Setting`)

### Master (`0-99`)

- `0` = boot
- `1` = healthy / stocked / idle
- `2` = machine worker busy producing
- `3` = stock worker is chasing a missing product or logistics is still restocking
- `43` = missing `stock_worker`
- `44` = missing `machine_worker`
- `45` = missing `logistics_worker`

### Machine worker (`100-199`)

- `100` = idle
- `110` = accepted new run
- `120` = configuring Autolathe
- `121` = start pulse written
- `122` = waiting for more exports
- `140` = batch complete
- `142` = invalid request
- `144` = missing Autolathe on `d0`

### Logistics worker (`200-299`)

- `200` = idle / no ingot request active
- `240` = missing Sorter on `d0`
- `241` = missing ingot vending machine on `d1`
- `243` = missing Autolathe on `d2`
- any other value = current ingot hash being requested

### Stock worker (`500-599`)

- `500` = scanning / currently stocked item found
- `540` = missing finished-goods vending machine on `d0`
- any other value = current missing product hash being restocked

### Setup guard (`90-99`)

- `0` = boot
- `1` = setup valid
- `91` = missing `cmd_token`
- `92` = missing `cmd_type`
- `93` = missing worker housing
- `97` = missing Autolathe on `d0`
- `98` = missing `slot0` / `slot1`

## Limits

- The current local recipe catalog only exposes **23 usable item hashes** for Autolathe products.
- This feature therefore cannot yet stock every wiki-listed Autolathe recipe automatically.
- It targets **one occupied vending stack**, not a guaranteed full max-size stack.

## Recovery steps

- If setup guard is not `1`, fix names and local `d0` wiring first.
- If stock worker shows a large non-status value, that is the product hash currently being restocked.
- If machine worker stays at `122`, the Autolathe usually needs more materials or power.
- If logistics worker shows a large non-status value, that is the ingot hash it is waiting for.
- If the vending machine fills with partial stacks, manually consolidate or clear stock; vending machines do not merge stacks internally.
