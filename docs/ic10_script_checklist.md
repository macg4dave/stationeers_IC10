# IC10 script checklist (paste-ready)

Use this when creating or editing **paste-into-game** IC10 scripts in `scripts/`.

## 1) Create the script folder + files

- Create `scripts/<script_name>/` (short `snake_case`)
- Add:
  - `scripts/<script_name>/<script_name>.ic10` (paste-ready)
  - `scripts/<script_name>/README.md` (player-facing setup)

## 2) IC10 file header (required)

At the top of `<script_name>.ic10`, include a compact header:

- Script name
- Category + Status
- Purpose (1–3 lines)
- Device registers mapping (`d0..d5`, `db` if used)
- Notes that prevent common failures (units, required in-game settings)

Example patterns are in:

- `scripts/pipe_temp_hot_cold_valves/pipe_temp_hot_cold_valves.ic10`
- `scripts/room_pressure_active_vent/room_pressure_active_vent.ic10`

## 3) Gate device availability (don’t assume d0 exists yet)

Use a `wait:` / `wait_devices:` loop with `yield` + `bdns` for every required device.

## 4) Units & normalization (most common AI mistake)

- Temperatures are often **Kelvin** → convert: $C = K - 273.15$.
- Some pressures may be **Pa** in some contexts; if you expect kPa, normalize like `room_pressure_active_vent.ic10` (detect large values then divide by 1000).

## 5) Avoid network spam

Before writing device flags (e.g. `On`, `Open`), prefer:

- read current value
- only `s` when different

Example: `pipe_temp_hot_cold_valves.ic10`.

## 6) Batch patterns: exact name hashes

If using `lbn/sbn`, remember:

- `HASH("IN")` matches **exact device name** only (not substring)
- Document the required in-game renames in the script `README.md`

Example: `scripts/active_vent_dual_sets/active_vent_dual_sets.ic10`.

## 7) Player-facing README (required)

In `scripts/<script_name>/README.md` include:

- Purpose (plain language)
- Required devices + what goes in `d0..d5`
- In-game settings prerequisites (link `docs/usage/<device>.md` when applicable)
  - Example: Active Vents often require **both** `On=1` **and** `Open=1`, plus correct `Mode`/pressure settings (`docs/usage/active_vent.md`)
- Tuning constants + units
- Status

## 8) Validate paste limits before “shipping”

IC chip limits: **128 lines** and **90 chars/line** (including comments and blanks).

Run the checker after editing scripts:

- `python tools/ic10_size_check.py scripts/ --ext .ic10`

## 9) Update the catalog / playbooks when you learn something

- If you hit a new “device does nothing” gotcha, add it to `docs/usage/` (keep it checklist-y).
- If you need authoritative I/O names, import/update the device in `catalog/` via `tools/wiki_import.py`.
