# ingot_printer (modular)

LIFO-priority **multi-Autolathe ingot printer** for testing and using Free Ingots mod support.

Goal: watch a finished-goods **Vending Machine**, detect any supported ingot whose total stock is
below `100`, and command **all connected named Autolathes** to print the selected ingot using a
**last-low-found, first-printed** priority rule.

Player setup guide: `modular scripts/ingot_printer/Setup.md`.

Active runtime files in this module:

- `ingot_printer_master.ic10`
- `ingot_printer_worker_print.ic10`
- `ingot_printer_worker_selector.ic10`
- `ingot_printer_worker_stackers.ic10`

Deprecated helper files that are **not used** by the current compact module flow:

- `ingot_printer_worker_keep.ic10`
- `ingot_printer_worker_pick_base.ic10`
- `ingot_printer_worker_pick_alloy.ic10`

## Requirements

- **Free Ingots** mod (or another mod/config that adds the same Autolathe ingot recipes)
- 4x IC Housing + IC Chip
- 1x Logic Memory
- 1x Vending Machine
- 1x end-of-line Stacker
- 1..N per-printer Stackers named `autostd`
- 1..N Autolathes

Currently tracked ingots with verified hashes in this repo:

- `Ingot (Silicon)` = `-290196476`
- `Ingot (Iron)` = `-1301215609`
- `Ingot (Gold)` = `226410516`
- `Ingot (Copper)` = `-404336834`
- `Ingot (Silver)` = `-929742000`
- `Ingot (Lead)` = `2134647745`
- `Ingot (Nickel)` = `-1406385572`
- `Ingot (Steel)` = `-654790771`
- `Ingot (Electrum)` = `502280180`
- `Ingot (Invar)` = `-297990285`
- `Ingot (Constantan)` = `1058547521`
- `Ingot (Solder)` = `-82508479`
- `Ingot (Astroloy)` = `412924554`
- `Ingot (Hastelloy)` = `1579842814`
- `Ingot (Inconel)` = `-787796599`
- `Ingot (Waspaloy)` = `156348098`
- `Ingot (Stellite)` = `-1897868623`

## Device mapping

### `ingot_printer_master.ic10`

- `d0` = end-of-line Stacker
- `d1` = finished-goods Vending Machine
- `db` = status

### `ingot_printer_worker_print.ic10`

- `d0` = one representative Autolathe that is also named `printer`
- `db` = status / current active target hash

### `ingot_printer_worker_selector.ic10`

- `d0` = finished-goods Vending Machine
- `db` = active target hash to keep/print, else `0`

### `ingot_printer_worker_stackers.ic10`

- `d0` = one representative Stacker also named `autostd`
- `db` = stacker-worker status

### Stock workers

Each stock worker is wired the same way:

- `d0` = finished-goods Vending Machine
- `db` = `0` when stocked, or the ingot hash when that ingot total is below `100`

Unused pins are explicitly labelled `n1..n5` / `n2..n5` so the in-game housing labels stay clean after updates.

## Name contract

Set these exact names (case-sensitive):

- IC Housing: `master`
- IC Housing: `printer_worker`
- IC Housing: `selector_worker`
- IC Housing: `stacker_worker`
- Logic Memory: `slot0`
- Autolathe: `printer` (apply this exact name to **every** Autolathe the module should control)
- Stacker: `autostd` (apply this exact name to every per-printer stacker you want held at fixed stack size)

## Behavior

Master behavior:

1. forces the end-of-line Stacker to `Mode = Automatic` and `On = 1`
2. reads the current target's total inventory from the finished-goods Vending Machine on `d1`
3. keeps the Stacker `Setting` fixed at `100`, using the Stacker as a true 100-item stacker for ingots during testing
4. when the Vending total plus the current Stacker batch reaches the target, it stops the printers and flushes only the remaining Stacker contents
5. validates `selector_worker` and `slot0`
6. asks `selector_worker` for the current ingot-to-keep or next ingot-to-print after a batch edge
7. writes that active target hash to `slot0`
8. changes target only when there is no current target yet, or after a Stacker batch edge when the current ingot is no longer reported low

Worker behavior:

1. reads the active target from `slot0`
2. batch-controls all Autolathes named `printer`
3. forces `On = 1`, `Open = 0`, `RecipeHash = slot0`, and `Activate = 1`
4. idles all named printers when `slot0 = 0`

Stacker-worker behavior:

1. batch-controls all Stackers named `autostd`
2. forces `On = 1`
3. forces `Mode = Automatic`
4. forces `Setting = 10`
5. does not track item contents inside those per-printer stackers; it only keeps their fixed stacking configuration applied

Gap-avoidance behavior:

- the master does **not** switch away from the active ingot just because some other ingot is also low
- the master uses the Vending Machine as the source of truth for stored inventory and the Stacker as the live running batch counter for the active ingot
- the Stacker `Setting` stays fixed at `100`; the master never shrinks it to match the remainder
- once the Vending total plus the live Stacker batch reaches the target, the master clears `slot0` first so the printers stop before the final drain batch is exported, then uses `Activate` to flush the remaining partial stack without changing `Setting`
- after that final flush, the master waits for the Vending Machine total itself to catch up before it allows the selector to choose again; this prevents the same ingot from being reselected during the eject/transport delay
- after a Stacker batch edge, it asks `selector_worker` to prefer the current ingot if that ingot is still below target stock
- if the current ingot is still low, it stays locked on that recipe instead of hopping to the next one early

Selector-worker behavior:

- `selector_worker` scans the Vending Machine directly instead of depending on one IC per ingot
- it rescans each supported ingot, sums quantities exactly, and finds the highest-priority low ingot
- if the currently active target from `slot0` is still low, it republishes that same target instead of switching early
- otherwise it returns the best next low ingot according to the tracked-order priority

Priority behavior:

- behavior is intentionally **LIFO-like**: the later a low ingot appears in the tracked-order list, the sooner it will be selected when several ingots are low at once
- later entries in the tracked-order list below therefore get higher print priority
- tracked-order list:
  1. `Ingot (Silicon)`
  2. `Ingot (Iron)`
  3. `Ingot (Gold)`
  4. `Ingot (Copper)`
  5. `Ingot (Silver)`
  6. `Ingot (Lead)`
  7. `Ingot (Nickel)`
  8. `Ingot (Steel)`
  9. `Ingot (Electrum)`
  10. `Ingot (Invar)`
  11. `Ingot (Constantan)`
  12. `Ingot (Solder)`
  13. `Ingot (Astroloy)`
  14. `Ingot (Hastelloy)`
  15. `Ingot (Inconel)`
  16. `Ingot (Waspaloy)`
  17. `Ingot (Stellite)`

## Status protocol (`db Setting`)

### Master (`200-299` and active target hashes)

- `0` = boot
- `200` = scanning / no active target yet
- any tracked ingot hash = current active target being printed / held until its stock worker clears
- `242` = missing Stacker on `d0`
- `243` = missing finished-goods Vending Machine on `d1`
- `248` = missing `slot0`
- `249` = missing `selector_worker`

### Print worker (`100-199` and active target hashes)

- `100` = idle / no active target
- `101` = turning all named printers on
- `102` = closing `Open` on all named printers
- `103` = clearing stale `Activate` before changing recipe
- `104` = writing target `RecipeHash` to all named printers
- `105` = setting `Activate = 1` on all named printers
- any tracked ingot hash = all named printers are being driven toward that target
- `144` = missing representative Autolathe on `d0`
- `148` = missing `slot0`

### Selector worker (`600-699` and target hashes)

- `600` = boot
- `0` = no low ingot found
- any tracked ingot hash = active ingot to keep or next ingot to print
- `640` = missing Vending Machine on `d0`
- `648` = missing `slot0`

### Stacker worker (`300-399`)

- `300` = boot
- `301` = turning all named `autostd` stackers on
- `302` = setting all named `autostd` stackers to `Mode = Automatic`
- `303` = setting all named `autostd` stackers to `Setting = 10`
- `310` = all named `autostd` stackers are configured for fixed stack size `10`
- `344` = missing representative Stacker on `d0`

### Stock workers (`0`, target hash, or `540`)

- `0` = that ingot is stocked to at least `100`
- target ingot hash = that ingot is currently below `100`
- `540` = missing Vending Machine on `d0`

## Notes

- This module lives under `modular scripts/` so it can act as a more realistic test bed for opt-in mod support.
- It uses one directly wired representative Autolathe only to discover device type and local state; all real production commands are sent to every exact-name `printer` Autolathe on the data network.
- The finished-goods Vending Machine is scanned exactly by summing slot quantities, not just checking for item presence.
- The optional `stacker_worker` can batch-configure every exact-name `autostd` stacker to fixed stack size `10` so each Autolathe can pre-stack output before it enters the shared chute network.
- The master keeps the Stacker fixed at `100` and uses the live Stacker quantity only as the in-progress running count for the currently printed ingot.
- The current testing target in this module is `100` items per ingot in the finished-goods Vending Machine.
- The compact build keeps the chip count low by using one selector worker instead of one stock worker per ingot.
- `ingot_printer_worker_keep.ic10`, `ingot_printer_worker_pick_base.ic10`, and `ingot_printer_worker_pick_alloy.ic10` are legacy placeholders from an older multi-worker design and are not part of the current setup.
- The module now tracks all 17 Free Ingots outputs currently described by the profile metadata.
- The missing mod ingot hashes were derived consistently as signed CRC32 of the prefab/item name, which matches the already verified Stationeers ingot hashes in this repo.
