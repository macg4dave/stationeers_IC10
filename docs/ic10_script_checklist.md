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

Also add a lightweight in-loop guard before critical `l` reads (especially analyzer reads):

- Example: put `bdns d0 wait_devices` at the top of `main:` before `l ... Temperature`
- Why: this avoids intermittent runtime line faults when a mapped device is temporarily unavailable (power/network reassignment/load timing)

## 4) Units & normalization (most common AI mistake)

- Temperatures are often **Kelvin** → convert: $C = K - 273.15$.
- Some pressures may be **Pa** in some contexts; if you expect kPa, normalize like `room_pressure_active_vent.ic10` (detect large values then divide by 1000).

## 4.5) Device modes: always use the catalog map

Before writing logic for a device with `Mode` (or enum-like fields):

- Open `catalog/devices/<Device>.json` and use its `modeValues` map.
- Add `define` constants for selected mode values in the script.
- Set those modes explicitly in `init` / setup (don’t assume defaults).
- Document chosen mode values in the script README.

Example (`LED_Display`):

- `Mode=0` number, `Mode=8` minutes, `Mode=7` seconds.

If using `Mode=10` (string display):

- Encode characters as ASCII bytes (e.g., `'0'` is `48`).
- Pack bytes as `packed = c0*256 + c1` (up to 6 chars supported by device).
- Quantize values to integers before extracting digits.
- Validate in-game output is digit-only (`00..23`, `00..59`) and not symbols.

## 5) Avoid network spam

Before writing device flags (e.g. `On`, `Open`), prefer:

- read current value
- only `s` when different

Example: `pipe_temp_hot_cold_valves.ic10`.

For display scripts, also avoid re-writing unchanged `Setting` each loop.

## 6) Batch patterns: exact name hashes

If using `lbn/sbn`, remember:

- `HASH("IN")` matches **exact device name** only (not substring)
- Document the required in-game renames in the script `README.md`

### 6.5) Hashing/device-targeting checklist (prevent "not found" issues)

When writing batch network scripts:

- Prefer an authoritative numeric prefab hash from `catalog/devices/<Device>.json` when known.
  - Example: Pipe Digital Valve prefab hash is documented as `-1280984102`.
- Keep name hashes explicit and exact (`HASH("cold")` means exactly `cold`, case-sensitive).
- If using `On` as actuator state, consider writing `Lock=0` before `On` when device behavior can be lock-gated.
- In script README usage steps, include exact rename text users should apply in-game.

Debug order when a batch write appears to do nothing:

1. confirm devices are on the same data network
2. confirm exact in-game name for name hash filters
3. confirm prefab hash value matches intended device type
4. confirm mode/lock prerequisites for that device

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

## 10) Daylight-derived clocks (if no direct clock source)

When deriving a clock from Daylight Sensor angles:

- Document the mapping constants in README (orientation, invert, offset, fine shift).
- Include a calibration order so users can tune quickly:
  1) orientation, 2) invert, 3) phase offset, 4) fine shift.
- Note clearly that this is an angle-derived clock, not a built-in direct clock value.

## 11) Modular features (master + workers)

When a feature is large, stateful, or multi-phase, prefer modular scripts:

- Use one folder with multiple chips:
  - `modular scripts/<feature>/`
  - `<feature>_master.ic10`
  - `<feature>_worker_<task>.ic10` (one concern each)
  - `README.md` with full wiring + shared-memory contract + status codes
- Put orchestration in master only:
  - button/lever edge handling
  - worker enable/disable (`On`)
  - command token writes
- Put task loops in workers only:
  - scan/collect/control logic specific to one concern
- For cross-chip messaging, prefer **Logic Memory** slots (`Setting`) as explicit channels.
- Add status output for each chip via its own `db Setting` and document meanings.
- Validate paste limits for **every** `.ic10` file in the feature folder.

See: `docs/modular_master_worker_pattern.md`.
