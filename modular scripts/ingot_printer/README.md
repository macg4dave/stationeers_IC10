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
- `ingot_printer_worker_finstd.ic10`
- `ingot_printer_worker_stackers.ic10`

Deprecated helper files that are **not used** by the current live flow:

- `ingot_printer_worker_reserve.ic10`
- `ingot_printer_worker_keep.ic10`
- `ingot_printer_worker_pick_base.ic10`
- `ingot_printer_worker_pick_alloy.ic10`

## Requirements

- **Free Ingots** mod (or another mod/config that adds the same Autolathe ingot recipes)
- 5x IC Housing + IC Chip
- 2x Logic Memory
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

- `d0..d5` = unused (`n0..n5`)
- `db` = status

### `ingot_printer_worker_print.ic10`

- `d0` = one representative Autolathe that is also named `printer`
- `db` = status / current active target hash

### `ingot_printer_worker_selector.ic10`

- `d0` = finished-goods Vending Machine
- `db` = active target hash to keep/print, else `0`

### `ingot_printer_worker_finstd.ic10`

- `d0` = end-of-line Stacker (`finstd` recommended)
- `db` = final-stacker worker status / current routed hash

### `ingot_printer_worker_stackers.ic10`

- `d0` = one representative Stacker also named `autostd`
- `db` = stacker-worker status

Unused pins are explicitly labelled `n1..n5` / `n2..n5` so the in-game housing labels stay clean after updates.

## Name contract

Set these exact names (case-sensitive):

- IC Housing: `master`
- IC Housing: `printer_worker`
- IC Housing: `selector_worker`
- IC Housing: `finstd_worker`
- IC Housing: `stacker_worker`
- Logic Memory: `slot0`
- Logic Memory: `slot1` (temporary block for the ingot currently over target in `finstd`)
- Autolathe: `printer` (apply this exact name to **every** Autolathe the module should control)
- Stacker: `autostd` (apply this exact name to every per-printer stacker you want held at fixed stack size)

Recommended for player clarity only:

- end-of-line Stacker on master `d0`: `finstd`

## Behavior

Master behavior:

1. validates `slot0`, `slot1`, `selector_worker`, and `finstd_worker`
2. mirrors the safe selector result into `slot0`
3. leaves the print / final-stacker details to the workers instead of duplicating them in the master

Print-worker behavior:

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

Finstd-worker behavior:

1. drives the end-of-line Stacker to `On = 1`, `Mode = Automatic`, and `Setting = 1000`
2. watches the live item and quantity currently held in `finstd`
3. if the current printed ingot in `finstd` rises above `100`, writes that ingot hash to `slot1`
4. `slot1` tells `selector_worker` not to keep choosing that same ingot just because the Vending Machine is still catching up
5. if another low ingot exists, the worker writes that next ingot straight into `slot0` so the printers switch without waiting for an extra master cycle
6. if no different low ingot exists, the worker does **not** eject `finstd`; it simply holds the block in `slot1` and immediately forces `slot0 = 0` so the printers stop
7. once `finstd` is no longer over-threshold for the old ingot, it clears `slot1` again

Selector-worker behavior:

- `selector_worker` scans the Vending Machine directly instead of depending on one IC per ingot
- it rescans each supported ingot, sums quantities exactly, and finds the highest-priority low ingot
- if `slot1` is blocking an ingot because `finstd` already holds more than the target amount, that ingot is skipped entirely until the block clears
- otherwise, if the currently active target from `slot0` is still low, it republishes that same target instead of switching early
- otherwise it returns the best next low ingot according to the tracked-order priority

Gap-avoidance behavior:

- the Vending Machine remains the stored-inventory source of truth
- `finstd` is the live overrun detector for the current printed ingot
- once `finstd` holds more than `100` of the current ingot, `finstd_worker` blocks that ingot through `slot1`
- if another low ingot exists, `finstd_worker` pushes that next ingot into `slot0` immediately so printing changes over faster
- if no other low ingot exists, `finstd_worker` pushes `slot0 = 0` immediately so printing stops and `finstd` is left alone; the blocked ingot will not be reselected until `finstd` naturally clears below the threshold or changes item

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
- `200` = idle / selector returned `0`
- any tracked ingot hash = current target written to `slot0`
- `248` = missing `slot0`
- `249` = missing `slot1`
- `250` = missing `selector_worker`
- `251` = missing `finstd_worker`
- `260` = `selector_worker` is reporting an error code instead of a target hash

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
- `649` = missing `slot1`

### Finstd worker (`400-499` and active target hashes)

- `400` = boot
- `401` = turning `finstd` on
- `402` = setting `finstd` to `Mode = Automatic`
- `403` = setting `finstd` `Setting = 1000`
- `410` = steady / no alternate ingot needed right now
- any tracked ingot hash = `finstd` is over-threshold for that ingot and routing has shifted away from it
- `442` = missing end-of-line Stacker on `d0`
- `448` = missing `slot0`
- `449` = missing `slot1`
- `450` = missing `selector_worker`

### Stacker worker (`300-399`)

- `300` = boot
- `301` = turning all named `autostd` stackers on
- `302` = setting all named `autostd` stackers to `Mode = Automatic`
- `303` = setting all named `autostd` stackers to `Setting = 10`
- `310` = all named `autostd` stackers are configured for fixed stack size `10`
- `344` = missing representative Stacker on `d0`

## Notes

- This module lives under `modular scripts/` so it can act as a more realistic test bed for opt-in mod support.
- It uses one directly wired representative Autolathe only to discover device type and local state; all real production commands are sent to every exact-name `printer` Autolathe on the data network.
- The finished-goods Vending Machine is scanned exactly by summing slot quantities, not just checking for item presence.
- The optional `stacker_worker` batch-configures every exact-name `autostd` stacker to fixed stack size `10` so each Autolathe can pre-stack output before it enters the shared chute network.
- The current live design uses a dedicated `finstd_worker` so the master no longer has to own the overrun-switch logic.
- `finstd_worker` never calls `Activate`; it only blocks reselection and lets the printers switch or stop.
- For faster response, `finstd_worker` can write `slot0` directly when it detects an over-target batch; the master still reconciles against `selector_worker` on the next loop.
- `ingot_printer_worker_reserve.ic10` is left in the folder as a legacy placeholder from the reserve-estimate experiment and is not part of the current live setup.
- The current testing target in this module is `100` items per ingot in the finished-goods Vending Machine.
- The compact build keeps the chip count low by using one selector worker instead of one stock worker per ingot.
- The module now tracks all 17 Free Ingots outputs currently described by the profile metadata.
- The missing mod ingot hashes were derived consistently as signed CRC32 of the prefab/item name, which matches the already verified Stationeers ingot hashes in this repo.
