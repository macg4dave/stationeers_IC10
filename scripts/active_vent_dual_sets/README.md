# active_vent_dual_sets

**Purpose:**
Sets one group of Active Vents to intake (inward) and another group to exhaust (outward)
based on exact device name matches using `HASH()` + `sbn`, gated by room temperature.

## Devices

- **Required:** Gas Sensor (room), Active Vents on the same data network as the IC
- **Optional:** None

## Device registers

- `d0` = Gas Sensor (room)

## Batch / hashes

- Active Vent prefab hash: `HASH("StructureActiveVent")` = `-1129453144`
- Intake group name hash (exact match): `HASH("IN")`
- Exhaust group name hash (exact match): `HASH("OUT")`

> **Important:** IC10 batch writes use the device **Prefab Hash**, not item hash.
> For Active Vents, use `-1129453144` (`StructureActiveVent`), not item hash `-842048328`.
> **Important:** `sbn` matches **exact** name hashes only. It does **not** match substrings.
> To target a group, rename **every** intake vent to the exact same name (e.g. `IN`), and
> **every** exhaust vent to another exact name (e.g. `OUT`). If you want different words,
> update the `IN_NAME_HASH` / `OUT_NAME_HASH` defines in the script.

## Usage

1. Rename all intake vents to `IN` and all exhaust vents to `OUT` (or update the hash
   constants in the script to match your chosen names).
2. Connect a Gas Sensor to the room you want to control and assign it to `d0`.
3. Paste `active_vent_dual_sets.ic10` into the IC and connect it to the same data network
   as the vents.
4. Power the IC. The vents turn on when temperature is $\ge 30\,^{\circ}\mathrm{C}$ and
   turn off when it drops below $30\,^{\circ}\mathrm{C}$.

## Tuning

- `TEMP_THRESHOLD_C`: temperature threshold in °C.
- `MODE_OUTWARD` / `MODE_INWARD`: swap values if your vents behave opposite of expected.
- `INTAKE_SETTING_KPA`: intake-group vent `Setting` target while ON.
- `EXHAUST_SETTING_KPA`: exhaust-group vent `Setting` target while ON.
- `LOOP_SLEEP_S`: polling interval for temperature (and minimum time between state changes).
- `REAPPLY_TICKS`: while vents are ON, how often to re-apply vent settings (reduces spam vs. every loop).

## Notes

- Repo guidance now treats **`Setting` as the main pressure target** for most Active Vent
  controllers.
- `PressureExternal` / `PressureInternal` are advanced limit fields; overriding them can
  accidentally block flow if you do not specifically want regulator/back-pressure behavior.
- If you are building a simple/manual-style vent controller, prefer:
  - set `Mode`
  - wait one tick (`yield`)
  - set `Setting`
  - set `Open = 1`
  - set `On = 1`
- This script now follows that pattern:
  - intake group writes `Mode = Outward`, `Setting = INTAKE_SETTING_KPA`, `Open = 1`, `On = 1`
  - exhaust group writes `Mode = Inward`, `Setting = EXHAUST_SETTING_KPA`, `Open = 1`, `On = 1`
- If you inspect a manually working vent and see values like `PressureExternal = 0`,
  `PressureInternal = 50662.5`, `Setting = 50`, that is a good hint that `Setting` is the
  useful control target while the extra pressure-limit fields are best left alone.

## Status

Functional
