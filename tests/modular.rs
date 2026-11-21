//! Behaviour scenarios for `modular scripts/` (simulated, multi-chip lockstep).
//!
//! Chips that share Logic Memory run tick by tick on one data network, so the tests
//! exercise the real cross-chip contracts (tokens, slots, housings).
mod common;
use common::*;

const MOD: &str = "modular scripts";

fn lockstep(chips: &mut [Chip], ticks: u64) {
    for _ in 0..ticks {
        for c in chips.iter_mut() {
            c.step_tick();
            assert_eq!(c.halted, None);
        }
    }
}

// ------------------------------------------------------------------ farm_potato_grower

fn potato() -> (Chip, Shared<Device>, Shared<Device>, Shared<Device>, Shared<Device>) {
    let hv = share(
        Device::new(&[
            ("Lock", 0.0),
            ("On", 1.0),
            ("Activate", 0.0),
            ("ImportCount", 0.0),
            ("Plant", 0.0),
            ("Harvest", 0.0),
        ])
        .prefab("StructureHarvie"),
    );
    let (lit, ctype) = (dev(&[("On", 0.0)]), dev(&[("Setting", 1.0)]));
    let slot0 = dev(&[("Setting", f64::from(1 | 8))]); // occupied + healthy, no daylight
    let chip =
        Chip::new(script(&format!("{MOD}/farm_potato_grower/farm_potato_worker_actuator.ic10")))
            .pin("d0", &hv)
            .pin("d1", &lit)
            .pin("d2", &ctype)
            .pin("d3", &slot0)
            .net(&hv);
    (chip, hv, lit, ctype, slot0)
}

#[test]
fn potato_light_dark_cycle() {
    let (mut c, _, lit, _, _) = potato();
    c.go(20);
    assert_eq!((lit.get("On"), c.status()), (1.0, 212.0), "light phase");
    c.go(650);
    assert_eq!((lit.get("On"), c.status()), (0.0, 213.0), "dark phase");
    c.go(400);
    assert_eq!(lit.get("On"), 1.0, "cycle restarts after TOTAL_TICKS");
}

#[test]
fn potato_mode_off_turns_light_off() {
    let (mut c, _, lit, ctype, _) = potato();
    c.go(20);
    ctype.set("Setting", 0.0);
    c.go(3);
    assert_eq!((lit.get("On"), c.status()), (0.0, 200.0));
}

#[test]
fn potato_mature_plant_harvest_pulse_and_cooldown() {
    let (mut c, hv, _, _, slot0) = potato();
    slot0.set("Setting", f64::from(1 | 2 | 8)); // occupied + mature + healthy
    c.go(30);
    let pulses: Vec<u64> =
        hv.borrow().writes.iter().filter(|w| w.1 == "Harvest" && w.2 == 1.0).map(|w| w.0).collect();
    assert!(!pulses.is_empty(), "mature plant must be harvested");
    assert_eq!(hv.writes_of("Harvest")[..2], [1.0, 0.0], "pulse 1 then 0");
    assert!(pulses.windows(2).all(|w| w[1] - w[0] >= 5), "cooldown between pulses: {pulses:?}");
}

// ------------------------------------------------------------- autolathe_ingot_printer

#[test]
fn ingot_printer_master_copies_the_selector_pick() {
    let sel = housing("selector_worker", -654790771.0);
    let fin = housing("finstd_worker", 0.0);
    let (s0, s1) = (memory("slot0", 0.0), memory("slot1", 0.0));
    let path = format!("{MOD}/autolathe_ingot_printer/autolathe_ingot_printer_master.ic10");
    let mut c = Chip::new(script(&path)).net(&sel).net(&fin).net(&s0).net(&s1);
    c.go(3);
    assert_eq!((s0.get("Setting"), c.status()), (-654790771.0, -654790771.0));
    sel.set("Setting", 640.0); // selector status code, not a pick
    c.go(3);
    assert_eq!((s0.get("Setting"), c.status()), (-654790771.0, 260.0));
    fin.set("PrefabHash", 0.0); // final stacker housing missing
    c.go(3);
    assert_eq!(c.status(), 251.0);
}

// ----------------------------------------------------------- autolathe_restock_vending

const FIRST_ITEM: f64 = 1225836666.0;

struct Restock {
    mem: Vec<(&'static str, Shared<Device>)>,
    mach: Shared<Device>,
    stack: Shared<Device>,
    chips: Vec<Chip>,
}

impl Restock {
    /// stock worker -> machine worker -> prep worker; `prep_first` swaps the update
    /// order, which scripts cannot rely on in-game.
    fn new(prep_first: bool) -> Self {
        let names = ["cmd_token", "cmd_type", "slot0", "slot1", "slot2", "slot3", "slot4"];
        let mem: Vec<_> = names.iter().map(|&n| (n, memory(n, 0.0))).collect();
        let vend = share(
            Device::new(&[("On", 1.0)])
                .slots((0..102).map(|_| fields(&[("Occupied", 0.0)])).collect()),
        );
        let mach = dev(&[
            ("On", 0.0),
            ("Activate", 0.0),
            ("Open", 1.0),
            ("RecipeHash", 0.0),
            ("ExportCount", 0.0),
        ]);
        let stack = dev(&[("On", 0.0), ("Mode", 1.0), ("Setting", 1.0), ("ExportCount", 0.0)]);
        let on_net = |c: Chip| mem.iter().fold(c, |c, (_, m)| c.net(m));
        let d = format!("{MOD}/autolathe_restock_vending/autolathe_restock_");
        let stock = on_net(Chip::new(script(&format!("{d}worker_stock.ic10"))).pin("d0", &vend));
        let machine = on_net(
            Chip::new(script(&format!("{d}worker_machine.ic10")))
                .pin("d0", &mach)
                .pin("d1", &stack),
        );
        let prep =
            on_net(Chip::new(script(&format!("{d}worker_machine_prep.ic10"))).pin("d0", &mach));
        let chips = match prep_first {
            true => vec![stock, prep, machine],
            false => vec![stock, machine, prep],
        };
        Restock { mem, mach, stack, chips }
    }
    fn m(&self, name: &str) -> f64 {
        self.mem.iter().find(|(n, _)| *n == name).map_or(f64::NAN, |(_, d)| d.get("Setting"))
    }
    fn machine(&mut self) -> &mut Chip {
        let i = self.chips.iter().position(|c| c.pins.contains_key("d1")).unwrap_or(1);
        &mut self.chips[i]
    }
}

#[test]
fn restock_prints_a_missing_item_and_consumes_the_command() {
    for prep_first in [false, true] {
        let mut r = Restock::new(prep_first);
        lockstep(&mut r.chips, 110); // one full 100-slot scan
        assert_eq!((r.m("slot0"), r.m("cmd_token")), (FIRST_ITEM, 1.0));
        lockstep(&mut r.chips, 10);
        assert_eq!(r.m("cmd_type"), 0.0, "machine worker consumed the command");
        assert_eq!(r.m("slot4"), 1.0, "run in progress");
        assert_eq!(read(&r.mach, &["On", "Open", "RecipeHash"]), [1.0, 0.0, FIRST_ITEM]);
        assert_eq!(r.m("slot3"), 1.0, "prep reports ready");
        assert_eq!(r.mach.get("Activate"), 1.0);
        // machine exports one item, stacker flushes it
        r.mach.set("ExportCount", 1.0);
        r.mach.set("Activate", 0.0);
        r.stack.set("ExportCount", 1.0);
        lockstep(&mut r.chips, 5);
        assert_eq!((r.m("slot4"), r.m("slot3")), (0.0, 0.0), "run lock released");
        let done = r.machine().status();
        let reported = r.machine().pins["db"].borrow().device().writes_of("Setting");
        assert!(reported.contains(&140.0), "reported done (status now {done})");
    }
}

#[test]
fn restock_machine_restart_releases_the_run_lock() {
    let mut r = Restock::new(false);
    lockstep(&mut r.chips, 120);
    assert_eq!(r.m("slot4"), 1.0);
    r.machine().reset(); // chip reset mid-run
    lockstep(&mut r.chips, 3);
    assert_eq!(r.m("slot4"), 0.0, "restarted worker must not leave slot4 stuck");
}

#[test]
fn restock_feeder_requests_once_per_gap() {
    // S2: the feeder used to write RequestHash every tick while an ingot travelled.
    let need = -1301215609.0; // Ingot (Iron)
    let slot2 = memory("slot2", need);
    let sort = share(Device::new(&[("On", 0.0), ("Mode", 0.0), ("Output", 0.0)]).slots(vec![
        fields(&[("Occupied", 0.0), ("OccupantHash", 0.0)]),
        fields(&[("Occupied", 0.0)]),
        fields(&[("Occupied", 0.0)]),
    ]));
    let vend = dev(&[("On", 0.0), ("RequestHash", 0.0)]);
    let path =
        format!("{MOD}/autolathe_restock_vending/autolathe_restock_worker_logistics_feeder.ic10");
    let mut c = Chip::new(script(&path)).pin("d0", &sort).pin("d1", &vend).net(&slot2);
    c.go(8);
    assert_eq!(vend.writes_of("RequestHash"), [need], "one request, then wait");
    c.go(12);
    assert_eq!(vend.writes_of("RequestHash").len(), 2, "asks again after the gap");
    {
        let mut s = sort.borrow_mut();
        s.slots[0] = fields(&[("Occupied", 1.0), ("OccupantHash", need)]); // ingot arrived
    }
    c.go(2);
    assert_eq!(sort.get("Output"), 1.0);
}
