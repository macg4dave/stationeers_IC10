# room_co2_below_20pct_active_vent

## Purpose

Read a **Gas Sensor** and open an **Active Vent** when room **CO2** is below **20%**.

The vent opens when either of these is true:

- room CO2 is below **20%**
- room pressure is below **100 kPa**

This means low pressure can still turn the vent on even if CO2 is already above **20%**.

If neither condition is true, the script closes the vent and turns it **OFF**.

## Devices

Required:

- Gas Sensor
- Active Vent

## Device registers

- `d0` = Gas Sensor
- `d1` = Active Vent

## Usage

1. Place a Gas Sensor in the room you want to monitor.
2. Place an Active Vent connected to the atmosphere / pipe setup you want to control.
3. Make sure both devices are powered and on the same data network as the IC Housing.
4. Edit the `VENT_MODE` constant in the script if you want a different airflow direction.
5. You do not need to set the vent **Mode** or **Setting** manually; this script writes both.
6. (Recommended) Rename devices so they are easy to assign:
   - Gas Sensor: `room_co2_sensor_1`
   - Active Vent: `room_co2_vent_1`
7. In the IC Housing, assign:
   - `d0` = `room_co2_sensor_1`
   - `d1` = `room_co2_vent_1`
8. Paste `room_co2_below_20pct_active_vent.ic10` into the in-game IC editor and run it.

## Tuning

Edit the constant at the top of `room_co2_below_20pct_active_vent.ic10`:

- `CO2_OPEN_BELOW_RATIO`: vent is forced **ON/Open** when
  `RatioCarbonDioxide < CO2_OPEN_BELOW_RATIO`
- `MIN_ROOM_PRESSURE_KPA`: the script writes this value to vent `Setting`, and
   low room pressure turns the vent **ON/Open** when `Pressure < MIN_ROOM_PRESSURE_KPA`
- `VENT_MODE`: vent `Mode` written by the script
  - `MODE_OUTWARD` = `0`
  - `MODE_INWARD` = `1`
  - swap these if your build uses the opposite mapping

Ratio notes:

- Gas Sensor `RatioCarbonDioxide` is reported as a value from `0.0` to `1.0`.
- `0.20` means **20% CO2**.
- The threshold is strict: exactly `0.20` keeps the vent **OFF/closed**.

Pressure notes:

- The script normalizes Gas Sensor `Pressure` to kPa before comparing.
- If the sensor reports Pa, values above `2000` are divided by `1000`.
- With the default setting, pressure below **100 kPa** forces the vent **ON/open**.

## In-game setup notes

- See `docs/usage/gas_sensor.md` for Gas Sensor reading gotchas.
- See `docs/usage/active_vent.md` for Active Vent setup notes.
- The script clears vent `Lock` before applying changes.
- This script writes vent `Mode`, `Setting`, `Open`, and `On`.
- For airflow to happen, the vent still needs power and a valid pipe/room setup.
- If the vent moves gas the wrong way, change `VENT_MODE` in the script.

## Status

Functional.
