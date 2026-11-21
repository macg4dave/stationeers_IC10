# Script renames (2026-11-21)

Every script was renamed to `<where it lives>_<what it does>` so the name says what it
does. Only file and folder names changed: in-game device names (`HASH("...")`), IC Housing
names, pins (`d0..d5`) and status codes are the same as before.

## Single-chip scripts (`scripts/`)

| Old name | New name | What it does |
|---|---|---|
| `active_vent_dual_sets` | `room_vents_swap_air_when_hot` | Room hot: `IN` vents blow air in, `OUT` vents pull it out |
| `air_conditioner_25c` | `air_conditioner_hold_25c` | Keeps an Air Conditioner on with a 25 C target |
| `dual_analyzer_furnace_pulse` | `furnace_pulse_when_pipes_cold` | Gas or liquid pipe cold: open valve, pulse the furnace |
| `gas_sensor_glass_door_30c` | `room_door_open_when_hot` | Opens a Glass Door when the room is hot |
| `hardsuit_helmet_temp_pressure_open` | `suit_helmet_auto_open` | Opens the helmet when outside air is safe |
| `landingpad_volatiles_pressure_valve` | `landing_pad_methane_unload` | Unloads pure methane from a landing pad, with a pressure cutoff |
| `large_battery_mean_gas_generator` | `power_generator_on_low_battery` | Runs a generator while the large batteries are low |
| `led_display_hms_clock` | `display_clock_from_sun` | 24 h clock on two LED Displays from a Daylight Sensor |
| `liquid_pipe_fill_percent_active_vent` | `liquid_pipe_top_up_vent` | Runs a vent while a liquid pipe is under a fill level |
| `liquid_temp_valve` | `liquid_valves_open_when_cold` | Opens all Liquid Digital Valves when the liquid is cold |
| `no_volatiles_no_steam_valve` | `pipe_valve_open_when_clean` | Opens a valve only with no methane and no steam |
| `no_volatiles_valve` | `pipe_valve_open_when_methane` | Opens a valve only while methane is present |
| `phase_change_temp_valve` | `phase_change_cooling_valve` | Opens `cold` valves when a phase-change device is hot |
| `pipe_furnace_valve_below_20c` | `furnace_heat_pipe_below_20c` | Heats a cold pipe with an Advanced Furnace |
| `pipe_half_full_active_vent` | `pipe_vent_fill_to_half` | Fills a pipe to half of a target pressure |
| `pipe_heater_below_20c` | `pipe_heater_hold_20c` | Pipe Heater keeps a pipe at 20 C |
| `pipe_pressure_active_vent` | `pipe_vents_fill_to_10mpa` | `PIPE_VENT` vents fill a pipe to 10 MPa |
| `pipe_pressure_gas_mixer` | `gas_mixer_stop_at_10mpa` | Stops a Gas Mixer when its output pipe reaches 10 MPa |
| `pipe_temp_hot_cold_valves` | `pipe_sort_hot_cold_with_pump` | Sends gas down a hot or cold valve, pump holds 10 MPa |
| `pipe_temp_valve` | `pipe_valves_open_when_cold` | Opens `cold` valves when a pipe is cold |
| `pipe_volatiles_gas_fuel_generator` | `power_generator_on_methane` | Runs a generator while its fuel pipe has methane |
| `purge_valve` | `liquid_pipe_purge_lever` | Lever empties a liquid pipe through valve, vent and outlet |
| `room_co2_below_20pct_active_vent` | `greenhouse_co2_pressure_vent` | Tops up a greenhouse when CO2 or pressure is low |
| `room_cooler_steamless_vent` | `room_cooler_and_steam_vent` | Wall Cooler when hot; vent runs while there is no steam |
| `room_heater_below_20c` | `room_heater_hold_20c` | Wall Heater keeps a room at 20 C |
| `room_pressure_active_vent` | `room_vents_hold_pressure` | `ROOM_VENT` vents hold a room between 90 and 120 kPa |
| `vending_machine_export` | `vending_export_exact_count` | Exports an exact number of items from a Vending Machine |
| `volatiles_purge_active_vent` | `pipe_methane_purge_vent` | Vents a pipe while it has methane and too little oxygen |
| `volatiles_purge_valve` | `pipe_methane_purge_valve` | Same, through a Pipe Digital Valve |

## Multi-chip systems (`modular scripts/`)

| Old folder | New folder | File prefix (old -> new) | What it does |
|---|---|---|---|
| `AutolatheVendStock` | `autolathe_restock_vending` | `autolathe_vend_stock_` -> `autolathe_restock_` | One Autolathe keeps a Vending Machine stocked |
| `ingot_printer` | `autolathe_ingot_printer` | `ingot_printer_` -> `autolathe_ingot_printer_` | Free Ingots mod: Autolathes print low ingots |
| `PotatoHarvieTest` | `farm_potato_grower` | `potato_harvie_test_` -> `farm_potato_` | Hydroponics + Harvie + Grow Light potato farm |
| `SatTraderTrack` | `trader_dish_auto_land` | `sat_trader_track_` -> `trader_dish_` | Satellite dishes find a trader and land it |

`autolathe_ingot_printer_worker_finstd` is now `autolathe_ingot_printer_worker_final_stacker`.
