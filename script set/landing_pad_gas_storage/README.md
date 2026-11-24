# landing_pad_gas_storage

Moves gas bought from a trader off the landing pad, through one **main pipe**, into a
tank for each gas. Dirty or mixed gas goes to a **Waste** tank; when Waste is full, a
purge valve and Active Vent empty the main pipe.

The rule that matters most: **the pad and the main pipe are cleared before the next gas
goes in.** Gas in the main pipe always leaves first: to its own tank, else to Waste,
else out of the purge vent. Gas still on the pad is never vented; it waits.

```text
 purge vent ─ purge valve ─┬─────────────── MAIN PIPE (analyzer) ─────────────── Landingpad Gas Output ─ pad
                           │                     │                     │
                     pump "Waste"          pump "Oxygen"       pump "CarbonDioxide"   ... one per gas
                           │                     │                     │
                      Waste tank              O2 tank               CO2 tank
                  (analyzer "Waste")   (analyzer "Oxygen")  (analyzer "CarbonDioxide")
```

| Chip | Job |
| --- | --- |
| `pad_gas_router.ic10` | Identifies the gas in the main pipe, pumps it into the right tank, and switches the pad output |
| `main_pipe_purge.ic10` | Opens the purge valve and vent when the main pipe holds gas that has nowhere to go |

The chips do not talk to each other; each reads the devices. You can run the router
alone; without the purge chip, gas with nowhere to go stays in the main pipe.

## Where each gas goes

The router identifies the gas **in the main pipe**, not on the pad: the pad feeds the
pipe, so the pipe shows what the pad holds. A gas is **pure** at ≥ 99.9 % (`GAS_MIN`).
Anything else (a mix, or a "dirty" gas with byproducts) is **dirty**.

| Gas in the main pipe | Goes to | The pad |
| --- | --- | --- |
| Pure, its tank has room | its tank | keeps unloading |
| Pure, no tank built for it | Waste | keeps unloading |
| Dirty | Waste | keeps unloading |
| Pure, its tank full | Waste (the pipe must clear) | waits until that tank has room |
| Anything, Waste full or missing | purge vent (`main_pipe_purge`) | waits until Waste has room |

All 8 gas ratios the repo catalog knows are already in the table, so a pure gas you
have no tank for still goes to Waste. Build tanks only for the gases you want to keep.

## Build

- Landing pad with one **Landingpad Gas Output** connector feeding the **main pipe**
- **Pipe Analyzer** on the main pipe
- For each tank (including Waste): a **Volume Pump** from the main pipe into the tank
  and a **Pipe Analyzer** on the tank's pipe, **both renamed** to the tank name below
- Purge: a **Pipe Digital Valve** from the main pipe to an **Active Vent** placed
  outside (the vent blows into the atmosphere around it)
- (optional) a light for "ready"
- Two IC Housings with chips; power and data cable to everything (one data network)

Use Volume Pumps, not valves, into the tanks: a valve only lets gas flow while the main
pipe is at a higher pressure than the tank, so it cannot empty the main pipe.

### Tank names (exact, case-sensitive)

Name the tank's Volume Pump **and** its Pipe Analyzer with the same name.

| Gas | Name | Ratio read |
| --- | --- | --- |
| Oxygen | `Oxygen` | `RatioOxygen` |
| Nitrogen | `Nitrogen` | `RatioNitrogen` |
| CO2 | `CarbonDioxide` | `RatioCarbonDioxide` |
| Methane | `Methane` | `RatioMethane` |
| Hydrogen | `Hydrogen` | `RatioHydrogen` |
| Nitrous oxide | `NitrousOxide` | `RatioNitrousOxide` |
| Pollutant | `Pollutant` | `RatioPollutant` |
| Steam | `Steam` | `RatioSteam` |
| Dirty, mixed or no tank | `Waste` | — |

## Chip 1: `pad_gas_router.ic10`

### Pins

| Pin | Name | Device |
| --- | --- | --- |
| `d0` | `pad` | Landingpad Gas Output feeding the main pipe |
| `d1` | `line` | Pipe Analyzer on the main pipe |
| `d2` | `ready` | (optional) any light: ON when the pad and main pipe are clear |

### What it does (every tick)

1. **Main pipe holds gas** (≥ 1 kPa): it is pumped where the table above says.
2. **Main pipe clear:** the pad output is ON (unless the pad waits for a full tank).
   When gas arrives, step 1 takes it.
3. **Main pipe stays clear for 5 s with the pad output ON:** the pad is empty. Status
   `1`, ready light ON. Buy the next gas.

- Only one pump runs at a time; when the target changes, the old pump is switched off
  first. At start every Volume Pump on the network is switched off once.
- Tank full: its analyzer ≥ 10 MPa; it has room again below 9.5 MPa.
- Main pipe over 20 MPa: the pad stops; it starts again below 19 MPa. The pump keeps
  draining.
- Main pipe analyzer `Error`, or the pad or analyzer pin missing: pad and pumps OFF.

### Settings

| Setting | Default | Meaning |
| --- | --- | --- |
| `GAS_MIN` | `0.999` | Ratio counted as one pure gas |
| `CLEAR_KPA` | `1` | Main pipe counts as clear below (kPa) |
| `LINE_MAX_KPA` | `20000` | Pad stops above (kPa, main pipe) |
| `LINE_REARM_KPA` | `19000` | Pad starts again below (kPa) |
| `FULL_KPA` | `10000` | Tank counts as full at (kPa, tank analyzer) |
| `REOPEN_KPA` | `9500` | Tank has room again below (kPa) |
| `READY_TICKS` | `10` | Ticks (0.5 s each) the pipe must stay clear before "ready" |

### Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `1` | ready: pad and main pipe clear, buy the next gas |
| `2` | main pipe clear, pad output ON, checking for gas |
| `10` | unloading the pad into a tank |
| `11` | clearing the main pipe into a tank; the pad waits |
| `30` | pad waits: the tank its gas needs (or Waste) has no room |
| `31` | main pipe full; pad paused while the pump drains it |
| `32` | main pipe gas has nowhere to go; waiting for `main_pipe_purge` |
| `9` | pad or main pipe analyzer missing, or analyzer error |

### Adding a gas

The table has room for **4 more gases** (12 in total) under the 128-line paste limit.

1. In `pad_gas_router.ic10`, under `# gas table`, copy the 3 lines of one gas and change
   the ratio and the name, e.g.:

   ```text
   l r0 line RatioNewGas
   brlt r0 GAS_MIN 2
   move r5 HASH("NewGas")
   ```

   Use the ratio name exactly as a Logic Reader on a Pipe Analyzer shows it, and add
   it to `catalog/devices/Pipe_Analyzer.json` (the lint warns about unknown names).
2. Build a Volume Pump and a tank Pipe Analyzer named after it (the `HASH` name).
3. Add a row to the tank names table above.

`brlt r0 GAS_MIN 2` skips the next line when the gas is under 99.9 %. Keep the `2`: it
is a line offset, not a label.

### Registers

Raw registers keep room for gases.

| Register | Holds |
| --- | --- |
| `r0` | ratio of the gas being checked |
| `r5` | gas in the main pipe (tank name hash; `Waste` when no table gas is pure) |
| `r6` | target tank this tick (0 = main pipe clear) |
| `r7` | tank the pad waits for (0 = none) |
| `r8` | main pipe kPa |
| `r9` | status |
| `r10` / `r11` | pad on / target pump on |
| `r12` `r13` | scratch (`tank` returns `r12` = tank exists, `r11` = has room) |
| `r14` | pump that was running (switched off when the target changes) |
| `r15` | ticks the main pipe has been clear with the pad output ON |

## Chip 2: `main_pipe_purge.ic10`

### Pins

| Pin | Name | Device |
| --- | --- | --- |
| `d0` | `line` | Pipe Analyzer on the main pipe (the same one as the router's `d1`) |
| `d1` | `purge` | Pipe Digital Valve from the main pipe to the vent |
| `d2` | `vent` | Active Vent behind the purge valve, outside |

### What it does

- Purge valve and vent ON (vent `Mode` 0 = outward, `Open` 1) while **all** of:
  the main pipe holds gas (≥ 1 kPa), no Volume Pump on the network is on, and the tank
  analyzer `Waste` is missing or reads ≥ 9.5 MPa — for 3 s in a row.
- Stops as soon as the pipe is clear, a pump starts, or Waste has room again.
- 9.5 MPa is the router's re-open level, so the router has given up on Waste whenever
  this chip sees it as full. The router also has the pad waiting by then, so only the
  gas already in the main pipe is vented.
- Analyzer `Error` or a missing pin: valve and vent OFF.

### Settings

| Setting | Default | Meaning |
| --- | --- | --- |
| `CLEAR_KPA` | `1` | Main pipe counts as clear below (kPa); keep equal to the router's |
| `WASTE_FULL_KPA` | `9500` | Waste counts as full at (kPa); keep equal to the router's `REOPEN_KPA` |
| `WAIT_TICKS` | `6` | Ticks (0.5 s each) the pipe must be stuck before purging |

### Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | idle: pipe clear, a pump is moving the gas, or Waste has room |
| `1` | gas stuck in the main pipe; waiting `WAIT_TICKS` |
| `2` | purging |
| `9` | device missing or analyzer error |

## Setup

1. Build the devices above and connect them, both IC Housings and power to one data
   network. Keep other Volume Pumps off this network: the router switches every Volume
   Pump off at start, and any running Volume Pump stops the purge.
2. Rename each tank's Volume Pump and Pipe Analyzer (labeller) to its tank name.
3. Router housing: `d0` Landingpad Gas Output, `d1` main pipe analyzer, `d2` light
   (optional). Paste `pad_gas_router.ic10`.
4. Purge housing: `d0` main pipe analyzer, `d1` purge valve, `d2` Active Vent. Paste
   `main_pipe_purge.ic10`.
5. With an empty pad and main pipe the router shows `2`, then `1` after 5 s. Buy a gas:
   `10` while it unloads, `2` when the pipe is clear again, then `1`.

## Notes

- **The pad output stays ON while idle** (status `1`/`2`) so new gas flows straight
  into the main pipe. Not checked in-game: whether an ON output affects a trader
  landing or a sale. If it does, report it.
- **"Pad empty" is a guess from the pipe:** the main pipe stays clear for
  `READY_TICKS` with the output ON. If gas takes longer to show up after the output
  turns on, raise `READY_TICKS`.
- **The pad waits for a full tank** until that tank drops below 9.5 MPa, even if the
  pad is in fact already empty. Empty some of the tank (or restart the chip) to go on.
- **How low a Volume Pump can empty a pipe** is not checked in-game. If the router
  stays at `11` with a few kPa left, raise `CLEAR_KPA` in both chips.
- **Pressure limits.** 10 MPa (tanks) and 20 MPa (main pipe) are the values other
  scripts here use. Check what your tanks and pipes are rated for.
- **The ready light does not block a trade.** Wait for `1` before buying the next gas.
- **Router chip missing or stopped:** the purge chip only sees "gas, no pump running,
  Waste full", so it would vent the main pipe whatever gas it holds.
- Device notes: `docs/usage/landingpad_output.md`, `docs/usage/pipe_analyzer.md`,
  `docs/usage/active_vent.md`, `docs/usage/pipe_digital_valve.md`

## Change history

- 2026-11-24: new set. Main pipe with one Volume Pump per tank, cleared before the next
  gas unloads; dirty gas to Waste; purge vent when Waste is full. The gas is identified
  in the main pipe (3 lines per gas), so the router holds 12 gases (8 in the table).

## Status

Functional (simulated in `tests/standalone.rs`, not run in-game yet).
