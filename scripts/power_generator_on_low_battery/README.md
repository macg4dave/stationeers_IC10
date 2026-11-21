# power_generator_on_low_battery

Charges your **Large Station Batteries** with a **Gas Fuel Generator**: on when they run low, off once they are mostly full.

*Previously called `large_battery_mean_gas_generator`.*

## Pins

| Pin | Device |
| --- | --- |
| `d0` | Gas Fuel Generator |

**Network devices:** Every Station Battery (Large) on the same data network is read (average charge). The IC Housing must be on the same data network as the named devices.

## What it does

- Average charge below 30 %: generator ON.
- Above 80 %: generator OFF.
- In between: holds.
- No large batteries found: generator OFF.
- Every pin is also checked inside the main loop: unplug a device and the chip waits instead of halting.

## Settings

Edit the `define` lines at the top of `power_generator_on_low_battery.ic10`.

| Setting | Default | Meaning |
| --- | --- | --- |
| `ON_BELOW` | `0.30` | Start below this charge ratio |
| `OFF_ABOVE` | `0.80` | Stop above this charge ratio |

## Status (IC Housing `Setting`)

| Value | Meaning |
| --- | --- |
| `0` | generator off |
| `1` | generator on |
| `2` | no batteries found |
| `9` | generator missing |

## Setup

1. Build the devices and connect them, the IC Housing and power to one data network.
2. In the IC Housing screen, set each pin as listed above.
3. Paste `power_generator_on_low_battery.ic10` into the chip and run it.
4. Rename the network devices exactly as listed above (Labeller).

## Change history

- 2026-11-21: remade and renamed. **Behaviour change:** it used to switch off again as soon as the average reached 30 %, so the generator flicked on and off around 30 %. It now charges up to 80 %. Set `OFF_ABOVE 0.30` for the old behaviour.

## Status

Functional (author's label from before the remake; re-test in-game).
