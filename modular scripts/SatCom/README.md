# SatCom control system (modular)

Name-first SatCom automation for a Large Satellite Dish using a master + workers.
All active scripts now use exact prefab+name lookup (`lbn`/`sbn`).

Player setup guide: `modular scripts/SatCom/Setup.md`.

## Architecture

- `satcom_master.ic10` - orchestration and status aggregation
- `satcom_setup_guard.ic10` - name/type validation + worker/channel init helper
- `satcom_worker_controls.ic10` - button + dial controls and command publication
- `satcom_worker_discover.ic10` - discover with previous-slot blacklist + min-2
- `satcom_worker_cycle.ic10` - cycle/tune contacts with per-slot blacklist flow
- `satcom_worker_display.ic10` - optional H/V LED display updater
- `satcom_worker_status_led.ic10` - optional status LED color/state updater

## Name contract

Required exact names:

- Buttons: `discover`, `cycle`
- Dials (manual): `dial_h`, `dial_v`
- IC Housing: `discover_worker`, `cycle_worker`, `controls_worker`
- Logic Memory: `cmd_token`, `cmd_type`, `slot0`, `slot1`, `slot2`
- Large Satellite Dish: `dish`
- Optional IC Housing: `status_led_worker`
- Optional LED Displays: `display_h`, `display_v`, `display_status`

Implementation notes:

- Workers and channels are targeted by prefab+name, not chip pin mapping.
- Master/setup guard read IC Housing prefab from `db PrefabHash`, so use one
  housing variant across SatCom ICs.
- Display worker resolves LED display prefab variants by exact name.
- Status LED worker resolves LED display prefab variants by exact name.

## Shared memory contract

Use Logic Memory `Setting` channels:

- `slot0` - first discovered `SignalID`
- `slot1` - second discovered `SignalID`
- `slot2` - third discovered `SignalID`
- `cmd_token` - incrementing command token
- `cmd_type` - command code
- `filter_status` (optional) - mirrors cycle filter verification status
- Empty contact sentinel is `-1` only (`0` is not used as empty).

Command codes:

- `1` = discover (rebuild contact slots)
- `2` = cycle (blacklist current slot, then tune next stored contact)
- `3` = clear (clear slots and unlock dish filter)

Workers execute commands only when `cmd_token` changes.

## Wiring

- Put all SatCom devices on one shared data network.
- No manual `d0..d5` mapping is required for active SatCom scripts.

## Controls

- Controls worker handles all button and dial input.
- Controls worker sets dial ranges on startup (`dial_h Mode=359`, `dial_v Mode=89`).
- Press `discover` to issue command `1`.
- `discover` auto-tunes the first new contact when scan completes.
- Press `cycle` to issue command `2`.
- Press both together to issue command `3`.
- Turn `dial_h` to manually set dish `Horizontal` when discover is not sweeping.
- Turn `dial_v` to manually set dish `Vertical` when discover is not sweeping.
- Contact filter control (`BestContactFilter`) is owned by cycle worker only.
- Optional `display_status` shows color-coded master state and numeric status.

## Known engine behaviors

- `SignalID=-1` means no contact; SatCom scripts treat only `-1` as empty.
- Dish movement or power state changes can reset acquisition; wait for `Idle=1`.
- Dish control/readback requires the dish and ICs on the same data network.

## Status protocol (`db Setting`)

Each chip writes status to its own housing `Setting`.

### Master status (`0-99`)

- `0` = init
- `1` = idle/ready
- `2` = discover worker busy
- `3` = cycle worker busy
- `7` = manual dial control active
- `5` = contacts available
- `6` = no contacts found
- `10` = discover command sent
- `20` = cycle command sent
- `30` = clear command sent
- `44` = controls worker reports missing/wrong controls

### Setup guard status (`90-99`)

- `1` = setup valid
- `91` = missing/wrong `cmd_token`
- `92` = missing/wrong `cmd_type`
- `93` = missing/wrong `discover_worker` housing
- `90` = missing/wrong `controls_worker` housing
- `94` = discover button wrong type/name
- `95` = cycle button wrong type/name
- `96` = missing/wrong `cycle_worker` housing
- `97` = missing/wrong `dish` device
- `98` = missing/wrong `slot0/slot1/slot2` memory
- `99` = missing/wrong `dial_h`/`dial_v` dial controls

### Controls worker status (`340-349`)

- `340` = idle/ready
- `341` = discover command sent
- `342` = cycle command sent
- `343` = clear command sent
- `344` = missing/wrong controls
- `345` = manual dial write applied

### Discover worker status (`100-199`)

- `100` = idle
- `110` = discover start/reset
- `120` = sweeping step / sweep retry
- `130` = complete with 3 new contacts
- `132` = complete with 2 new contacts
- `140` = cleared by clear command

Discover worker never writes `BestContactFilter`.

Discover flow details:

- on `discover`, current `slot0..slot2` are treated as a blacklist for that run
- worker keeps sweeping until it finds at least 2 new contacts
- if a sweep finds fewer than 2 new contacts, it restarts sweeping automatically
- when discover completes, worker emits `cycle` so first new contact is tuned

### Cycle worker status (`200-299`)

- `200` = idle
- `210` = cycling contacts
- `220` = tuned (`BestContactFilter` written)
- `221` = no valid contacts to tune
- `223` = tune attempted but filter readback mismatch
- `230` = filter cleared by clear command
- `233` = clear attempted but filter readback mismatch

Cycle worker owns contact skip/lock flow:

- first `cycle` after discover tunes a stored contact
- next `cycle` blacklists the current slot (`slotN=-1`) and advances to another
- blacklist persists until next `discover` rebuilds `slot0..slot2`
- `discover` also clears `BestContactFilter` so scanning is not locked
- `clear` command resets filter lock (`BestContactFilter=-1`)
- if `filter_status` memory exists, cycle writes `220/221/223/230/233` there

Note on tooling: some editor diagnostics currently misreport `BestContactFilter`
for this prefab. Runtime readback statuses (`220/221/223/230/233`) are the
source of truth for in-game behavior.

### Display worker status (`300-399`)

- `300` = init
- `310` = updating H/V displays

### Status LED worker status (`320-329`)

- `320` = init
- `321` = status LED synced
- `324` = `display_status` missing/wrong type

Status LED color map (`display_status Color`):

- Blue (`0`) = discover/scanning (`2`, `10`)
- Orange (`3`) = cycle/tuning (`3`, `20`)
- Green (`2`) = ready/contacts available (`1`, `5`)
- Yellow (`5`) = no contacts (`6`)
- Red (`4`) = controls/setup issue (`44`)
- White (`6`) = init/manual/clear (`0`, `7`, `30`)
- Purple (`11`) = any unclassified master code

## Limits

- Every `.ic10` stays within 128 lines and 90 chars per line.
- Validate with:
  - `python tools/ic10_size_check.py "modular scripts/SatCom" --ext .ic10`
  - `python tools/setup_contract_check.py`
