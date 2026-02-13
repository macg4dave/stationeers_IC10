# large_satellite_dish_cycle_contacts

**Status:** Functional  
**Category:** Controller

## Purpose

Collects up to 3 unique dish contacts, then cycles through them in order.

- First button press: starts contact collection sweep.
- Later button presses: tune to next stored contact (`BestContactFilter`).
- If no new contact is seen for a while, collection auto-finishes.

## Devices

Required:

- 1x **Large Satellite Dish**
- 1x **Logic Switch (Important Button)**
- 1x **IC10** in an IC Housing (optional `db` status write)

## Device registers

- `d0` = Large Satellite Dish
- `d1` = Logic Switch (Important Button)

## Usage

1. Wire dish + button to IC housing data network.
2. Assign screws: `d0` dish, `d1` important button.
3. Paste `large_satellite_dish_cycle_contacts.ic10` into IC.
4. Press button once to collect contacts.
5. After collection ends, press button to tune next contact in order.

When tuning, the selected `SignalID` is also written to `db Setting` when `db` exists.

## Tuning

- `COLLECT_TIMEOUT` — sweep checks without new contact before ending collect mode.
- Sweep bounds/step: `H_MIN/H_MAX/H_STEP`, `V_MIN/V_MAX/V_STEP`.

## Notes / gotchas

- Contact order is the discovery order during collection.
- Pressing button while collecting stops collection immediately.
- To recollect from scratch, press while collecting to stop, then press again to start fresh collect.
