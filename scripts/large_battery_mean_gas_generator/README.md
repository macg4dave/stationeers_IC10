# large_battery_mean_gas_generator

Turns a Gas Fuel Generator on when the **mean charge ratio** of **all Large Station Batteries** on the data network is below **30%**.

- ON condition: mean battery `Ratio < 0.30`
- OFF condition: mean battery `Ratio >= 0.30`
- Fail-safe: if no large batteries are found, generator is forced OFF

## Device mapping

- `d0` = Gas Fuel Generator

Batteries are discovered by prefab hash on the same data network (no direct `d1..d5` mapping needed).

## In-game setup

1. Place an IC Housing with this script.
2. Wire the IC Housing to your data network.
3. Set `d0` to your Gas Fuel Generator.
4. Ensure your **Large Station Batteries** are on the same data network.
5. Ensure the Gas Fuel Generator has valid gas supply and pipe setup.

## Tuning constants

In `large_battery_mean_gas_generator.ic10`:

- `LOW_RATIO` (default `0.30`) — threshold for enabling generator.

## Status

- Functional
- Writes `db Setting` as quick status:
  - `0` = generator target OFF
  - `1` = generator target ON
