# PrinterHall (modular)

A name-first modular **printer hall** controller for a shared Autolathe bus.

This first version keeps the architecture general while targeting devices the repo
already documents well: **Autolathes**, a shared **Sorter**, named controls, and an
optional **Proximity Sensor** for idle shutdown.

Player setup guide: `modular scripts/PrinterHall/Setup.md`.

## Architecture

- `printer_hall_master.ic10` - reads named hall controls and publishes commands
- `printer_hall_worker_selector.ic10` - opens exactly one active printer
- `printer_hall_worker_logistics.ic10` - routes shared feed toward printer lane or overflow lane
- `printer_hall_worker_overflow.ic10` - opens the buffer printer for overflow / flush windows
- `printer_hall_worker_idle.ic10` - powers only the active printer and idles the hall on timeout
- `printer_hall_setup_guard.ic10` - validates names and initializes shared channels once

## Scope of this version

- Supports up to **3 named Autolathes** as hall printers.
- Uses a **buffer printer** as overflow storage.
- Assumes one shared feed sorter where:
  - `Output 1` = printer lane
  - `Output 0` = overflow / reject lane
- Does **not** yet inspect printer reagent contents by name; that remains a better fit
  for local single-printer workers like `AutolatheBatch`.

## Device mapping per chip

### Name-targeted chips

These scripts use exact prefab+name lookup and do not require local `d0..d5` wiring:

- `printer_hall_master.ic10`
- `printer_hall_worker_selector.ic10`
- `printer_hall_worker_overflow.ic10`
- `printer_hall_setup_guard.ic10`

### Logistics worker

- `d0` = shared feed sorter
- `db` = logistics status

### Idle worker

- `d0` = hall proximity sensor
- `db` = idle / power status

## Name contract

Required exact names:

- IC Housing: `master`
- IC Housing: `selector_worker`
- IC Housing: `logistics_worker`
- IC Housing: `overflow_worker`
- IC Housing: `idle_worker`
- IC Housing: `setup_guard`
- Logic Memory: `hall_cmd_token`, `hall_cmd_type`, `hall_slot0`, `hall_slot1`, `hall_slot2`
- Logic Switch (Button): `select_1`, `select_2`, `select_3`, `flush_overflow`, `run_batch`
- Logic Switch (Switch): `hall_power`
- Autolathe: `printer_1`, `printer_2`, `printer_3`, `buffer_printer`

## Shared memory contract

- `hall_cmd_token` - incrementing command token written by master
- `hall_cmd_type` - last command code
- `hall_slot0` - active printer index (`0` none, `1..3` printer selection)
- `hall_slot1` - hall power flag (`0` off, `1` on)
- `hall_slot2` - idle timeout in loops (default `300`)

Command codes:

- `1` = select `printer_1`
- `2` = select `printer_2`
- `3` = select `printer_3`
- `5` = flush overflow path
- `6` = ask the selected local batch cell to start its configured run

## Control flow

- Press one of the select buttons to choose the active printer.
- Turn `hall_power` on to let the selected printer open and receive bus traffic.
- The `hall_*` memories are intentionally prefixed so this feature can share a data
  network with local batch cells such as `AutolatheBatch`.
- Press `run_batch` to ask the currently selected local batch cell to start using that
  cell's own `slot0` / `slot1` recipe and count settings.
- The logistics worker releases incoming items to:
  - printer lane while the hall is powered and a printer is selected
  - overflow lane when no printer is selected or during flush windows
- The overflow worker opens `buffer_printer` when:
  - no active printer is selected
  - a flush request is active
- The idle worker powers only the selected printer and shuts it back down after the
  configurable timeout if no player is nearby and the printer is not active.

## Status protocol (`db Setting`)

### Master (`0-99`)

- `0` = boot
- `1` = ready / hall powered
- `11` = hall power switch is off
- `10` = selected printer 1
- `12` = selected printer 2
- `13` = selected printer 3
- `15` = flush command sent
- `16` = run-batch command sent
- `43` = missing `selector_worker`
- `44` = missing `logistics_worker`
- `45` = missing `overflow_worker`
- `46` = missing `idle_worker`

### Selector worker (`100-199`)

- `100` = hall off
- `101` = no active printer selected
- `110` = `printer_1` open
- `111` = `printer_2` open
- `112` = `printer_3` open
- `140` = invalid active index

### Idle worker (`200-299`)

- `200` = hall power off
- `201` = hall powered, no active printer
- `210` = active printer awake
- `221` = active printer timed out / sleeping
- `244` = missing proximity sensor on `d0`

### Logistics worker (`300-399`)

- `300` = routing to overflow / hall idle
- `310` = routing to printer lane
- `311` = ready, waiting for next sorter input
- `320` = flush window routing to overflow
- `340` = missing feed sorter on `d0`

### Overflow worker (`400-499`)

- `400` = buffer closed because hall power is off
- `410` = buffer closed while an active printer owns the hall
- `420` = buffer open because no active printer is selected
- `421` = buffer open for a flush window

### Setup guard (`90-99`)

- `0` = boot
- `1` = setup valid
- `91` = missing `hall_cmd_token`
- `92` = missing `hall_cmd_type`
- `93` = missing required worker/master housing
- `94` = missing required control name/type
- `97` = missing required printer name/type
- `98` = missing `hall_slot0` / `hall_slot1` / `hall_slot2`

## Recovery steps

- If setup guard is not `1`, fix names first.
- If master is `11`, turn on `hall_power`.
- If selector stays at `101`, press one of the select buttons.
- If `run_batch` appears to do nothing, verify the selected printer's local
  `AutolatheBatch` cell is present and hall-gated.
- If logistics is `340`, check the local `d0` feed sorter wiring.
- If idle is `244`, check the local `d0` proximity sensor wiring.
- If items still go to overflow while the hall is active, confirm the sorter path is:
  - `Output 1` -> printer lane
  - `Output 0` -> overflow / reject lane
