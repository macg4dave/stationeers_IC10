# ingot_printer setup

Use this page to set up a LIFO-priority **multi-Autolathe ingot printer**.

This is a practical mod-support build for **Free Ingots** Autolathe ingot recipes.

Only these three scripts are part of the live module setup:

- `modular scripts/ingot_printer/ingot_printer_master.ic10`
- `modular scripts/ingot_printer/ingot_printer_worker_print.ic10`
- `modular scripts/ingot_printer/ingot_printer_worker_selector.ic10`

Do **not** use the deprecated helper files `ingot_printer_worker_keep.ic10`,
`ingot_printer_worker_pick_base.ic10`, or `ingot_printer_worker_pick_alloy.ic10` for a new build.

## Build list

- 3x IC Housing + IC Chip
  - ingot_printer Master
  - ingot_printer Print Worker
  - ingot_printer Selector Worker
- 1x Logic Memory
  - `slot0`
- 1x Vending Machine
- 1x Stacker
- 1..N Autolathes

## Name contract

Set these exact names (case-sensitive):

- IC Housing: `master`
- IC Housing: `printer_worker`
- IC Housing: `selector_worker`
- Logic Memory: `slot0`
- Autolathe: `printer` (apply this exact name to every controlled Autolathe)

Internal prefab tokens used by the name-based scripts:

- `StructureLogicMemory`

## Wiring map

### `ingot_printer_master.ic10`

- `d0` -> end-of-line Stacker

### `ingot_printer_worker_print.ic10`

- `d0` -> one representative Autolathe that is also named `printer`

### `ingot_printer_worker_selector.ic10`

- `d0` -> finished-goods Vending Machine

## Setup steps

1. Put all three IC Housings, the Logic Memory, the Vending Machine, the Stacker, and every Autolathe on one data network.
2. Paste these scripts: `modular scripts/ingot_printer/ingot_printer_master.ic10`, `modular scripts/ingot_printer/ingot_printer_worker_print.ic10`, and `modular scripts/ingot_printer/ingot_printer_worker_selector.ic10`.

3. Apply the required names from **Name contract**.
4. Wire the master exactly as shown in **Wiring map**.
5. Wire the print worker `d0` to one representative Autolathe that is also named `printer`.
6. Wire `selector_worker` `d0` to the finished-goods Vending Machine.
7. Rename every production Autolathe you want controlled by this module to the exact same name: `printer`.
8. Build the chute path so all controlled Autolathes feed one end-of-line Stacker, and then route the Stacker output into the finished-goods Vending Machine.
9. Power everything.
10. Wait until `master` leaves boot / error states.

## Controls

There are no buttons or dials in normal use.

Once powered, `selector_worker` continuously scans the Vending Machine and determines which supported ingot is below `1000` and should currently be printed.

The master then picks the **last low ingot in tracked order** and keeps all named `printer`
Autolathes on that recipe until the end-of-line Stacker exports a batch **and** the current
ingot is no longer reported low by the `selector_worker`.
After each batch edge, the master re-evaluates the low-ingot set, but it stays on the same ingot
if that ingot still has not reached target stock.

Internally, `selector_worker` keeps the current ingot locked if it is still low; otherwise it picks the best next low ingot according to the same tracked-order priority.

Tracked ingots:

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

Priority note: because selection is last-low-found first, later entries found low in the tracked order print first.

## Runtime debug snapshot (required for issue reports)

When debugging, capture these values in one screenshot/note:

- `master` (`db Setting`)
- `printer_worker` (`db Setting`)
- `selector_worker` (`db Setting`)
- `slot0` (`Setting`)
- Vending Machine: relevant slot totals for the ingot you expected to print
- Stacker: `Setting`, `Mode`, `On`, `ExportCount`
- representative Autolathe: `On`, `Open`, `Activate`, `RecipeHash`, `ExportCount`

Quick interpretation:

- if `master = 242`, fix the Stacker mapping on `d0`
- if `master = 248` or `printer_worker = 148`, fix the `slot0` Logic Memory name/network first
- if `master = 249`, fix the `selector_worker` name/network first
- if `printer_worker = 144`, fix the representative Autolathe mapping on worker `d0`
- if `selector_worker = 640`, fix the Vending Machine mapping on selector `d0`
- if `selector_worker = 648`, fix the `slot0` Logic Memory name/network
- if `slot0` stays `0`, the master has not queued any low ingots yet
- if `slot0` shows an ingot hash but the printers do nothing, verify that all production Autolathes are renamed exactly `printer`
