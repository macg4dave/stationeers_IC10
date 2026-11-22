# Engineering audit (2026-11)

Scope: every `.ic10` under `scripts/` and `modular scripts/`, the tooling, the
catalog, templates and docs. Branch `modernisation/engineering-audit`.

**How to read results.** *Static* = lint/size/contract checks. *Simulated* = scenario
passes in `src/engine.rs` (a model of the chip, not the game). *In-game* = only
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
- **Tooling** (one Rust crate since §14): IC10 parser, lint and simulator; catalog,
  setup-contract and doc-path checks; profile emitter; scenarios in `tests/`. Sections
  before §14 name the Python files it replaced.

Inter-script dependencies: none between standalone scripts (each owns its devices;
two scripts both use the name `cold` — `pipe_valves_open_when_cold` and `phase_change_cooling_valve`
— so they must not share a data network). Modular chips depend on each other only
through the documented memory/housing contracts.

## 2. Evidence used

| Fact | Evidence | Confidence |
| --- | --- | --- |
| Prefab hash = signed CRC-32 of prefab name | 14 of 17 hard-coded hashes reproduce exactly (Active Vent, Gas Sensor, Digital Valve, Advanced Furnace, AC, Volume Pump, Gas Generator, Sorter, Harvie, Grow Light, Pipe Heater, Wall Heater, Logic Switch, Logic Dial, Flashing Light, Klaxon) | confirmed |
| `br*` take relative offsets; `b*`/`j` absolute | IC10 instruction set; file `trader_dish_worker_dish.ic10` uses both correctly elsewhere | confirmed |
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
| D1 | `pipe_sort_hot_cold_with_pump` | Pressure > 2000 divided by 1000 ("Pa guess") | pump never stops at the 10 MPa target: unbounded pressure | read kPa directly | low |
| D2 | `room_vents_hold_pressure`, `greenhouse_co2_pressure_vent` | same heuristic | a > 2 MPa room reads as ~2 kPa → intake / vent opens (positive feedback) | read kPa directly | low (normal rooms unchanged) |
| D3 | `room_vents_swap_air_when_hot` | `state` boots at 0 = OFF, so cold start writes nothing | vents left running stay on | start `state` at -1 | low |
| D4 | `farm_potato_grower` actuator | `brlt`/`brge` given labels | jumps ~63 lines into the off-tail: light never on, Harvie never plants/harvests | `blt`/`bge` | low |
| D5 | `trader_dish_auto_land` master | `bnez cur` before `l cur dishw On` | dish worker not re-enabled (dial ≠ 0) or rewritten every tick (dial 0) | add the load | low |
| D6 | `trader_dish_auto_land` dish worker | `beqz prog 2` (absolute) instead of `breqz` | "any trader" mode never sweeps | `breqz prog 2` | medium (needs game test) |
| D7 | `autolathe_restock_vending` machine worker | ready check inverted | machine worker sets `slot3=1` on a *mismatched* recipe; prep skips `RecipeHash`; wrong item built | `bne ... wait_prep` | medium (needs game test) |
| D8 | `autolathe_profile_emit.py` | platform newlines | Windows regen rewrites generated files | LF + `--check` | none |
| D9 | docs / catalog | 8 phantom scripts + 4 phantom features listed; SatCom playbook for deleted feature; bad index entries | users and agents chase files that do not exist | rebuilt indexes, removed playbook, fixed index; checker now catches this | none |

Also: three `define` chains replaced with literals (cannot verify the game resolves
them; literals are equivalent either way).

## 5. Suspected defects and risks

Rows marked Fixed/Changed were addressed in the 2026-11-21 remake (§12).

| ID | Where | Observation | Suggested check / change | Priority |
| --- | --- | --- | --- | --- |
| S1 | `vending_export_exact_count` | waits forever if the item is not stocked; request memory is cleared first, so the request is lost | in-game: request an absent item. Fix would add a timeout | medium — **Fixed 2026-11-21:** 20 s timeout, partial stack returned, status 2. |
| S2 | `autolathe_restock_vending` feeder | writes `RequestHash` every tick until the ingot reaches the sorter; may dispense several stacks in transit | watch a refill in-game; if over-dispensing, request once per `ImportCount` change | medium — **Fixed 2026-11-21:** one request per `REQUEST_GAP_TICKS`. |
| S3 | `gas_mixer_stop_at_10mpa`, `room_door_open_when_hot` | single threshold, no deadband | can chatter at the threshold; add a band if users see flapping | low — **Fixed 2026-11-21:** bands added (and to every other single-threshold script). |
| S4 | `pipe_methane_purge_valve` | on analyzer error it jumps to `wait` and leaves the valve as it was | decide: hold or force closed | low — **Fixed 2026-11-21:** valve forced closed on error. |
| S5 | `furnace_pulse_when_pipes_cold`, `furnace_heat_pipe_below_20c` | rely on Advanced Furnace `Activate` semantics (pulse vs latched) not documented in catalog | confirm in-game which one the furnace expects | low |
| S6 | `air_conditioner_hold_25c` | forces `Mode = 1`; catalog lists Mode 0 Idle / 1 Active (may be a status) | confirm writing Mode is needed | low |
| S7 | `trader_dish_auto_land` setup guard | large dish prefab = `HASH("Large_Satellite_Dish")` (a wiki title) | if the guard always shows `97` with `dish_l` present, the hash is wrong; the guard only reports, workers still run | low — **Moot 2026-11-21:** the multi-chip trader system was replaced (§13). |
| S8 | `liquid_valves_open_when_cold` | prefab `-517628750` not reproducible from a known name | reported Functional; keep | info |
| S9 | 15 standalone scripts | no `bdns` inside the main loop (only in the wait loop) | removing a device mid-run halts the chip; adding the guard is one line per pin | low — **Fixed 2026-11-21:** every standalone script re-checks its pins in the loop. |

## 6. Design review (questionable or unnecessary complexity)

- **farm_potato_grower**: the master increments `cmd_token`, but no worker reads it; master
  and setup guard both force the workers `On`. Four chips and five memories for a job
  that two chips could do. Kept: players have it wired; simplification is optional.
- **autolathe_ingot_printer**: `slot0` has two writers (master and `finstd_worker`). Both copy the
  selector's pick, so it works, but ownership is fragile. The selector scans 17 recipes ×
  100 slots per pick (~80 ticks); acceptable.
- **autolathe_restock_vending**: idle paths re-write `slot3`/`slot4` every tick; `slot3` had
  two writers (the D7 bug sat exactly there). The stock worker scans one vending slot
  per tick (≈ 19 min for a full 23-item sweep) — deliberate, cheap, but slow to react.
- **trader_dish_auto_land dish worker**: runtime `alias` re-binding (`alias dish d1`) inside
  `swap` to hand off between dishes. Works and saves lines, but is the hardest code in
  the repo to reason about; keep as is, documented here.
- **Standalone families** (similar code, different configs): temperature valves
  (`pipe_valves_open_when_cold`, `liquid_valves_open_when_cold`, `phase_change_cooling_valve`), heaters
  (`pipe_heater_hold_20c`, `room_heater_hold_20c`), methane valves
  (`pipe_valve_open_when_methane`, `pipe_valve_open_when_clean`, `pipe_methane_purge_valve`). They
  differ in sensor, prefab, name and thresholds, so they stay separate; the index groups
  them so a reader picks the right one.
- **Defensive checks that are fine**: `PrefabHash` checks on the sensor pin
  (`room_*`, `room_door_open_when_hot`) catch mis-wiring cheaply; keep.

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

Now `tests/engine.rs`, `tests/standalone.rs`, `tests/modular.rs` and `tests/repo.rs`
(ported from Python in §14); file names below are the originals.

- `test_ic10_engine.py` — branches, timing, alias, batch, hash, analyser rules.
- `test_standalone_scripts.py` — scenarios for 28 of 29 scripts (not
  `vending_export_exact_count`: needs an item-transport model).
- `test_modular_scripts.py` — Potato actuator cycle and harvest; trader_dish_auto_land
  master tokens and re-enable, dish sweep in both modes; ingot master sync and status
  passthrough; autolathe_restock_vending stock → machine → prep handshake in **both chip
  orders**, and a machine-worker restart mid-run.
- `test_all_scripts.py` — every shipped file lints clean and runs 300 ticks on
  stub devices without halting.

Differential check (one-off, during the audit): for D1, D2 and D3 the original script
from `main` and the fixed script were fed the same 200 random 30-step input sequences
inside the normal range (pressures < 2 MPa; warm start for D3). Device writes were
identical in all 800 runs, so the fixes only change behaviour in the defect cases.

Not covered: `vending_export_exact_count`, autolathe_ingot_printer selector/finstd/print/stackers
workers, autolathe_restock_vending logistics/feeder/master/guard, PotatoHarvie sensor/master/
guard, trader_dish_auto_land landing worker — they only get the lint and run checks.

## 9. Per-script results

Status = author's label (unchanged: all **Functional**). Static = lint + paste limits.
Sim = behaviour scenario. Every script was remade on 2026-11-21 (§12), so every one
needs an in-game re-test; the column says what to look at first.

| Script | Changes (audit + remake) | Static | Sim | Check first in-game |
| --- | --- | --- | --- | --- |
| room_heater_hold_20c | 20/22 °C band, no-reading → off | pass | pass | heater cycles once across 20–22 °C |
| pipe_heater_hold_20c | 20/22 °C band, empty pipe → off | pass | pass | same |
| air_conditioner_hold_25c | tidy only | pass | pass | AC holds 25 °C (S6) |
| room_cooler_and_steam_vent | cooler 28/30 °C band, steam band | pass | pass | cooler and vent both switch |
| room_door_open_when_hot | 28/30 °C band | pass | pass | door opens > 30, closes < 28 |
| furnace_heat_pipe_below_20c | 20/22 °C band, error → off, subroutine | pass | pass | heating starts and stops (S5) |
| furnace_pulse_when_pipes_cold | CHECK 1/2 no longer need the unused pin | pass | pass | pulse lights the furnace (S5) |
| pipe_valves_open_when_cold | unlock + 10 s re-send | pass | pass | `cold` valves follow temperature |
| liquid_valves_open_when_cold | start-up close, re-send | pass | pass | valves react at all (S8 hash) |
| phase_change_cooling_valve | 28/30 °C band, re-send | pass | pass | `cold` valves open > 30 °C |
| pipe_sort_hot_cold_with_pump | D1; error → pump off | pass | pass | **pump stops at ~10.25 MPa** |
| room_vents_hold_pressure | D2; one fill/exhaust routine | pass | pass | 90–120 kPa cycle |
| room_vents_swap_air_when_hot | D3; 28/30 °C band | pass | pass | **cold start turns vents off** |
| pipe_vents_fill_to_10mpa | error → off, kPa settings | pass | pass | fills and stops at 10 MPa |
| pipe_vent_fill_to_half | tidy | pass | pass | — |
| greenhouse_co2_pressure_vent | D2; CO2 20/22 % band | pass | pass | tops up and stops |
| liquid_pipe_top_up_vent | 50/55 % band, zero-volume guard | pass | pass | vent stops above 55 % |
| gas_mixer_stop_at_10mpa | 9.5/10 MPa band | pass | pass | mixer restarts below 9.5 MPa |
| pipe_valve_open_when_methane | error → closed | pass | pass | — |
| pipe_valve_open_when_clean | error → closed | pass | pass | — |
| pipe_methane_purge_valve | error → closed (S4) | pass | pass | — |
| pipe_methane_purge_vent | error → off, Mode each loop | pass | pass | — |
| power_generator_on_methane | tidy | pass | pass | — |
| landing_pad_methane_unload | 19 MPa re-arm, single status write | pass | pass | cutoff re-arms below 19 MPa |
| liquid_pipe_purge_lever | tidy, status | pass | pass | LED colours |
| power_generator_on_low_battery | **30/80 % band (behaviour change)** | pass | pass | charges to 80 % |
| suit_helmet_auto_open | rewritten, same rules | pass | pass | **manual close is respected** |
| display_clock_from_sun | shared digit routine | pass | pass | digits unchanged |
| vending_export_exact_count | timeout (S1), status | pass | timeout | **normal export still exact** |
| autolathe_restock_vending (7 + 2 generated) | D7; feeder S2; headers | pass | handshake, restart, feeder | **full restock cycle** |
| autolathe_ingot_printer (5) | renamed, headers | pass | master | — |
| farm_potato_grower (4) | D4; headers | pass | actuator | **light cycle, harvest** |
| trader_dish_auto_land (now 1 chip in `scripts/`) | redesigned (§13) | pass | simulated dish, 160 random runs | **everything: see its README** |
| templates | literal defines | pass | run only | — |

## 10. In-game test list (priority order)

1. `pipe_sort_hot_cold_with_pump`: pump stops above ~10.25 MPa and restarts below 9.75 MPa. Since 2026-11-21
   Pipe Heaters follow the cold valve and the pump on `d3` is optional: check both.
2. `autolathe_restock_vending`: empty one stocked item; the right recipe is set before
   printing (machine `120` → `121`/`122`, prep `154` → `155`); the feeder fetches one
   ingot stack at a time (S2).
3. `farm_potato_grower`: Grow Light follows the light window; Harvie plants and harvests.
4. `trader_dish_auto_land`: LED shows degrees falling to ≤ 2 while locking; interrogation
   completes; with no lever (or lever off) the trader is called down; lever on stops it
   (assumptions listed in its README).
5. `suit_helmet_auto_open`: opens in safe air; stays closed after you close it.
6. `vending_export_exact_count`: a normal export is still exact; an absent item gives
   status `2` after ~20 s instead of hanging.
7. `room_vents_swap_air_when_hot`: cold start with vents running — they stop.
8. `power_generator_on_low_battery`: runs from < 30 % to > 80 %.
9. Everything else: one on/off cycle across its band; the housing shows the status
   number from its README.

## 11. Remaining technical debt

- S5, S6, S8 above (need in-game answers); S7 needs confirmation.
- `wiki_recipe_import.py` cannot fetch the live wiki; give it the XML path too.
- 16 catalog devices were not in the November export (list in `catalog/README.md`
  workflow); several entries are still `best_guess` (Landingpad outputs, dishes,
  `phase_change_device`).
- Root file `.tmp_vending_export_source.html` is a stray saved wiki page under git;
  nothing references it. Candidate for removal (left for the owner).
- Modular simplifications in §6 are optional and would change in-game wiring.

## 12. Remake and rename (2026-11-21)

The owner asked for every script to be renamed and refined; all scripts will be
re-tested in-game. What changed:

- **Names:** `<where it lives>_<what it does>`; table in `docs/renames.md`. In-game
  device names, IC Housing names, pins and status codes were not changed.
- **Single-chip scripts (all 29):** hysteresis bands on every on/off threshold; pins
  re-checked in the main loop; faults/no reading drive outputs to their safe state;
  status on the housing `Setting` (except chips that live in a device, where `db` is
  the device); read-before-write throughout; READMEs rewritten to one layout.
- **Behaviour changes worth knowing:** generator charges to 80 % (was: off at 30 %);
  thresholds that used to flip at one value now have a 2 °C / 5 % / 0.5 MPa band;
  `pipe_vents_fill_to_10mpa` and `pipe_methane_purge_*` stop on analyzer error;
  `vending_export_exact_count` gives up after 20 s; the trader guard checks a different
  large-dish hash.
- **Multi-chip systems:** feeder request gap (S2), trader guard hash (S7), header
  comments. The larger simplifications in §6 were left alone: they would change wiring.
- **Tests:** 68 scenarios (8 new for the remake); `check_all` passes.

## 13. Trader dish redesign (2026-11-21)

The owner reported that the trader system never worked. D5/D6/S7 above describe the old
four-chip `SatTraderTrack` design. It was replaced by the single chip
`scripts/trader_dish_auto_land/`.

- **Likely root cause:** the old dish worker (and `docs/usage/large_satellite_dish.md`)
  treated `SignalStrength` as "negative, larger is better", as on the older wiki. Current
  community write-ups (stationeering.substack.com, Mar–Apr 2026: "Signal-Domain Contact
  Acquisition", "Trade I/II") describe it as the angle in degrees to the contact,
  smaller = closer, lock at about 2°. The old sweep therefore moved away from contacts.
  The old design also needed four chips, two Logic Memories and a dish hand-off between
  two dishes.
- **New design:** raster scan, then coordinate descent on `SignalStrength`, with horizontal
  steps scaled by 1/sin(Vertical) and steps allowed over straight up. Then `Activate` to
  interrogate at `MAX_W`, re-lock on drift, 600 s give-up, and `Activate` again to call
  down when the lever is on. Status is `phase*100 + ContactTypeId`.
- **Simulation:** `tests/trader_dish.rs` (then `.py`) uses a fake dish whose `SignalStrength` is
  the true angle to a contact. In a Monte Carlo of 160 random contacts at visibility
  radii 15–40°, 159 were found and called (median about 85 s). The one miss was at a 15°
  radius: a scan-grid gap that more `SCAN_W` closes.
- **Unverified assumptions** (in the script README): SignalStrength units and sign;
  Vertical 0 = straight up; `Activate` after interrogation calls down; `ContactTypeId`
  values; `MAX_W` enough for large/exotic traders.

## 14. Tooling rewritten in Rust (2026-11-21)

The owner asked for all tooling in Rust from now on, without the wiki importers.

- **Removed:** every Python file in the old `tools` folder and in `tests/`, including `wiki_import.py`,
  `wiki_xml_import.py` and `wiki_recipe_import.py`. The catalog is now edited by hand.
- **Replaced by** one crate:
  - `src/engine.rs` (parser, lint, simulator);
  - `src/catalog.rs` (serde schemas, catalog check, profile emitter);
  - `src/repo.rs` (lint every script, setup contracts, doc paths);
  - `src/main.rs` (`ic10 check|lint|hash|emit`);
  - `tests/*.rs`.
- **Merged:**
  - the separate paste-limit checker is gone, because lint already reports
    E020–E022;
  - `check_all.py` became `cargo test` (the static checks run as
    `tests/repo.rs::every_static_check_passes`);
  - each "refined behaviour" test was merged into its script's scenario.
- **Parity:** lint findings, including `--info`, are identical to the Python version
  on all 53 files. All 56 Rust tests pass, and a deliberately broken threshold turns
  the matching scenario red.
- **Small engine fixes:**
  - `sap`/`sna` now take 4 operands, as in-game, and are simulated;
  - `rrN` indirect registers work as targets and as values.
- **Prebuilt crates checked:**
  - `ryex/ic10emu` (Rust IC10 emulator, last pushed 2024-09) was not adopted. Its
    data has `RatioVolatiles` and no `RatioMethane`, and it needs a full prefab
    database for each device, which rules out the fake devices the tests rely on.
  - `tree-sitter-ic10` is only a parser and needs a C build.
  - Generic work uses `serde`, `serde_json`, `regex`, `glob`, `clap` and `crc32fast`.

## 15. Solar tracking restored (2026-11-21)

The old `solar_named_tracking` script was deleted on 2026-06-01 in commit `4eb4776`. The
commit message mentions only satellite scripts, so the deletion looks accidental. It is
replaced by `scripts/solar_panels_track_sun/`:

- same naming contract (`0`/`90`/`180`/`270` = world direction of the data port);
- same maths;
- now also drives Dual, Heavy Dual and 1x5 panels; 1x5 panels are flipped in-game
  (user-confirmed: name `0` = data port at 180), so their `Horizontal` gets +180;
- follows the sun at night;
- re-aims only on change, with a 10 s re-send.

Simulated: four scenarios in `tests/standalone.rs`. Six single-line mutations of the
script each turn at least one of them red.

Confirmed in-game (user, 2026-11-21): 1x5 and Heavy 1x5 panels track the sun. The
Heavy 1x5 hash is -2049226859, read from `PrefabHash`; the guessed name
`StructureSolarPanel1x5Reinforced` (1945473703) matched nothing, and the real prefab
name is still unknown.

In-game checks needed:

- **Facing at midday:** every type faces the sun. Dual panels may need their name
  shifted one group, because the data-port position on Dual is unconfirmed.
- **Night:** at night, panels follow the sun below the horizon and face sunrise at dawn.

## 16. Lights on when dark (2026-11-22)

`scripts/lights_on_when_dark/`: one flat Daylight Sensor; every light on the network by
type is on from `ON_AT` to `OFF_AT` (default 18:00–06:30) in the sun time of
`display_clock_from_sun` (same maths, same `RISE_DEG`/`SHIFT_MIN`). It first switched by
sun height; in-game the lights never came on (status 0 at night, sensor probably on a
wall). Simulated: two scenarios in `tests/standalone.rs`; twelve single-line mutations
each turn one red.

In-game checks needed:

- **Light hashes:** the eight light prefab names are not in the catalog and unconfirmed.
  Only types whose hash is right will switch; read `PrefabHash` for any that don't.
- **Timing:** lights switch when the clock shows `ON_AT` / `OFF_AT`.
- **Flat sensor at night:** whether `Vertical` goes above 90 after sunset is still
  unconfirmed. The clock and the lights both rely on it to tell 21:00 from 15:00.
- **Wall sensor (`WALL 1`):** the conversion is a guess, fitted to one in-game sunrise
  pair (flat H 4 V 81, wall H 22 V 171 → 06:39 vs 06:36). Check over a whole day with
  the clock's `d2` input.

## 17. APC on high battery (2026-11-22)

New script `scripts/power_apc_on_high_battery/`: an Area Power Control on `d0` runs
while the total charge of all Station Batteries is above 70 %, off below 60 %.
Simulated: one scenario in `tests/standalone.rs`; six single-line mutations each turn
it red.

In-game checks needed:

- **Small battery hash:** `StructureBattery` (-400115994) is unconfirmed;
  `StructureBatteryLarge` is the hash `power_generator_on_low_battery` uses.
- **APC `On`:** switching `On` cuts the APC's output.

## 18. Clock from the sun (2026-11-22)

`display_clock_from_sun` turned only the sun's compass direction (`Horizontal`) into
time. In-game at sunrise it showed 00:08–00:12 and barely moved: on a steep sun path
the direction hardly changes all morning. It now uses the sun's angle along its path,
from `Horizontal` and `Vertical` (sunrise 06:00, highest 12:00, set 18:00).

In-game data (user, sunrise, 2026-11-22): flat sensor, top to 0: H 4, V 81 (sun 9° up;
confirms `Vertical` counts from straight up). Wall sensor facing 0 at the same moment:
H 22, V 171, which the `lights_on_when_dark` wall guess (`WALL_TURN 0`) turns into 8°.

The clock errors at lines 68 and 73 were a wiring mix-up: `d0` was the Daylight Sensor
(`PrefabHash` 1076425094 read in-game), not a display.

In-game checks needed: the clock advances evenly through the day and night; `RISE_DEG`
(sensor `Horizontal` at sunrise) stays the same from day to day.
