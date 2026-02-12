# LED Display setup checklist

## What scripts usually write

- `On`
- `Mode`
- `Setting`
- (optional) `Color`

## Minimum to work

- Connected to the same data network as the IC Housing
- Assigned to the correct `d0..d5` pin
- Powered (check `Power` output if debugging)

## Common gotchas

- **Mode matters**: if a script expects unit formatting, set `Mode` explicitly.
- Don’t rely on default mode; some devices keep prior mode state.
- Typical clock split (3 displays):
  - Hours: `Mode=0` (number)
  - Minutes: `Mode=8` (minutes)
  - Seconds: `Mode=7` (seconds)
- `Mode=10` expects packed-string numeric encoding, not plain text.

## `Mode=10` (String) checklist for clock-style output

When using string mode for `HH` / `MM` fields, these are the common failure points:

- Use `Mode=10` explicitly in script init (and optionally re-assert if users change mode in-game).
- Pack digits as ASCII bytes, not raw numbers:
  - `tens_char = tens + 48`
  - `ones_char = ones + 48`
  - `packed = tens_char * 256 + ones_char`
- Ensure values are whole integers before digit extraction (avoid float leakage).
- Prefer digit extraction via integer decomposition:
  - `tens = value / 10`
  - `ones = value - tens*10`
- Keep expected ranges tight before packing:
  - Hours: `0..23`
  - Minutes/Seconds: `0..59`

Symptoms of bad packing:

- Output like `2I`, `3e`, `0[` usually means packed bytes are not digit ASCII (`0`-`9`).
- Correct output should always be two digits (`00`-`23`, `00`-`59`).

## Full `Mode` reference (LED Display)

Use these values when writing `s <display> Mode <value>`.

- `0` — **Normal number display**
  - `Setting` is shown directly as a number.
  - Very small values (< `1.000E-07`) display as `0`.

- `1` — **Percentage number display**
  - `Setting` range `0.0..1.0` maps to `0%..100%`.
  - Values outside that range continue scaling (e.g., `10` → `1000%`).

- `2` — **Power display**
  - Adds `W` suffix.
  - Applies metric prefixes as needed (e.g., `kW`).

- `3` — **Kelvin display**
  - Adds `K` suffix.
  - Applies metric prefixes as needed (e.g., `kK`).

- `4` — **Celsius display**
  - Adds `°C` suffix.
  - Applies metric prefixes as needed (e.g., `k°C`).

- `5` — **Meters display**
  - Adds `m` suffix.
  - Applies metric prefixes as needed (e.g., `km`).

- `6` — **Credits display**
  - Adds `€` suffix.
  - Applies metric prefixes as needed (e.g., `k€`).

- `7` — **Seconds display**
  - Adds `sec` suffix.
  - Does not apply metric prefix scaling for `Setting >= 1000`.

- `8` — **Minutes display**
  - Adds `min` suffix.
  - Does not apply metric prefix scaling for `Setting >= 1000`.

- `9` — **Days display**
  - Adds `days` suffix.
  - Does not apply metric prefix scaling for `Setting >= 1000`.
  - Still displays `days` even when value is `1`.

- `10` — **String display**
  - Treats `Setting` as octet-packed ASCII (up to 6 chars).
  - Example from catalog: `$414243444546` displays `ABCDEF`.

- `11` — **Fahrenheit display**
  - Adds `°F` suffix.
  - Applies metric prefixes as needed (e.g., `k°F`).

- `12` — **Litres display**
  - Adds `L` suffix.
  - Applies metric prefixes as needed (e.g., `kL`).

- `13` — **Mol display**
  - Adds `mol` suffix.
  - Applies metric prefixes as needed (e.g., `kmol`).

- `14` — **Pascal display**
  - Adds `Pa` suffix.
  - Applies metric prefixes as needed (e.g., `kPa`).
