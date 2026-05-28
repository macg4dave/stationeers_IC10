# ingot_printer setup

Use this page to set up a LIFO-priority **multi-Autolathe ingot printer**.

This is a practical mod-support build for **Free Ingots** Autolathe ingot recipes.

These five scripts are part of the live module setup:

- `modular scripts/ingot_printer/ingot_printer_master.ic10`
- `modular scripts/ingot_printer/ingot_printer_worker_print.ic10`
- `modular scripts/ingot_printer/ingot_printer_worker_selector.ic10`
- `modular scripts/ingot_printer/ingot_printer_worker_finstd.ic10`
- `modular scripts/ingot_printer/ingot_printer_worker_stackers.ic10`

Do **not** use the deprecated helper files `ingot_printer_worker_reserve.ic10`,
`ingot_printer_worker_keep.ic10`, `ingot_printer_worker_pick_base.ic10`, or
`ingot_printer_worker_pick_alloy.ic10` for a new build.

## Build list

- 5x IC Housing + IC Chip
  - ingot_printer Master
  - ingot_printer Print Worker
  - ingot_printer Selector Worker
  - ingot_printer Finstd Worker
  - ingot_printer Stacker Worker
- 2x Logic Memory
  - `slot0`
  - `slot1`
- 1x Vending Machine
- 1x end-of-line Stacker
  - recommended label for clarity: `finstd`
- 1..N per-printer Stackers
  - `autostd`
- 1..N Autolathes

## Name contract

Set these exact names (case-sensitive):

- IC Housing: `master`
- IC Housing: `printer_worker`
- IC Housing: `selector_worker`
- IC Housing: `finstd_worker`
- IC Housing: `stacker_worker`
- IC Housing: `reserve_worker` (legacy placeholder file still present in the folder; not used by the live setup)
- Logic Memory: `slot0`
- Logic Memory: `slot1` (used to block reselecting an ingot when `finstd` is already over `100`)
- Autolathe: `printer` (apply this exact name to every controlled Autolathe)
- Stacker: `autostd` (apply this exact name to every per-printer stacker that should hold fixed stack size `10`)

Recommended for player clarity only:

- end-of-line Stacker on master `d0`: `finstd`

Internal prefab tokens used by the name-based scripts:

- `StructureLogicMemory`

## Wiring map

### `ingot_printer_master.ic10`

- no device wiring required; `d0..d5` stay unused as `n0..n5`

### `ingot_printer_worker_print.ic10`

- `d0` -> one representative Autolathe that is also named `printer`

### `ingot_printer_worker_selector.ic10`

- `d0` -> finished-goods Vending Machine

### `ingot_printer_worker_finstd.ic10`

- `d0` -> end-of-line Stacker (`finstd` recommended)

### `ingot_printer_worker_stackers.ic10`

- `d0` -> one representative per-printer Stacker that is also named `autostd`

## Setup steps

1. Put all five IC Housings, both Logic Memories, the Vending Machine, the end-of-line Stacker, every per-printer `autostd` Stacker, and every Autolathe on one data network.
2. Paste these scripts: `modular scripts/ingot_printer/ingot_printer_master.ic10`, `modular scripts/ingot_printer/ingot_printer_worker_print.ic10`, `modular scripts/ingot_printer/ingot_printer_worker_selector.ic10`, `modular scripts/ingot_printer/ingot_printer_worker_finstd.ic10`, and `modular scripts/ingot_printer/ingot_printer_worker_stackers.ic10`.
3. Apply the required names from **Name contract**.
4. Leave the master device pins unused.
5. Wire the print worker `d0` to one representative Autolathe that is also named `printer`.
6. Wire `selector_worker` `d0` to the finished-goods Vending Machine.
7. Wire `finstd_worker` `d0` to the end-of-line Stacker.
8. Wire `stacker_worker` `d0` to one representative per-printer Stacker that is also named `autostd`.
9. Rename every production Autolathe you want controlled by this module to the exact same name: `printer`.
10. Place one `autostd` Stacker after each controlled Autolathe so each printer pre-stacks its own output to fixed size `10` before entering the shared chute network.
11. Build the chute path so all `autostd` Stackers feed one end-of-line Stacker (`finstd` in this guide), and then route the end-of-line Stacker output into the finished-goods Vending Machine.
12. Power everything.
13. Wait until `master`, `selector_worker`, `finstd_worker`, and `stacker_worker` all leave boot / error states.

## Controls

There are no buttons or dials in normal use.

Once powered, `selector_worker` continuously scans the Vending Machine and determines which supported ingot is below `100` and should currently be printed.

At the same time, `finstd_worker` continuously manages the end-of-line Stacker. If the current ingot held in `finstd` goes over `100`, it blocks that same ingot in `slot1`. That lets the system switch the Autolathes to a different low ingot immediately instead of waiting for the master to do all the counting itself.

When `finstd` crosses the target, `finstd_worker` now writes the next valid ingot directly into `slot0` if one exists, so the Autolathes switch faster.

If no different low ingot exists, `finstd_worker` does **not** eject `finstd`. Instead, it leaves that batch in the final stacker, keeps the ingot blocked in `slot1`, and immediately forces `slot0 = 0` so the printers stop until another valid ingot can be selected or the held `finstd` amount drops back under the threshold.

At the same time, `stacker_worker` continuously forces every exact-name `autostd` Stacker to `On = 1`, `Mode = Automatic`, and `Setting = 10`. Those per-printer Stackers are configuration-only in this module: they are not counted by the stock logic.

The master now only mirrors the safe selector result into `slot0`, and `printer_worker` applies that hash to all named `printer` Autolathes.

`selector_worker` still keeps the current ingot locked if it is still low, but it will not keep that ingot when `slot1` says `finstd` already holds more than the target for it. That is the handoff that makes the extra worker chip useful.

Because blocked ingots are now skipped entirely while they remain in `slot1`, the system can intentionally sit stopped with `slot0 = 0` if the only low ingot is the same one already over `100` in `finstd`. That is expected with the no-eject design.

Current testing target: `100` items in the finished-goods Vending Machine for each tracked ingot.

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
- `finstd_worker` (`db Setting`)
- `stacker_worker` (`db Setting`)
- `slot0` (`Setting`)
- `slot1` (`Setting`)
- Vending Machine: relevant slot totals for the ingot you expected to print
- final Stacker (`finstd`): `Setting`, `Mode`, `On`, `ImportCount`, `ExportCount`
- representative `autostd` Stacker: `Setting`, `Mode`, `On`
- representative Autolathe: `On`, `Open`, `Activate`, `RecipeHash`, `ExportCount`

Quick interpretation:

- if `master = 248` or `printer_worker = 148`, fix the `slot0` Logic Memory name/network first
- if `master = 249`, fix the `slot1` Logic Memory name/network first
- if `master = 250`, fix the `selector_worker` name/network first
- if `master = 251`, fix the `finstd_worker` name/network first
- if `master = 260`, fix the underlying `selector_worker` error before trusting `slot0`
- if `stacker_worker = 344`, fix the representative `autostd` Stacker mapping on worker `d0`
- if `printer_worker = 144`, fix the representative Autolathe mapping on worker `d0`
- if `selector_worker = 640`, fix the Vending Machine mapping on selector `d0`
- if `selector_worker = 648`, fix the `slot0` Logic Memory name/network
- if `selector_worker = 649`, fix the `slot1` Logic Memory name/network
- if `finstd_worker = 442`, fix the final Stacker mapping on `finstd_worker` `d0`
- if `finstd_worker = 448` or `449`, fix the Logic Memory names/network
- if `finstd_worker = 450`, fix the `selector_worker` name/network
- if `slot0` stays `0`, the master has not queued any low ingots yet
- if `slot1` shows an ingot hash, `finstd` is currently blocking that ingot from immediate reselection
- if `slot0 = 0` and `slot1` still shows an ingot hash, the system is intentionally stopped waiting for a different low ingot or for `finstd` to clear naturally
- if `slot0` shows an ingot hash but the printers do nothing, verify that all production Autolathes are renamed exactly `printer`
- if chute congestion still happens, verify that every per-printer Stacker is renamed exactly `autostd` and that `stacker_worker` has reached `310`
