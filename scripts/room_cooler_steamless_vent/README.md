# room_cooler_steamless_vent

## Purpose

One **Gas Sensor** drives two actions:

- If room temperature is above a threshold (default **30°C**), turn **ON** a **Wall Cooler**.
- If there is effectively **no steam** in the atmosphere (Gas Sensor `RatioSteam` near zero), turn **ON** an **Active Vent**.

## Devices

Required:

- Gas Sensor
- Wall Cooler
- Active Vent

## Device registers

- `d0` = Gas Sensor
- `d1` = Wall Cooler
- `d2` = Active Vent

## Usage

1. Place a Gas Sensor in the room you want to monitor.
2. Place a Wall Cooler in that room.
3. Place an Active Vent (and set its Mode/pressure behavior as desired in-game).
4. (Recommended) Rename devices to make assignment easy:
   - Gas Sensor: `room_atmo_1`
   - Wall Cooler: `room_atmo_1_cooler`
   - Active Vent: `room_atmo_1_vent`
5. In the IC housing, assign:
   - `d0` = `room_atmo_1`
   - `d1` = `room_atmo_1_cooler`
   - `d2` = `room_atmo_1_vent`
6. Copy/paste `room_cooler_steamless_vent.ic10` into the in-game IC editor and run it.

## Tuning

Edit the constants at the top of `room_cooler_steamless_vent.ic10`:

- `COOL_ON_ABOVE_C` (°C): Wall Cooler forced **ON** when `tempC > COOL_ON_ABOVE_C`.
- `STEAM_RATIO_MIN` (0..1): Active Vent forced **ON** when `RatioSteam < STEAM_RATIO_MIN`.

## Notes

- Gas Sensor `Temperature` is reported in Kelvin; the script converts to Celsius using: $C = K - 273.15$.
- `RatioSteam` is a fraction of the atmosphere. If you prefer “steam present” to mean something else (e.g., at least 1%), increase `STEAM_RATIO_MIN` to `0.01`.
- The script toggles only the devices’ `On` property; it does **not** set vent `Mode`, `Open`, or pressure settings.

## Status

Functional.
