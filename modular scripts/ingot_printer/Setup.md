# ingot_printer setup

Use this page to set up a LIFO-priority **multi-Autolathe ingot printer**.

This is a practical mod-support build for **Free Ingots** Autolathe ingot recipes.

## Build list

- 19x IC Housing + IC Chip
  - ingot_printer Master
  - ingot_printer Print Worker
  - ingot_printer Stock Worker: Silicon
  - ingot_printer Stock Worker: Iron
  - ingot_printer Stock Worker: Gold
  - ingot_printer Stock Worker: Copper
  - ingot_printer Stock Worker: Silver
  - ingot_printer Stock Worker: Lead
  - ingot_printer Stock Worker: Nickel
  - ingot_printer Stock Worker: Steel
  - ingot_printer Stock Worker: Electrum
  - ingot_printer Stock Worker: Invar
  - ingot_printer Stock Worker: Constantan
  - ingot_printer Stock Worker: Solder
  - ingot_printer Stock Worker: Astroloy
  - ingot_printer Stock Worker: Hastelloy
  - ingot_printer Stock Worker: Inconel
  - ingot_printer Stock Worker: Waspaloy
  - ingot_printer Stock Worker: Stellite
- 1x Logic Memory
  - `slot0`
- 1x Vending Machine
- 1x Stacker
- 1..N Autolathes

## Name contract

Set these exact names (case-sensitive):

- IC Housing: `master`
- IC Housing: `printer_worker`
- IC Housing: `stock_silicon`
- IC Housing: `stock_iron`
- IC Housing: `stock_gold`
- IC Housing: `stock_copper`
- IC Housing: `stock_silver`
- IC Housing: `stock_lead`
- IC Housing: `stock_nickel`
- IC Housing: `stock_steel`
- IC Housing: `stock_electrum`
- IC Housing: `stock_invar`
- IC Housing: `stock_constantan`
- IC Housing: `stock_solder`
- IC Housing: `stock_astroloy`
- IC Housing: `stock_hastelloy`
- IC Housing: `stock_inconel`
- IC Housing: `stock_waspaloy`
- IC Housing: `stock_stellite`
- Logic Memory: `slot0`
- Autolathe: `printer` (apply this exact name to every controlled Autolathe)

Internal prefab tokens used by the name-based scripts:

- `StructureLogicMemory`

## Wiring map

### `ingot_printer_master.ic10`

- `d0` -> end-of-line Stacker

### `ingot_printer_worker_print.ic10`

- `d0` -> one representative Autolathe that is also named `printer`

### Stock workers

For each of these files, wire `d0` to the finished-goods Vending Machine:

- `ingot_printer_worker_stock_iron.ic10`
- `ingot_printer_worker_stock_silicon.ic10`
- `ingot_printer_worker_stock_gold.ic10`
- `ingot_printer_worker_stock_copper.ic10`
- `ingot_printer_worker_stock_silver.ic10`
- `ingot_printer_worker_stock_lead.ic10`
- `ingot_printer_worker_stock_nickel.ic10`
- `ingot_printer_worker_stock_steel.ic10`
- `ingot_printer_worker_stock_electrum.ic10`
- `ingot_printer_worker_stock_invar.ic10`
- `ingot_printer_worker_stock_constantan.ic10`
- `ingot_printer_worker_stock_solder.ic10`
- `ingot_printer_worker_stock_astroloy.ic10`
- `ingot_printer_worker_stock_hastelloy.ic10`
- `ingot_printer_worker_stock_inconel.ic10`
- `ingot_printer_worker_stock_waspaloy.ic10`
- `ingot_printer_worker_stock_stellite.ic10`

## Setup steps

1. Put all nineteen IC Housings, the Logic Memory, the Vending Machine, the Stacker, and every Autolathe on one data network.
2. Paste these scripts: `modular scripts/ingot_printer/ingot_printer_master.ic10`, `modular scripts/ingot_printer/ingot_printer_worker_print.ic10`, `modular scripts/ingot_printer/ingot_printer_worker_stock_silicon.ic10`, `modular scripts/ingot_printer/ingot_printer_worker_stock_iron.ic10`, `modular scripts/ingot_printer/ingot_printer_worker_stock_gold.ic10`, `modular scripts/ingot_printer/ingot_printer_worker_stock_copper.ic10`, `modular scripts/ingot_printer/ingot_printer_worker_stock_silver.ic10`, `modular scripts/ingot_printer/ingot_printer_worker_stock_lead.ic10`, `modular scripts/ingot_printer/ingot_printer_worker_stock_nickel.ic10`, `modular scripts/ingot_printer/ingot_printer_worker_stock_steel.ic10`, `modular scripts/ingot_printer/ingot_printer_worker_stock_electrum.ic10`, `modular scripts/ingot_printer/ingot_printer_worker_stock_invar.ic10`, `modular scripts/ingot_printer/ingot_printer_worker_stock_constantan.ic10`, `modular scripts/ingot_printer/ingot_printer_worker_stock_solder.ic10`, `modular scripts/ingot_printer/ingot_printer_worker_stock_astroloy.ic10`, `modular scripts/ingot_printer/ingot_printer_worker_stock_hastelloy.ic10`, `modular scripts/ingot_printer/ingot_printer_worker_stock_inconel.ic10`, `modular scripts/ingot_printer/ingot_printer_worker_stock_waspaloy.ic10`, and `modular scripts/ingot_printer/ingot_printer_worker_stock_stellite.ic10`.

3. Apply the required names from **Name contract**.
4. Wire the master exactly as shown in **Wiring map**.
5. Wire the print worker `d0` to one representative Autolathe that is also named `printer`.
6. Wire every stock worker `d0` to the same finished-goods Vending Machine.
7. Rename every production Autolathe you want controlled by this module to the exact same name: `printer`.
8. Build the chute path so all controlled Autolathes feed one end-of-line Stacker, and then route the Stacker output into the finished-goods Vending Machine.
9. Power everything.
10. Wait until `master` leaves boot / error states.

## Controls

There are no buttons or dials in normal use.

Once powered, the stock workers continuously scan the Vending Machine and report which supported ingots are below `1000`.

The master then picks the **last low ingot in tracked order** and keeps all named `printer`
Autolathes on that recipe until the end-of-line Stacker exports one `1000`-item batch.
After each batch, the master re-evaluates the low-ingot set and picks the next target.

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
- `stock_silicon`, `stock_iron`, `stock_gold`, `stock_copper`, `stock_silver`, `stock_lead`, `stock_nickel`, `stock_steel`, `stock_electrum`, `stock_invar`, `stock_constantan`, `stock_solder`, `stock_astroloy`, `stock_hastelloy`, `stock_inconel`, `stock_waspaloy`, `stock_stellite` (`db Setting`)
- `slot0` (`Setting`)
- Vending Machine: relevant slot totals for the ingot you expected to print
- Stacker: `Setting`, `Mode`, `On`, `ExportCount`
- representative Autolathe: `On`, `Open`, `Activate`, `RecipeHash`, `ExportCount`

Quick interpretation:

- if `master = 242`, fix the Stacker mapping on `d0`
- if `master = 248` or `printer_worker = 148`, fix the `slot0` Logic Memory name/network first
- if `printer_worker = 144`, fix the representative Autolathe mapping on worker `d0`
- if any stock worker shows `540`, fix that worker's Vending Machine mapping on `d0`
- if `slot0` stays `0`, the master has not queued any low ingots yet
- if `slot0` shows an ingot hash but the printers do nothing, verify that all production Autolathes are renamed exactly `printer`
