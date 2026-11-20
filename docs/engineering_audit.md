# Engineering audit (2026-11)

Scope: every `.ic10` under `scripts/` and `modular scripts/`, the Python tools, the
catalog, templates and docs. Branch `modernisation/engineering-audit`.

**How to read results.** *Static* = lint/size/contract checks. *Simulated* = scenario
passes in `tools/ic10_engine.py` (a model of the chip, not the game). *In-game* = only
the user can confirm. Nothing below is claimed as in-game verified unless the user
said so.

## 1. Architecture

- **Standalone scripts** (29): one chip, devices on pins `d0..d5`, sometimes batch
  targeting of named devices (`sbn`/`lbn`). Pattern: wait loop with `bdns` → main loop
  reads sensor → decides → read-before-write to actuators → `yield`/`sleep`.
- **Modular features** (4, 22 chips incl. 2 generated variants): master + workers +
  setup guard. Chips talk through named Logic Memory devices (`cmd_token`, `cmd_type`,
  `slotN`) found by `lbn` on the shared data network, and read each other's housing
  `Setting` as status. Masters keep workers `On`; workers each own one loop.
- **Catalog**: per-device LogicTypes, `modeValues`, item and structure hashes; wiki
  import (HTML or Special:Export XML); recipe catalog and Autolathe profiles that
  generate the `*.free_ingots.ic10` variants.
- **Tooling** (stdlib Python): paste-limit, setup-contract, catalog and doc-path
  checkers; wiki importers; profile emitter. Added in this audit: `ic10_engine.py`
  (parser, analyser, simulator), `ic10_lint.py`, `check_all.py`, `tests/`.

Inter-script dependencies: none between standalone scripts (each owns its devices;
two scripts both use the name `cold` — `pipe_temp_valve` and `phase_change_temp_valve`
— so they must not share a data network). Modular chips depend on each other only
through the documented memory/housing contracts.

## 2. Evidence used

| Fact | Evidence | Confidence |
| --- | --- | --- |
| Prefab hash = signed CRC-32 of prefab name | 14 of 17 hard-coded hashes reproduce exactly (Active Vent, Gas Sensor, Digital Valve, Advanced Furnace, AC, Volume Pump, Gas Generator, Sorter, Harvie, Grow Light, Pipe Heater, Wall Heater, Logic Switch, Logic Dial, Flashing Light, Klaxon) | confirmed |
| `br*` take relative offsets; `b*`/`j` absolute | IC10 instruction set; file `sat_trader_track_worker_dish.ic10` uses both correctly elsewhere | confirmed |
| Analyzer / Gas Sensor `Pressure` in kPa | wiki tables ("In kPa") and every working pressure script's thresholds | confirmed |
| Methane replaced Volatiles | user (in-game) | confirmed |
| Labels/comments use an execution slot | common IC10 behaviour; encoded in simulator | assumed |
| Batch read with no match returns 0 | simulator assumption; scripts only compare it to a hash | assumed |
| Liquid Digital Valve prefab `-517628750` | no candidate prefab name matches; script reported Functional | unverified |
| Large Satellite Dish prefab `HASH("Large_Satellite_Dish")` | that string is a wiki title, not a prefab name | suspect (S7) |

## 3. Baseline (before any change)

| Check | Result |
| --- | --- |
| paste limits (both trees) | pass |
| setup contracts | pass |
| catalog schema | **fail**: index lists missing `Landingpad_Gas_Storage.json`; `phase_change_device.json` not indexed |
| doc paths | **fail**: 2 links to the deleted SatCom feature's Setup.md |
| generator | committed variants matched; regenerating on Windows rewrote every line (CRLF) |
| behaviour tests | none existed |
| new lint (first run) | 2 errors (D4), 1 suspicious jump (D6), 3 define chains |
| new scenarios vs original scripts | 42 pass (baseline behaviour captured), 10 reproduce D1–D7 |

## 4. Confirmed defects (all fixed, one commit each)

| ID | Where | Defect | Impact | Fix | Risk |
| --- | --- | --- | --- | --- | --- |
| D1 | `pipe_temp_hot_cold_valves` | Pressure > 2000 divided by 1000 ("Pa guess") | pump never stops at the 10 MPa target: unbounded pressure | read kPa directly | low |
| D2 | `room_pressure_active_vent`, `room_co2_below_20pct_active_vent` | same heuristic | a > 2 MPa room reads as ~2 kPa → intake / vent opens (positive feedback) | read kPa directly | low (normal rooms unchanged) |
| D3 | `active_vent_dual_sets` | `state` boots at 0 = OFF, so cold start writes nothing | vents left running stay on | start `state` at -1 | low |
| D4 | `PotatoHarvieTest` actuator | `brlt`/`brge` given labels | jumps ~63 lines into the off-tail: light never on, Harvie never plants/harvests | `blt`/`bge` | low |
| D5 | `SatTraderTrack` master | `bnez cur` before `l cur dishw On` | dish worker not re-enabled (dial ≠ 0) or rewritten every tick (dial 0) | add the load | low |
| D6 | `SatTraderTrack` dish worker | `beqz prog 2` (absolute) instead of `breqz` | "any trader" mode never sweeps | `breqz prog 2` | medium (needs game test) |
| D7 | `AutolatheVendStock` machine worker | ready check inverted | machine worker sets `slot3=1` on a *mismatched* recipe; prep skips `RecipeHash`; wrong item built | `bne ... wait_prep` | medium (needs game test) |
| D8 | `autolathe_profile_emit.py` | platform newlines | Windows regen rewrites generated files | LF + `--check` | none |
| D9 | docs / catalog | 8 phantom scripts + 4 phantom features listed; SatCom playbook for deleted feature; bad index entries | users and agents chase files that do not exist | rebuilt indexes, removed playbook, fixed index; checker now catches this | none |

Also: three `define` chains replaced with literals (cannot verify the game resolves
them; literals are equivalent either way).

## 5. Suspected defects and risks (not changed — need in-game evidence)

| ID | Where | Observation | Suggested check / change | Priority |
| --- | --- | --- | --- | --- |
| S1 | `vending_machine_export` | waits forever if the item is not stocked; request memory is cleared first, so the request is lost | in-game: request an absent item. Fix would add a timeout | medium |
| S2 | `AutolatheVendStock` feeder | writes `RequestHash` every tick until the ingot reaches the sorter; may dispense several stacks in transit | watch a refill in-game; if over-dispensing, request once per `ImportCount` change | medium |
| S3 | `pipe_pressure_gas_mixer`, `gas_sensor_glass_door_30c` | single threshold, no deadband | can chatter at the threshold; add a band if users see flapping | low |
| S4 | `volatiles_purge_valve` | on analyzer error it jumps to `wait` and leaves the valve as it was | decide: hold or force closed | low |
| S5 | `dual_analyzer_furnace_pulse`, `pipe_furnace_valve_below_20c` | rely on Advanced Furnace `Activate` semantics (pulse vs latched) not documented in catalog | confirm in-game which one the furnace expects | low |
| S6 | `air_conditioner_25c` | forces `Mode = 1`; catalog lists Mode 0 Idle / 1 Active (may be a status) | confirm writing Mode is needed | low |
| S7 | `SatTraderTrack` setup guard | large dish prefab = `HASH("Large_Satellite_Dish")` (a wiki title) | if the guard always shows `97` with `dish_l` present, the hash is wrong; the guard only reports, workers still run | low |
| S8 | `liquid_temp_valve` | prefab `-517628750` not reproducible from a known name | reported Functional; keep | info |
| S9 | 15 standalone scripts | no `bdns` inside the main loop (only in the wait loop) | removing a device mid-run halts the chip; adding the guard is one line per pin | low |

## 6. Design review (questionable or unnecessary complexity)

- **PotatoHarvieTest**: the master increments `cmd_token`, but no worker reads it; master
  and setup guard both force the workers `On`. Four chips and five memories for a job
  that two chips could do. Kept: players have it wired; simplification is optional.
- **ingot_printer**: `slot0` has two writers (master and `finstd_worker`). Both copy the
  selector's pick, so it works, but ownership is fragile. The selector scans 17 recipes ×
  100 slots per pick (~80 ticks); acceptable.
- **AutolatheVendStock**: idle paths re-write `slot3`/`slot4` every tick; `slot3` had
  two writers (the D7 bug sat exactly there). The stock worker scans one vending slot
  per tick (≈ 19 min for a full 23-item sweep) — deliberate, cheap, but slow to react.
- **SatTraderTrack dish worker**: runtime `alias` re-binding (`alias dish d1`) inside
  `swap` to hand off between dishes. Works and saves lines, but is the hardest code in
  the repo to reason about; keep as is, documented here.
- **Standalone families** (similar code, different configs): temperature valves
  (`pipe_temp_valve`, `liquid_temp_valve`, `phase_change_temp_valve`), heaters
  (`pipe_heater_below_20c`, `room_heater_below_20c`), methane valves
  (`no_volatiles_valve`, `no_volatiles_no_steam_valve`, `volatiles_purge_valve`). They
  differ in sensor, prefab, name and thresholds, so they stay separate; the index groups
  them so a reader picks the right one.
- **Defensive checks that are fine**: `PrefabHash` checks on the sensor pin
  (`room_*`, `gas_sensor_glass_door_30c`) catch mis-wiring cheaply; keep.

## 7. Tooling review

| Tool | Finding | Action |
| --- | --- | --- |
| `ic10_size_check.py` | correct; limits duplicated with new lint | limits now imported from `ic10_engine.py` |
| `setup_contract_check.py` | checks tokens appear in `Setup.md`, not that pins match | kept; this pushes authors to list non-name tokens (S7) |
| `doc_path_check.py` | only repo-rooted paths in a few docs | now scans all README/Setup/AGENTS docs and doc-relative entries |
| `catalog_check.py` | sound | — |
| `wiki_import.py` | live fetch blocked by Cloudflare; `--help` crashed | help text explains the browser workflow |
| `wiki_xml_import.py` | new; additive merge | — |
| `autolathe_profile_emit.py` | CRLF on Windows; no check mode | LF + `--check` |
| `wiki_recipe_import.py` | live fetch blocked like `wiki_import.py` | debt: add XML input |
| shared code | each tool defines `ROOT`; `_load_json` appears twice | left: tiny, a shared module would add coupling for no gain |

## 8. Tests added

- `tests/test_ic10_engine.py` — branches, timing, alias, batch, hash, analyser rules.
- `tests/test_standalone_scripts.py` — scenarios for 28 of 29 scripts (not
  `vending_machine_export`: needs an item-transport model).
- `tests/test_modular_scripts.py` — Potato actuator cycle and harvest; SatTraderTrack
  master tokens and re-enable, dish sweep in both modes; ingot master sync and status
  passthrough; AutolatheVendStock stock → machine → prep handshake in **both chip
  orders**, and a machine-worker restart mid-run.
- `tests/test_all_scripts.py` — every shipped file lints clean and runs 300 ticks on
  stub devices without halting.

Differential check (one-off, during the audit): for D1, D2 and D3 the original script
from `main` and the fixed script were fed the same 200 random 30-step input sequences
inside the normal range (pressures < 2 MPa; warm start for D3). Device writes were
identical in all 800 runs, so the fixes only change behaviour in the defect cases.

Not covered: `vending_machine_export`, ingot_printer selector/finstd/print/stackers
workers, AutolatheVendStock logistics/feeder/master/guard, PotatoHarvie sensor/master/
guard, SatTraderTrack landing worker — they only get the lint and run checks.

## 9. Per-script results

Status = author's label (unchanged). Static = `check_all` lint/size. Sim = scenario.

| Script | Change in this audit | Static | Sim | In-game test needed |
| --- | --- | --- | --- | --- |
| active_vent_dual_sets | D3 cold-start fix | pass | pass | yes (cold start) |
| air_conditioner_25c | — | pass | pass | no |
| dual_analyzer_furnace_pulse | — | pass | pass | no (S5 optional) |
| gas_sensor_glass_door_30c | — | pass | pass | no |
| hardsuit_helmet_temp_pressure_open | — | pass | pass | no |
| landingpad_volatiles_pressure_valve | — | pass | pass | no |
| large_battery_mean_gas_generator | — | pass | pass | no |
| led_display_hms_clock | — | pass | pass | no |
| liquid_pipe_fill_percent_active_vent | — | pass | pass | no |
| liquid_temp_valve | — | pass | pass | no |
| no_volatiles_no_steam_valve | — | pass | pass | no |
| no_volatiles_valve | — | pass | pass | no |
| phase_change_temp_valve | — | pass | pass | no |
| pipe_furnace_valve_below_20c | — | pass | pass | no (S5 optional) |
| pipe_half_full_active_vent | — | pass | pass | no |
| pipe_heater_below_20c | — | pass | pass | no |
| pipe_pressure_active_vent | — | pass | pass | no |
| pipe_pressure_gas_mixer | — | pass | pass | no |
| pipe_temp_hot_cold_valves | D1 pump fix; README default corrected | pass | pass | **yes** (pump stops ~10.25 MPa) |
| pipe_temp_valve | — | pass | pass | no |
| pipe_volatiles_gas_fuel_generator | — | pass | pass | no |
| purge_valve | — | pass | pass | no |
| room_co2_below_20pct_active_vent | D2; literal `VENT_MODE` | pass | pass | yes (quick sanity) |
| room_cooler_steamless_vent | — | pass | pass | no |
| room_heater_below_20c | — | pass | pass | no |
| room_pressure_active_vent | D2 | pass | pass | yes (quick sanity) |
| vending_machine_export | — | pass | run only | S1 |
| volatiles_purge_active_vent | — | pass | pass | no |
| volatiles_purge_valve | — | pass | pass | no (S4 decision) |
| AutolatheVendStock (7 + 2 generated) | D7 machine worker | pass | handshake, restart | **yes** (full restock cycle) |
| ingot_printer (5) | — | pass | master | no |
| PotatoHarvieTest (4) | D4 actuator | pass | actuator | **yes** (light cycle, harvest) |
| SatTraderTrack (4) | D5 master, D6 dish | pass | master, dish | **yes** (dial 0 sweep; S7 status) |
| templates | literal defines | pass | run only | no |

## 10. In-game test list (priority order)

1. `pipe_temp_hot_cold_valves`: pump stops above ~10.25 MPa and restarts below 9.75 MPa.
2. `AutolatheVendStock`: empty one stocked item; the Autolathe gets the right
   `RecipeHash` before it starts (machine worker `120` → `121`/`122`, prep `154` → `155`).
3. `PotatoHarvieTest`: Grow Light on for the light window, off for dark; Harvie plants
   and harvests.
4. `SatTraderTrack`: dial `0` — the dish sweeps; dial `> 0` unchanged; note
   `setup_guard` status (S7).
5. `active_vent_dual_sets`: start the chip in a cold room with vents running — they stop.
6. Room pressure scripts: normal behaviour around 90–120 kPa unchanged.

## 11. Remaining technical debt

- S1–S9 above.
- `wiki_recipe_import.py` cannot fetch the live wiki; give it the XML path too.
- 16 catalog devices were not in the November export (list in `catalog/README.md`
  workflow); several entries are still `best_guess` (Landingpad outputs, dishes,
  `phase_change_device`).
- Root file `.tmp_vending_export_source.html` is a stray saved wiki page under git;
  nothing references it. Candidate for removal (left for the owner).
- Modular simplifications in §6 are optional and would change in-game wiring.
