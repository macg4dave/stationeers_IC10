# [Feature] setup (name-based auto setup)

Use this page to set up [Feature] with a fixed naming contract.
The system auto-discovers controls by exact names and item type.

## Build list

- Nx IC Housing + IC Chip
  - [Feature] Master
  - [Feature] Worker A
  - [Feature] Worker B
  - [Feature] Setup Guard (recommended)
  - [Feature] Worker C (optional)
- Nx Logic Memory
  - `cmd_token`
  - `cmd_type`
  - `slot0`
  - `slot1`
  - `slot2`
- Nx controls
  - [Control A]
  - [Control B]
- Nx feature devices
  - [Device 1]

## Name contract

Set these exact names (case-sensitive):

- Control Type A: `[control_a_name]`
- Control Type B: `[control_b_name]`
- IC Housing: `[master_housing_name]`
- IC Housing: `[setup_guard_name]` (recommended)
- IC Housing: `[worker_a_housing_name]`
- IC Housing: `[worker_b_housing_name]`
- IC Housing: `[worker_c_housing_name]` (optional)
- Logic Memory: `slot0`
- Logic Memory: `slot1`
- Logic Memory: `slot2`
- Logic Memory: `cmd_token`
- Logic Memory: `cmd_type`

## Setup steps

1. Put all devices on one data network.
2. Paste scripts:
   - `modular scripts/<feature>/<feature>_master.ic10`
   - `modular scripts/<feature>/<feature>_worker_<task_a>.ic10`
   - `modular scripts/<feature>/<feature>_worker_<task_b>.ic10`
   - `modular scripts/<feature>/<feature>_setup_guard.ic10` (recommended)
   - `modular scripts/<feature>/<feature>_worker_<task_c>.ic10` (optional)
3. Apply required names from **Name contract**.
4. Ensure shared channels (`slot0..slot2`, `cmd_token`, `cmd_type`) are wired as required.
5. Power devices and wait a few ticks.
6. Run [Control A], then [Control B].

## Controls

- [Control A]: [What it does for players].
- [Control B]: [What it does for players].
- [Optional combo control]: [What it does for players].

## Setup guard status (`db Setting`)

- `0` boot
- `10` one-time init complete
- `1` setup valid
- `94` control A wrong type
- `95` control B wrong type
- `97` missing/wrong critical feature device (recommended reserve)
- `98` missing/wrong required shared memory channels (recommended reserve)

## Runtime debug snapshot (required for issue reports)

When debugging, capture these values in one screenshot/note:

- `master` (`db Setting`)
- `setup_guard` (`db Setting`)
- each worker chip `db Setting`
- `cmd_token` and `cmd_type` memory values

Quick interpretation:

- if `cmd_token` increments when controls are pressed, master/input path is working
- if workers stay idle while token increments, debug worker prerequisites next
