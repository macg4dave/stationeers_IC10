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
  - `PressureExternal`
  - `PressureInternal`

### Max-flow setpoints (rule of thumb)

If your goal is "move gas as fast as possible" (i.e. don't let the vent's own pressure
limits be the bottleneck), a reliable pattern is:

- Set `Setting` and `PressureExternal` to your pipe max (e.g. `MAX_PIPE_PRESSURE_KPA`)
- Set `PressureInternal` based on `Mode`:
  - **Outward** (pipe → room): set `PressureInternal` to a *low* minimum pipe pressure
    (e.g. 0–10 kPa). Setting it to pipe max can prevent outward flow.
  - **Inward** (room → pipe): set `PressureInternal` to a *high* maximum pipe pressure
    (e.g. `MAX_PIPE_PRESSURE_KPA`).

### Mode can reset pressures (gotcha)

Some builds reset pressure fields when you change `Mode`.

- If your automation uses `PressureExternal` / `PressureInternal`, set/check them after changing `Mode`.

If you see the values “stick” only briefly (or revert immediately), add a one-tick delay:

- write `Mode`
- wait one tick (`yield`)
- then write `Setting` / `PressureExternal` / `PressureInternal`

## Batch/name-hash gotcha

If using `lbn`/`sbn`, **NameHash is exact**:

- Rename ALL vents in the group to the same exact name (duplicates are fine), e.g. `IN` and `OUT`.
