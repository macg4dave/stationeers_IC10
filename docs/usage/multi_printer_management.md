# Multi-printer management checklist

Use this when building a **printer hall** with several machines sharing one ingot bus.

This playbook captures reusable ideas from public Stationeers printer-management builds
without depending on one exact workshop layout.

## Core pattern

A practical hall-level split is:

- **one active printer at a time**
  - route ingots only to the selected machine
  - avoid half-filling several printers at once
- **one overflow / storage path**
  - send surplus ingots somewhere predictable
  - a dedicated buffer printer or storage device works well
- **one hall controller**
  - decides which printer is active
  - powers down or closes inactive machines

## Routing checklist

- Use **short exact names** for sorters, splitters, and key machines.
- Prefer `lbn` / `sbn` name-targeting when the build is too large for direct pin wiring.
- If you use flip-flop chute splitters, verify the exact part variant during setup.
- If two route descriptions disagree, trust the actual physical path and re-test with one ingot.

## Sorter ideas worth reusing

- One sorter can separate **ingots** from everything else.
- Another sorter can route **printer feed** versus **overflow storage**.
- If a sorter is controlled by IC, confirm its expected mode before debugging the script.
- Publish current route state to `db Setting` or a display if players need quick diagnostics.

## Active-printer behavior

When switching the active printer:

- close or disable the previous active machine cleanly
- clear stale state if the machine keeps old recipe/progress memory
- optionally eject leftovers before enabling the next machine
- avoid leaving two printers able to accept ingots at the same time

## Idle power-saving pattern

A useful hall feature is:

- detect nearby players with a **Proximity Sensor**
- start a timer only when printers are idle
- power down inactive printers after the timer expires

This is a good optional worker in a modular design.

## Shared user-input cautions

If several dials or buttons feed one hall controller:

- document whether values are **summed** or **single-source only**
- provide a reset path for latched counters or batch values
- assume multi-input convenience can become accidental overproduction

## Build notes that are easy to miss

- Short names matter when long `lbn` / `sbn` lines are fighting IC10 line width.
- Workshop descriptions can contain wiring typos; re-check sorter outputs in-game.
- Large monolithic printer-hall scripts often hit the **128-line** IC10 cap fast.
- If a design needs more features than one chip can hold, split it into workers instead of compressing everything into one unreadable blob.

## Good fit for this repo

For this repo, a multi-printer hall is best treated as a **modular feature** with separate workers for:

- active-printer selection
- hall logistics / routing
- overflow handling
- idle shutdown / proximity timer

Keep the player-facing setup doc explicit about:

- exact names
- route directions (`output0` / `output1`)
- which machine is the overflow target
- which worker owns each shared memory or control channel
