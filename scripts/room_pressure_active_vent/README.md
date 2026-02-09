# room_pressure_active_vent

**Purpose:** Reads **room pressure** from a **Gas Sensor** and drives an **Active Vent**:

- If room pressure is **below 100 kPa** → vent **pressurizes the room** (pipe → room).
- If room pressure is **above 120 kPa** → vent **depressurizes the room** (room → pipe).
- Between 100–120 kPa it turns the vent **OFF** (hysteresis band).

## Devices

Required:

- **Gas Sensor** (placed in the room)
- **Active Vent** (connected to your pipe network, powered)

## Device registers

- `d0` = Gas Sensor
- `d1` = Active Vent

## Behavior / notes

- The script reads `Pressure` (kPa) from the Gas Sensor.
- Active Vent **Mode values can be confusing** (and may differ from older notes).
  This repo already uses `Mode = 1` as “Outward” in `volatiles_purge_active_vent`, so this script follows the same convention:
  - `Mode = 1` → **BLOW** (pipe → room)
  - `Mode = 0` → **SUCK** (room → pipe)

- **Important:** changing `Mode` resets the vent’s `PressureExternal` / `PressureInternal` to defaults.
  This script therefore sets:
  - `PressureExternal` to the target (100 or 120 kPa depending on direction)
  - `PressureInternal` to a safe limit for the pipe side
    - when sucking room air into pipe: it sets a **high max** (`PIPE_MAX_KPA`) so the vent isn't blocked by a pressurized pipe network

- **Workaround:** some players report Active Vents can ignore/overwrite pressure limits if you write them in the same tick as a `Mode` change.
  This script waits **1 tick** after changing `Mode` before writing the pressure limits.

- While the vent is being commanded ON, the script sets `Lock = 1` to reduce accidental manual toggles; it unlocks (`Lock = 0`) when turning the vent off.

### Tuning

In `room_pressure_active_vent.ic10`:

- `LOW_KPA` (default `100`)
- `HIGH_KPA` (default `120`)
- `LOOP_TICKS` (default `10` ticks ≈ 5 seconds, assuming ~2 ticks/sec)

If the vent seems to run in the wrong direction in your world, swap the constants in the script:

- `MODE_BLOW`
- `MODE_SUCK`

## Setup

1. Place a Gas Sensor in the room you want to control.
2. Place an Active Vent connected to the pipe network you want to pump from/to.
3. In the IC Housing set:
   - `d0` → the Gas Sensor
   - `d1` → the Active Vent
4. Paste `room_pressure_active_vent.ic10` into the chip and run it.

## Status

Functional.
