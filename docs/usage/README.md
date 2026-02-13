# Usage playbooks (in-game setup)

These notes exist because AI (and humans!) commonly miss one "tiny" Stationeers setup detail and then everything looks broken.

- If you add a new script and learn a new gotcha, update/add a playbook here.
- Keep these pages short and checklist-y.

## Hash-based targeting sanity checks

When a script uses `lb/sb/lbn/sbn` and appears to "not find" devices:

- Verify all devices are on the same data network.
- Verify hash-based names are exact and case-sensitive (`HASH("cold")` only matches `cold`).
- Verify the script's prefab/type hash matches the intended device.
- Verify device state gates (lock/mode) are satisfied.

## Playbooks

- `modular_wiring_setup.md` — modular chip/link wiring order + end-user setup flow.
- `active_vent.md` — Active Vent required settings.
- `active_liquid_outlet.md` — Active Liquid Outlet required settings.
- `advanced_furnace.md` — Advanced Furnace required settings.
- `daylight_sensor.md` — Daylight Sensor required settings.
- `gas_sensor.md` — Gas Sensor required settings.
- `ic_housing.md` — using `db` for status/debug.
- `led_display.md` — LED Display mode and setup checks.
- `large_satellite_dish.md` — Large Satellite Dish required settings.
- `liquid_digital_valve.md` — Liquid Digital Valve required settings.
- `liquid_pipe_analyzer.md` — Liquid Pipe Analyzer required settings.
- `logic_switch_important_button.md` — Logic Switch (Important Button) required settings.
- `logic_switch_lever.md` — Logic Switch (Lever) required settings.
- `phase_change_device.md` — placeholder device required settings.
- `pipe_analyzer.md` — Pipe Analyzer required settings.
- `pipe_digital_valve.md` — Pipe Digital Valve required settings.
- `satcom.md` — SatCom modular setup checklist (required devices + wiring).
- `solar_panels.md` — Solar panels required settings.
- `wall_cooler.md` — Wall Cooler required settings.
