# Active Vent setup checklist

When a script "sets the vent" but nothing happens, it's usually because one of these properties wasn't set.

## Minimum to see flow / movement

- `On = 1` (enabled)
- `Open = 1` (actually opens the vent so it can flow)
- `Mode` set correctly for your intent
  - Some scripts use constants like `MODE_INWARD`/`MODE_OUTWARD`. Verify which numeric value maps to which direction in your build.

## Common patterns that scripts use

- Some scripts only toggle `On`.
  - In that case you must set `Open = 1` and `Mode` in the device UI first, or nothing will move.
- Many scripts do "safe writes":
  - Read current `Mode`/`Open`/`On` and only write when a value changes (reduces data-network spam).
- Many scripts unlock -> configure -> (optional) lock:
  - `Lock = 0`, then set `Mode`/`Open`/`On`, then optionally `Lock = 1` to prevent in-game overrides.
- When turning a vent OFF, some scripts also set `Open = 0` and `Lock = 0` (fully stop the vent and allow manual control).

## Common accompanying properties (script-dependent)

- `Lock = 1` after configuration (optional, but many scripts do it to prevent manual/in-game overrides)
- Pressure / setpoint properties used by that script, e.g.:
  - `Setting`
  - sometimes `PressureExternal`
  - sometimes `PressureInternal`

For many simple/manual-style controllers, **`Setting` is the main pressure target**.
Leave `PressureExternal` / `PressureInternal` at the vent's mode defaults unless you
specifically want regulator/back-pressure behavior.

### Normal control vs advanced limits

For normal room control, a reliable pattern is:

- set `Mode`
- wait one tick if needed
- set `Setting`
- set `Open = 1`
- set `On = 1`

Only write `PressureExternal` / `PressureInternal` when you deliberately want to customize
the vent's extra pressure limits. Those fields can matter, but they are also an easy way
to accidentally block flow.

### Mode can reset pressures (gotcha)

Some builds reset pressure fields when you change `Mode`.

- If your automation uses `PressureExternal` / `PressureInternal`, set/check them after changing `Mode`.

If you see the values “stick” only briefly (or revert immediately), add a one-tick delay:

- write `Mode`
- wait one tick (`yield`)
- then write `Setting` / `PressureExternal` / `PressureInternal`

## Practical clue from manual testing

If a manually working vent shows values like:

- `PressureExternal = 0`
- `PressureInternal = 50662.5`
- `Setting = 50`

that is a good hint that the vent is happily working with a normal `Setting` target and
its own mode/default pressure behavior. In that case, matching manual behavior in IC10
usually means writing **`Mode` + `Setting` + `Open` + `On`**, not forcing both extra
pressure fields.

## Batch/name-hash gotcha

If using `lbn`/`sbn`, **NameHash is exact**:

- Rename ALL vents in the group to the same exact name (duplicates are fine), e.g. `IN` and `OUT`.

## Batch hash gotcha (important)

IC10 batch writes (`sb` / `sbn`) target devices by **Prefab Hash**, not item hash.

- For Active Vents, use prefab hash `-1129453144` (`StructureActiveVent`) for batch writes.
- Do **not** use item hash `-842048328` for IC10 batch targeting; that can make a script look
  correct while silently failing to hit the vents.

Quick debug order for batch-controlled Active Vents:

1. confirm the vent has real electrical power (`Power = 1`)
2. confirm the vent is on the same data network as the IC
3. confirm the script uses prefab hash `-1129453144`
4. if using `sbn`, confirm the in-game name matches the `HASH("...")` string exactly
5. confirm `Mode` is written before `Setting`
6. if your script also writes `PressureExternal` / `PressureInternal`, confirm those writes happen after `Mode` and are actually needed
