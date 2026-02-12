# purge_valve

## Purpose

Acts like a **purge valve**:

- If the **lever is ON** and the **liquid pipe contains any liquid**, it:
  - opens a **Liquid Digital Valve**
  - turns on an **Active Vent**
  - turns on an **Active Liquid Outlet**
- Otherwise it turns all three **OFF**.

This is useful for “dump to waste” / purge lines that you only want active on demand.

Detection note: this script treats **any non-trivial pipe pressure** as “something present”,
so it will purge **gas and/or liquid**.

## Devices

Required:

- Logic Switch (Lever)
- Liquid Pipe Analyzer (Kit)
- Liquid Digital Valve
- Active Vent
- Active Liquid Outlet
- LED (from Kit (Lights))

## Device registers

- `d0` = Logic Switch (Lever)
- `d1` = Liquid Pipe Analyzer
- `d2` = Liquid Digital Valve
- `d3` = Active Vent
- `d4` = Active Liquid Outlet
- `d5` = LED

Note: this script reads the lever's `Open` state (the data network property for levers).

## Usage

1. Place and wire the devices so the analyzer is reading the pipe you care about, and the valve/vent/outlet are connected to the purge path.
2. Configure the **Active Vent** and **Active Liquid Outlet** modes/settings in their UIs (this script only toggles `On`).
3. In the IC housing, assign devices to `d0..d5` as above.
4. Paste `purge_valve.ic10` into the IC.
5. Flip the lever ON to enable purging; flip it OFF to stop.

### LED status colors

- **Yellow**: pipe has contents, lever **OFF**
- **Red**: pipe has contents, lever **ON** (purging enabled)
- **Green**: lever **ON**, pipe empty
- **Off**: lever **OFF**, pipe empty

## Tuning

Inside `purge_valve.ic10`:

- `MIN_PRESSURE_KPA` — minimum analyzer `Pressure` (kPa) required to treat the pipe as “has anything”.
  - Default: `0.001`
  - If you see false triggers due to noise, increase it slightly.

## Status

Functional
