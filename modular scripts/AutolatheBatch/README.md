# Autolathe batch runner (modular)

A small modular test case for Autolathe automation.

Goal: press one button to make a single Autolathe build a configurable batch of one
recipe using recipe/count values from Logic Memory.

Player setup guide: `modular scripts/AutolatheBatch/Setup.md`.

## Architecture

- `autolathe_batch_master.ic10` - reads the start button and emits a start command
- `autolathe_batch_worker_machine.ic10` - drives one Autolathe to a target export count
- `autolathe_batch_worker_logistics.ic10` - keeps printer materials topped up via sorter + vending
- `autolathe_batch_worker_hall_gate.ic10` - optional gate that only enables this cell when `PrinterHall` selects it
- `autolathe_batch_setup_guard.ic10` - validates mappings and initializes command memories

This is intentionally small and useful as a first modular printer/autolathe test case.

## Device mapping per chip

### Master

- `d0` = worker housing
- `d1` = `cmd_token` Logic Memory
- `d2` = `cmd_type` Logic Memory
- `d3` = `slot0` Logic Memory (recipe hash)
- `d4` = `slot1` Logic Memory (target export count)
- `d5` = start button
- `db` = master status

### Worker

- `d0` = `cmd_token` Logic Memory
- `d1` = `cmd_type` Logic Memory
- `d2` = `slot0` Logic Memory (recipe hash)
- `d3` = `slot1` Logic Memory (target export count)
- `d4` = Autolathe
- `db` = worker status

### Setup guard

- `d0` = worker housing
- `d1` = `cmd_token` Logic Memory
- `d2` = `cmd_type` Logic Memory
- `d3` = `slot0` Logic Memory (recipe hash)
- `d4` = `slot1` Logic Memory (target export count)
- `d5` = Autolathe
- `db` = setup status

### Logistics worker

- `d0` = Sorter
- `d1` = Vending Machine
- `d2` = retry button
- `d3` = Autolathe
- `db` = logistics status / current ingot request

### Hall gate worker (optional)

- `d0` = `cell_index` Logic Memory (`1..3` for the hall slot this cell owns)
- `d1` = batch master housing
- `d2` = machine worker housing
- `d3` = logistics worker housing
- `db` = hall-integration status

## Shared memory contract

- `cmd_token` - incrementing command token written by master
- `cmd_type` - command code
- `slot0` - product/recipe hash to write to Autolathe `RecipeHash`
- `slot1` - target export count for this run

Command codes:

- `1` = start batch

## Controls

- Start button: rising edge starts a run if the worker is idle
- `slot0`: set the recipe hash before pressing start
- `slot1`: set the target export count before pressing start
- Retry button: clears the current ingot request so logistics can re-request material

Recommended first test:

- `slot0 = -487378546` for `Iron Sheets`
- `slot1 = 3`
- put iron ingots in the vending machine
- press the start button once

## Status protocol (`db Setting`)

### Master status (`0-99`)

- `0` = boot
- `1` = ready / idle
- `2` = worker busy
- `5` = worker completed last run
- `10` = start command sent
- `11` = invalid request in `slot0`/`slot1`
- `43` = missing worker housing mapping
- `44` = missing/wrong start button mapping
- `45` = missing shared memory mapping

### Worker status (`100-199`)

- `100` = idle
- `110` = accepted new run
- `120` = configuring machine (`RecipeHash`/`On`/`Open`)
- `121` = start pulse written to `Activate`
- `122` = waiting for more exports
- `140` = batch complete
- `142` = invalid request
- `144` = missing Autolathe mapping
- `145` = missing command/data memory mapping

### Setup guard status (`90-99`)

- `0` = boot
- `10` = shared memories initialized once
- `1` = setup valid
- `91` = missing `cmd_token`
- `92` = missing `cmd_type`
- `93` = missing worker housing mapping
- `97` = missing Autolathe mapping
- `98` = missing `slot0`/`slot1`

### Logistics worker status / debug (`db Setting`)

- `200` = idle / no active ingot request
- `240` = missing Sorter mapping
- `241` = missing Vending Machine mapping
- `242` = missing retry button mapping
- `243` = missing Autolathe mapping
- any other value = current ingot hash being requested from the vending machine

### Hall gate worker status (`250-269`, optional)

- `250` = hall power off
- `251` = hall powered, no active printer selected
- `260` = this cell is currently selected and enabled
- `261` = another hall printer is selected; this cell is gated off
- `262` = invalid `cell_index` value
- `263` = missing `cell_index` memory mapping
- `264` = missing batch master housing mapping
- `265` = missing machine worker housing mapping
- `266` = missing logistics worker housing mapping

## Notes

- This worker counts **exports**, not recipe progress. That makes it a good simple test,
  but some recipes may export stacks in ways that do not map 1:1 to "one crafted unit".
- If the Autolathe lacks materials, the worker keeps retrying instead of failing fast.
- `slot0` uses the produced item's hash as the recipe hash; this matches the common
  Stationeers pattern used by public automation examples.

Useful upgrade paths observed in public printer-logistics scripts:

- use a local sorter in `Mode = 2` to accept only the currently requested ingot hash
- use printer `Contents[reagent]` / `Required[reagent]` reads to decide what to restock
- reuse a Stacker `Setting` as a player-editable batch-count control
- expose the current ingot request through `db Setting` for faster in-game debugging

The included logistics worker now implements the first, second, and fourth of those.

## Optional PrinterHall integration

If you want a full hall where one shared bus feeds several local batch cells:

- run one `PrinterHall` feature for hall-level selection, power, overflow, and idle logic
- run one `AutolatheBatch` cell per physical printer
- add `autolathe_batch_worker_hall_gate.ic10` to each cell

The hall gate reads `PrinterHall`'s prefixed memory contract:

- `hall_slot0` = selected printer index
- `hall_slot1` = hall power flag

The local batch master also listens for:

- `hall_cmd_token`
- `hall_cmd_type = 6`

and only enables the local batch master + machine + logistics workers when:

- hall power is on
- this cell's `cell_index` matches the selected hall printer index

When the selected hall operator presses `run_batch`, the local batch master starts the
configured run automatically using this cell's own `slot0` / `slot1` values.

This keeps hall routing and local recipe/material logic separate and easier to debug.

## Recovery steps

- If setup guard is not `1`, fix mappings first.
- If master stays at `11`, check `slot0` and `slot1` values.
- If worker stays at `122`, the Autolathe is usually waiting on materials or power.
- If logistics worker shows a large non-status value, that value is the ingot hash it is waiting for.
- If hall gate is `261`, another hall printer is selected and this cell is intentionally gated off.
- To retry, press the start button again after the worker returns to `100` or `140`.
