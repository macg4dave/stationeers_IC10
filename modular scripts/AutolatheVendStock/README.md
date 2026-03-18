# AutolatheVendStock (modular)

A simplified modular **single-Autolathe vending stocker**.

Goal: keep one finished-goods **Vending Machine** stocked with one occupied stack of each
currently hash-backed Autolathe recipe item, using one **Autolathe**, one ingot-supply
**Vending Machine**, one downstream **Stacker**, and one **Sorter**.

Player setup guide: `modular scripts/AutolatheVendStock/Setup.md`.

## Why this exists

This merges the useful parts of `PrinterHall` and `AutolatheBatch` into one smaller,
fully automatic feature:

- no buttons
- no hall selection
- no per-cell gating
- one shared finished-goods vending target (`vend stock` role)
- one ingot-supply vending machine that only keeps the Autolathe topped up (`vend ingot` role)
- one local Autolathe that auto-restocks missing products

## Architecture

- `autolathe_vend_stock_master.ic10` - ensures workers stay enabled and publishes simple summary status
- `autolathe_vend_stock_worker_stock.ic10` - scans the finished-goods vending machine and requests missing products
- `autolathe_vend_stock_worker_machine.ic10` - runs the Autolathe for the requested recipe/count
- `autolathe_vend_stock_worker_logistics.ic10` - watches Autolathe reagent levels and publishes the current ingot request
- `autolathe_vend_stock_worker_logistics_feeder.ic10` - routes the requested ingot through the sorter and keeps the ingot vending machine pulsing
- `autolathe_vend_stock_setup_guard.ic10` - validates named shared memories / workers and initializes memory state once

## Device mapping per chip

### Master

- no local `d0..d5` wiring required
- `db` = master status

### Stock worker

- `d0` = finished-goods vending machine (`vend stock` role)
- `db` = stock worker status / current missing product hash

### Machine worker

- `d0` = Autolathe
- `d1` = downstream Stacker used as the local batch counter / release gate
- `db` = machine worker status

### Logistics worker

- `d2` = Autolathe
- `db` = logistics status / current ingot request

### Logistics feeder worker

- `d0` = Sorter
- `d1` = ingot-supply vending machine (`vend ingot` role)
- `db` = feeder status / current ingot request being routed

Sorter lane note:

- requested ingots are routed to sorter `Output = 1`
- rejects / other items go to sorter `Output = 0`
- when facing the sorter outputs with the power switch on your right:
  - `Output = 0` exits **right**
  - `Output = 1` exits **left**

### Setup guard

- `d0` = Autolathe
- `db` = setup status

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
- Logic Memory: `slot2`

Internal prefab tokens used by the name-based scripts:

- `StructureLogicMemory`

## Shared memory contract

- `cmd_token` - incrementing command token
- `cmd_type` - command code
- `slot0` - current recipe hash request
- `slot1` - current batch count request
- `slot2` - current raw ingot request hash for `logistics_feeder_worker`

Command codes:

- `1` = start one Autolathe run using `slot0` / `slot1`

## Automatic stock behavior

Intended workflow:

1. the finished-goods vending machine (`vend stock`) acts as the demand signal
2. when a tracked product is missing or below its target stock level, the stock worker requests it
3. the machine worker runs the Autolathe until that stock request is satisfied
4. the ingot-supply vending machine (`vend ingot`) does **not** decide what to build; it only keeps the
   Autolathe's reagents topped up so the machine worker can continue building

The stock worker currently tracks the **23 Autolathe recipes with usable item hashes** in the
local catalog and tries to keep **one occupied vending stack** for each of them.

The split logistics path expects the ingot-supply vending machine to hold the Autolathe's feed ingots.
The request worker uses a simple hysteresis refill rule:

- if a tracked reagent drops below `50`, it becomes the active refill request
- the request worker publishes that raw ingot hash to `slot2`
- the feeder worker reads `slot2`, keeps pulsing vending requests for that ingot, and routes sorter output `1` to the Autolathe
- the request worker keeps that request active until the Autolathe reaches `200`
- then it clears that request and scans for the next low reagent

When one tracked item is missing from the finished-goods vending machine:

1. stock worker writes the product hash to `slot0`
2. stock worker writes `1` to `slot1`
3. stock worker emits command `1`
4. machine worker builds until its downstream Stacker exports one batch
5. the Stacker `Setting` controls the batch size for that product run
6. finished goods should be routed from the Stacker into the vending machine
7. stock worker advances to the next tracked product only after it sees that stack exist

Current limitation:

- the current stock worker treats "stock met" as **one occupied vending stack exists** for that item
- the machine worker uses the downstream Stacker `Setting` as its local batch size for each request
- it does **not yet** maintain an exact configurable quantity target per item
- that exact-count behavior is a sensible next upgrade, but the ingot top-up path is intentionally kept
  separate so you do not need a full recipe/build-list system just to keep the Autolathe fed

## Status protocol (`db Setting`)

### Master (`0-99`)

- `0` = boot
- `1` = healthy / stocked / idle
- `2` = machine worker busy producing
- `3` = stock worker is chasing a missing product or logistics is still restocking
- `43` = missing `stock_worker`
- `44` = missing `machine_worker`
- `45` = missing `logistics_worker`
- `46` = missing `logistics_feeder_worker`

### Machine worker (`100-199`)

- `100` = idle
- `110` = accepted new run
- `120` = configuring Autolathe
- `121` = start pulse written
- `122` = waiting for more exports
- `123` = batch built, waiting for Stacker release
- `140` = batch complete
- `142` = invalid request
- `144` = missing Autolathe on `d0`
- `145` = missing Stacker on `d1`

### Logistics worker (`200-299`)

- `200` = idle / no ingot request active
- `243` = missing Autolathe on `d2`
- any other value = current ingot hash being requested toward the `200` target

### Logistics feeder worker (`300-399`)

- `300` = idle / no ingot request active
- `340` = missing Sorter on `d0`
- `341` = missing ingot vending machine on `d1`
- `342` = missing `slot2`
- any other value = current ingot hash being routed from the ingot vending machine

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
- `98` = missing `slot0` / `slot1` / `slot2`

## Limits

- The current local recipe catalog only exposes **23 usable item hashes** for Autolathe products.
- This feature therefore cannot yet stock every wiki-listed Autolathe recipe automatically.
- It currently targets **one occupied vending stack**, with the per-run batch size coming from the downstream Stacker `Setting`.

## Recovery steps

- If setup guard is not `1`, fix names and local `d0` wiring first.
- If stock worker shows a large non-status value, that is the product hash currently being restocked.
- If machine worker stays at `122`, the Autolathe usually needs more materials or power.
- If machine worker stays at `123`, the Stacker is usually still holding the batch or the output path is blocked.
- If logistics worker shows a large non-status value, that is the ingot hash it is waiting for.
- If logistics feeder worker shows a large non-status value, that is the ingot hash it is currently trying to route into the Autolathe.
- If the vending machine fills with partial stacks, manually consolidate or clear stock; vending machines do not merge stacks internally.
