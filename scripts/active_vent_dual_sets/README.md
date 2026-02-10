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

- Active Vent prefab hash: `HASH("StructureActiveVent")`
- Name hashes (exact match):
   - Intake group: `HASH("IN")`
   - Exhaust group: `HASH("OUT")`

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
- `MODE_INWARD` / `MODE_OUTWARD`: swap values if your vents behave opposite of expected.
- `LOOP_SLEEP_S`: how often to re-apply settings.

## Status

Functional
