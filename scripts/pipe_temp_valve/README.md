# pipe_temp_valve

Controls a pipe digital valve based on the pipe temperature measured by a Pipe Analyzer.

## In-game setup

1. Place and connect:
   - a **Pipe Analyzer** on the pipe network you want to monitor
   - a **Pipe Digital Valve** you want to open/close
2. (Recommended) Rename the in-game devices so they’re easy to pick when wiring/assigning:
   - rename the Pipe Analyzer to `read_pipe_temp_1`
   - rename the Pipe Digital Valve to `read_pipe_temp_1_valve`
3. Assign IC device registers:
   - `d0` = Pipe Analyzer (`read_pipe_temp_1`)
   - `d1` = Pipe Digital Valve (`read_pipe_temp_1_valve`)
4. Copy/paste `pipe_temp_valve.ic10` into the in-game IC chip and run it.

## Behavior

- Reads `d0 Temperature` (Kelvin) and converts to Celsius by subtracting `273.15`.
- Turns the valve **ON** when temperature is below **10°C**.
- Turns the valve **OFF** when temperature is above **30°C**.
- Between 10°C and 30°C it leaves the valve state unchanged.

## Customization

Edit `pipe_temp_valve.ic10`:

- Change the `10` and `30` threshold constants.
- Change `d0` / `d1` mapping if you prefer different device register assignments.
