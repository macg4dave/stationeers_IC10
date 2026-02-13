# <Feature> setup (player checklist)

Use this page to get <Feature> working in game. You do not need to read script
logic to follow it.

## Build list

- Nx IC Housing + IC Chip
  - <Feature> Master
  - <Feature> Worker A
  - <Feature> Worker B
- Nx Logic Memory
  - `cmd_token`
  - `cmd_type`
  - `data0`
  - `data1`
- Nx controls
  - <Control 1>
  - <Control 2>
- Nx feature devices
  - <Device 1>

## Setup steps

1. Put all devices on the same data network.
2. Paste scripts into the correct chips:
   - `modular scripts/<feature>/<feature>_master.ic10`
   - `modular scripts/<feature>/<feature>_worker_<task_a>.ic10`
   - `modular scripts/<feature>/<feature>_worker_<task_b>.ic10`
3. Wire each chip exactly as shown below.
4. Power everything and wait a few ticks.
5. Run the first action for this feature.

## Wiring map

Wire shared links first (`d0`, `d1`, `d2`...), then controls and feature devices.

### Master chip (`<feature>_master.ic10`)

- `d0` = Worker A IC Housing
- `d1` = Worker B IC Housing
- `d2` = Logic Memory `cmd_token`
- `d3` = Logic Memory `cmd_type`
- `d4` = <Control 1>
- `d5` = <Control 2>

### Worker A (`<feature>_worker_<task_a>.ic10`)

- `d0` = Logic Memory `data0`
- `d1` = Logic Memory `data1`
- `d2` = Logic Memory `cmd_token`
- `d3` = Logic Memory `cmd_type`
- `d4` = <Feature Device 1>
- `d5` = <Feature Device 2>

### Worker B (`<feature>_worker_<task_b>.ic10`)

- `d0` = Logic Memory `data0`
- `d1` = Logic Memory `data1`
- `d2` = Logic Memory `cmd_token`
- `d3` = Logic Memory `cmd_type`
- `d4` = <Feature Device 1>
- `d5` = <Feature Device 2>

## Controls

- <Control 1>: <What it does for players>.
- <Control 2>: <What it does for players>.
- <Optional combo control>: <What it does for players>.
