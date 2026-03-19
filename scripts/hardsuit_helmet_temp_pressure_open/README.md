# hardsuit_helmet_temp_pressure_open

## Purpose

Automatically open the **Hardsuit Helmet** visor when the **outside atmosphere around the suit** is both:

- between **4°C** and **45°C**
- between **80 kPa** and **150 kPa**

If either condition is not met, the script closes the helmet.

## Devices

Required:

- 1× Hardsuit with processor slot
- 1× Hardsuit Helmet
- 1× IC10 chip installed in the Hardsuit processor slot

## Device registers

When this script runs inside a **Hardsuit** IC10 chip:

- `db` = Hardsuit interface
- `d0` = attached Hardsuit Helmet interface

You do **not** manually wire `db` or `d0`; the suit provides them automatically.

## Usage

1. Wear a Hardsuit and attach a Hardsuit Helmet.
2. Insert an IC10 chip into the Hardsuit processor slot.
3. Paste `hardsuit_helmet_temp_pressure_open.ic10` into that chip.
4. Run the script.

The visor will:

- **open** only when external `Temperature` is between `4°C` and `45°C`
- **open** only when external `Pressure` is between `80 kPa` and `150 kPa`
- **close** otherwise
- **close again** if it was open and either reading later drops below the threshold

## Tuning

Edit the constants at the top of `hardsuit_helmet_temp_pressure_open.ic10`:

- `TEMP_OPEN_AT_OR_ABOVE_C` — minimum external temperature in **°C** required to open
- `TEMP_OPEN_AT_OR_BELOW_C` — maximum external temperature in **°C** allowed to stay open
- `PRESSURE_OPEN_AT_OR_ABOVE_KPA` — minimum external pressure in **kPa** required to open
- `PRESSURE_OPEN_AT_OR_BELOW_KPA` — maximum external pressure in **kPa** allowed to stay open

## Notes

- Hardsuit `TemperatureExternal` is reported in Kelvin, so the script converts it using:
  $C = K - 273.15$
- Hardsuit `PressureExternal` is compared as **kPa**.
- The script reevaluates temperature and pressure every cycle, so it will reopen or re-close
  the helmet as conditions move inside or outside the safe range.
- The script writes `Lock = 0` and then updates `Open` every cycle.
- If the helmet is missing or detached, the script waits until `d0` is available again.

## Status

Functional.
