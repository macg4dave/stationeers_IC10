# Scripts

Single-chip, paste-ready Stationeers IC10 programs. Each lives in its own folder:

- `scripts/<name>/<name>.ic10` — paste this into the in-game IC chip
- `scripts/<name>/README.md` — pins, settings, status codes, setup

Names follow `<where it lives>_<what it does>`. Old names are listed in
`docs/renames.md`. Multi-chip systems live in `modular scripts/`.

## Conventions every script follows

- **Bands, not single thresholds:** on/off switching has a gap (e.g. on below 20 °C,
  off above 22 °C) so devices do not flicker at the trigger point.
- **Pins checked every loop:** unplug a device and the chip waits instead of halting.
- **Faults switch outputs off:** analyzer `Error` or no reading → the controlled device
  goes to its safe state (see each README for the exact rule).
- **Status on the IC Housing:** the housing's `Setting` shows a number; each README has
  the table (`9` always means "device missing or bad reading").
- **Writes only on change:** devices are read first and only written when different.

**Pins** = devices assigned to `d0..d5` in the IC Housing. **Names** = devices found on
the network by type + exact name, so rename them in-game exactly as the README says.
**Prefab** = every device of that type on the network. **Sim** = a behaviour scenario
in `tests/test_standalone_scripts.py` passes (simulated, not an in-game test).

### Heating and cooling

| Script | What it does | Targeting | Sim |
| --- | --- | --- | --- |
| `room_heater_hold_20c/` | Wall Heater on below 20 °C, off above 22 °C | Pins | yes |
| `pipe_heater_hold_20c/` | Pipe Heater on below 20 °C, off above 22 °C | Pins | yes |
| `air_conditioner_hold_25c/` | Air Conditioner kept on at a 25 °C target (chip in the AC) | db | yes |
| `room_cooler_and_steam_vent/` | Wall Cooler above 30 °C; Active Vent runs while there is no steam | Pins | yes |
| `room_door_open_when_hot/` | Glass Door opens above 30 °C, closes below 28 °C | Pins | yes |
| `furnace_heat_pipe_below_20c/` | Advanced Furnace heats a pipe below 20 °C; pauses input when the furnace passes 100 °C | Pins | yes |
| `furnace_pulse_when_pipes_cold/` | Gas < 30 °C or liquid < 80 °C: valve + furnace `Activate` pulse every 30 s | Pins | yes |

### Valves driven by temperature

| Script | What it does | Targeting | Sim |
| --- | --- | --- | --- |
| `pipe_valves_open_when_cold/` | Valves named `cold`: open below 10 °C, close above 30 °C | Names | yes |
| `liquid_valves_open_when_cold/` | Every Liquid Digital Valve: open below 20 °C, close above 30 °C | Prefab | yes |
| `phase_change_cooling_valve/` | Valves named `cold`: open above 30 °C, close below 28 °C | Names | yes |
| `pipe_sort_hot_cold_with_pump/` | Hot/cold valves by temperature; pump holds ~10 MPa | Pins | yes |

### Pressure and air

| Script | What it does | Targeting | Sim |
| --- | --- | --- | --- |
| `room_vents_hold_pressure/` | Vents named `ROOM_VENT` keep a room between 90 and 120 kPa | Names | yes |
| `room_vents_swap_air_when_hot/` | Above 30 °C vents `IN` blow in and `OUT` pull out; off below 28 °C | Names | yes |
| `pipe_vents_fill_to_10mpa/` | Vents named `PIPE_VENT` fill a pipe to 10 MPa | Names | yes |
| `pipe_vent_fill_to_half/` | Vent fills a pipe to 50–55 kPa | Pins | yes |
| `greenhouse_co2_pressure_vent/` | Vent tops up a room when CO2 < 20 % or pressure < 100 kPa | Pins | yes |
| `liquid_pipe_top_up_vent/` | Vent runs while a liquid pipe is under 50 % full | Pins | yes |
| `gas_mixer_stop_at_10mpa/` | Gas Mixer off above 10 MPa, back on below 9.5 MPa | Pins | yes |

### Methane and fuel

| Script | What it does | Targeting | Sim |
| --- | --- | --- | --- |
| `pipe_valve_open_when_methane/` | Valve open only while the pipe has methane | Pins | yes |
| `pipe_valve_open_when_clean/` | Valve open only with no methane, no steam and > 1 kPa | Pins | yes |
| `pipe_methane_purge_valve/` | Valve purges while O2 < 33 % of the methane | Pins | yes |
| `pipe_methane_purge_vent/` | Vent purges while methane is present and O2 < 33 % | Pins | yes |
| `power_generator_on_methane/` | Gas Fuel Generator runs while its fuel pipe has methane | Pins | yes |
| `landing_pad_methane_unload/` | Unloads ≥ 99.9 % methane from a landing pad; 20 MPa cutoff; override | Pins | yes |
| `liquid_pipe_purge_lever/` | Lever empties a liquid pipe; LED shows the state | Pins | yes |

### Power, suit, display, logistics

| Script | What it does | Targeting | Sim |
| --- | --- | --- | --- |
| `power_generator_on_low_battery/` | Generator on below 30 % average large-battery charge, off above 80 % | Prefab | yes |
| `suit_helmet_auto_open/` | Helmet opens in safe air (4–45 °C, 80–150 kPa), respects a manual close | db + pin | yes |
| `display_clock_from_sun/` | 24 h clock on two LED Displays from a Daylight Sensor | Pins | yes |
| `vending_export_exact_count/` | Exports an exact item count; gives up if the item runs out | Pins | timeout only |
| `trader_dish_auto_land/` | One dish finds a trader, locks on, interrogates, calls it down (**Experimental**, new design) | Pins | yes (simulated dish) |

All scripts except `trader_dish_auto_land` carry the author's **Functional** label from before the 2026-11-21 remake.
They have not yet been re-tested in-game; see `docs/engineering_audit.md` for the list.

## Naming and batch targeting

- Name hashes are exact and case-sensitive: `HASH("cold")` matches `cold`, not `cold_1`
  or `Cold`.
- If a script "can't find" devices: check the data network, then the exact name, then
  the device's `Lock`/`Mode` (`docs/usage/README.md`).

## Adding a script

Copy `scripts/_template/`, follow `docs/ic10_script_checklist.md`, add a scenario to
`tests/test_standalone_scripts.py`, then run `python tools/check_all.py`.
