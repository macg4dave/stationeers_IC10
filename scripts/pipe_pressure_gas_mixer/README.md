# pipe_pressure_gas_mixer

Turns a **Gas Mixer** on while a connected **Pipe Analyzer** reports **10 MPa or less** of pressure, and turns it off above that limit.

- ON condition: `Pressure <= MAX_PRESSURE_KPA`
- OFF condition: `Pressure > MAX_PRESSURE_KPA`
- Fail-safe: if the Pipe Analyzer reports `Error != 0`, the mixer is forced OFF
- Analyzer startup: if the Pipe Analyzer is toggled OFF, the script turns it ON and waits a tick before reading

## Device mapping

- `d0` = Pipe Analyzer
- `d1` = Gas Mixer

## In-game setup

1. Place an IC Housing with this script.
2. Wire the IC Housing, Pipe Analyzer, and Gas Mixer to the same data network.
3. Set `d0` to the Pipe Analyzer that watches the gas line feeding your mixer.
4. Set `d1` to the Gas Mixer you want to control.
5. Ensure the Pipe Analyzer is powered and working.
6. Ensure the Gas Mixer is connected to the pipe network you want to regulate.

If you still get a runtime line error, double-check that:

- `d0` is really a **Pipe Analyzer**
- `d1` is really a **Gas Mixer**
- both devices are on the same data network as the IC Housing

## Tuning constants

In `pipe_pressure_gas_mixer.ic10`:

- `MAX_PRESSURE_KPA` (default `10000`) — maximum pipe pressure in **kPa** allowed before the Gas Mixer is turned OFF

Reminder: **10 MPa = 10000 kPa**.

## Status

- Functional
- Writes `db Setting` as quick status:
  - `0` = mixer target OFF
  - `1` = mixer target ON
  - `3` = analyzer fault/error forced OFF
  - `4` = analyzer was OFF; script turned it ON and is waiting
