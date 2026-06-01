# pipe_volatiles_gas_fuel_generator

Turns a **Gas Fuel Generator** on when a connected **Pipe Analyzer** reports **any Methane** in the pipe.

- ON condition: `RatioMethane > EPS`
- OFF condition: `RatioMethane <= EPS`
- Fail-safe: if the Pipe Analyzer reports `Error != 0`, generator is forced OFF
- Analyzer startup: if the Pipe Analyzer is toggled OFF, the script turns it ON and waits a tick before reading

## Device mapping

- `d0` = Pipe Analyzer
- `d1` = Gas Fuel Generator

## In-game setup

1. Place an IC Housing with this script.
2. Wire the IC Housing, Pipe Analyzer, and Gas Fuel Generator to the same data network.
3. Set `d0` to the Pipe Analyzer that watches the generator fuel line.
4. Set `d1` to the Gas Fuel Generator.
5. Ensure the Pipe Analyzer is powered and working.
6. Ensure the Gas Fuel Generator has valid gas supply and the usual room requirements to run.

If you still get a runtime line error, double-check that:

- `d0` is really a **Pipe Analyzer**
- `d1` is really a **Gas Fuel Generator**
- both devices are on the same data network as the IC Housing

## Tuning constants

In `pipe_volatiles_gas_fuel_generator.ic10`:

- `EPS` (default `0.000001`) — values above this count as “Methane present”

Increase `EPS` if you want to ignore tiny floating-point noise near zero.

## Status

- Functional
- Writes `db Setting` as quick status:
  - `0` = generator target OFF
  - `1` = generator target ON
  - `3` = analyzer fault/error forced OFF
  - `4` = analyzer was OFF; script turned it ON and is waiting
