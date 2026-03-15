# Autolathe / printer automation checklist

Use this when designing a multi-device production line around an **Autolathe** or other
printer-style machines.

This note distills useful patterns seen in public Stationeers automation examples and
matches them against the current device/catalog knowledge in this repo.

## A practical architecture that scales

A useful split is:

- **finished-goods vending machine**
  - tracks stock of output items
  - requests replenishment when stock falls below a minimum
- **BOM / recipe worker**
  - receives a requested product hash
  - decides whether that machine can build it
  - derives the required ingot/material hashes and quantities
- **machine worker**
  - owns one printer/autolathe and its local sorter/stacker
  - loads materials, runs production, and flushes leftovers
- **raw-material vending machine**
  - stores ingots/materials and fulfills material requests
- **optional request splitter**
  - fans a single product request out to several BOM/machine workers
  - first capable worker answers, others remain idle

For this repo, that pattern would fit best as a **modular feature** under
`modular scripts/` rather than a single monolithic chip.

## Useful device variables

### Autolathe / printer-side

Commonly useful fields:

- `RecipeHash` — select what to build
- `Activate` — begin/continue production
- `On` — enable the machine
- `Open` — useful for purge / emptying behavior in some machine flows
- `ImportCount` / `ExportCount` — good for detecting movement without slot polling

Useful reagent-specific reads seen in printer logistics scripts:

- `Contents[reagent]` — current amount of a given printer material already inside
- `Required[reagent]` — missing amount for the currently selected recipe

Practical use:

- use `Contents` with floor thresholds for common base materials such as iron/copper/silicon
- use `Required` to detect recipe-specific alloy or rarer material demand

### Vending Machine

Useful fields/patterns:

- `RequestHash` — request a specific item hash for output
- slots `2..101` — storage slots you can scan to total stock by item hash
- `Quantity` per slot must be summed manually because vending machines keep split stacks

### Sorter / Stacker

- Sorter:
  - `Mode = 2` for IC-controlled lane routing
  - `Output` chooses the next lane in logic mode
  - `ImportCount` is handy for edge-detecting item arrival
- Stacker:
  - `Mode = 1` for hold/manual release flows
  - `Setting` controls target stack size
  - `ImportCount` can confirm produced-item movement

Operator-friendly trick from public scripts:

- reuse **Stacker `Setting`** as an in-world editable batch-count input
  - players can change batch size without touching IC source
  - the script can stop when printer `ExportCount >= stacker.Setting`

## A solid machine cycle

One workable per-machine flow is:

1. **Idle / empty**
   - clear or reset the active recipe
   - keep sorter bypass/reject behavior safe
2. **Load recipe**
   - set `On = 1`
   - set `RecipeHash`
   - keep purge/emptying disabled while loading materials
3. **Load materials**
   - local sorter accepts only the currently requested ingot/material hash
   - any unexpected item is rejected back to storage
4. **Produce batch**
   - trigger `Activate`
   - count produced items using a downstream stacker or movement counters
5. **Flush leftovers**
   - temporarily enable machine empty/purge behavior
   - send unused ingots/materials back to the raw-material vending machine

## Stock-control ideas worth keeping

- Keep a **minimum stock threshold** per output item.
- When stock drops below the threshold, request a **fixed production batch**.
- A public example uses a batch of **10 items**; that seems like a good tunable default,
  not a hard rule.
- Because vending machines do not merge partial stacks internally, a low stack count can
  still hide poor storage efficiency. Summing quantities is necessary, but slot pressure
  is still worth watching.

Another useful single-machine pattern:

- keep one `current_ingot_request` sentinel value (example: `-1` = no request active)
- only request one ingot type at a time from the shared vending machine
- local sorter accepts only that ingot hash and rejects everything else
- once printer `ImportCount` increments, clear the pending request and re-evaluate needs

## Request-channel conventions

If you use Logic Memories as request channels, define the meaning of each value up front.
A workable convention from public examples is:

- `0` = idle / done / confirmed
- `-1` = unavailable or waiting on upstream fulfillment
- `-2` = unable to continue (example: missing materials)
- `> 0` or item-hash value = active request

The exact numbers are less important than documenting them clearly in the feature README.

## BOM lookup pattern

A compact pattern is to store a lookup table of:

- product hash
- required material hashes
- required quantities

This can live in:

- a hard-coded table in the chip
- a stack-based lookup structure
- or, for a more maintainable repo design, documented data tables plus generated IC10

Hard-coded tables are efficient but opaque, so if you go that route, keep the setup docs
and status table in sync.

## Good fits for this repo

Useful follow-up work here would be:

- a modular `printer_supply_chain/` feature under `modular scripts/`
- a small player-facing single-machine `autolathe_batch_producer/` script under `scripts/`
- producer recipe expansion beyond `Autolathe` in `catalog/recipes/`

Useful intermediate step before a full supply chain:

- add a **logistics worker** to `AutolatheBatch` that owns an optional sorter + vending + retry button
- let multiple machine workers share one vending machine by serializing ingot requests through shared memory

## Gotchas

- Sorter logic routing wants **`Mode = 2`**, not split/filter mode.
- Vending machines store **split stacks** separately; totals and slot usage are different problems.
- If you rely on machine purge/empty behavior via `Open`, test it in-game for that exact machine type before shipping the script.
- If you use memory channels for requests, document who owns each channel and who is allowed to clear it.
- A nice debug pattern is publishing the currently requested ingot hash to `db Setting`; that gives an immediate "what is it waiting for?" readout in-game.
