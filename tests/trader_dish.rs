//! Scenarios for `scripts/trader_dish_auto_land` (simulated dish, not in-game verified).
//!
//! The fake dish models the 2026 signal behaviour players describe: SignalStrength
//! is the angle in degrees between where the dish points and the contact (smaller
//! is closer), -1 when nothing is visible. Vertical runs from the zenith (0) to the
//! horizon (90). Activate while idle starts interrogation; Activate after
//! InterrogationProgress reached 1 calls the trader down.
mod common;
use common::*;

struct FakeDish {
    dev: Device,
    target: (f64, f64),
    ctype: f64,
    sid: f64,
    visible: f64,
    progress: f64,
    interrogating: bool,
    called: bool,
}

impl FakeDish {
    fn new(h: f64, v: f64, ctype: f64) -> Shared<Self> {
        let dev = Device::new(&[
            ("Horizontal", 0.0),
            ("Vertical", 0.0),
            ("Setting", 0.0),
            ("Activate", 0.0),
            ("BestContactFilter", -1.0),
            ("Idle", 1.0),
            ("TargetPadIndex", 0.0),
            ("SignalStrength", -1.0),
            ("SignalID", -1.0),
            ("ContactTypeId", -1.0),
            ("InterrogationProgress", 0.0),
        ])
        .prefab("StructureLargeSatelliteDish");
        share(FakeDish {
            dev,
            target: (h, v),
            ctype,
            sid: 777.0,
            visible: 40.0,
            progress: 0.0,
            interrogating: false,
            called: false,
        })
    }

    /// Great-circle angle between the dish heading and the contact.
    fn distance(&self) -> f64 {
        let (h1, v1) =
            (self.dev.get("Horizontal").to_radians(), self.dev.get("Vertical").to_radians());
        let (h2, v2) = (self.target.0.to_radians(), self.target.1.to_radians());
        let c = v1.cos() * v2.cos() + v1.sin() * v2.sin() * (h1 - h2).cos();
        c.clamp(-1.0, 1.0).acos().to_degrees()
    }
}

impl Logic for FakeDish {
    fn device(&self) -> &Device {
        &self.dev
    }
    fn device_mut(&mut self) -> &mut Device {
        &mut self.dev
    }
    fn read(&mut self, f: &str) -> Option<f64> {
        let d = self.distance();
        let seen = d <= self.visible;
        let or_none = |v: f64| if seen { v } else { -1.0 };
        match f {
            "SignalStrength" => Some(or_none(d)),
            "SignalID" => Some(or_none(self.sid)),
            "ContactTypeId" => Some(or_none(self.ctype)),
            "InterrogationProgress" => {
                if self.interrogating && d <= 6.0 && self.dev.get("Setting") >= 10000.0 {
                    self.progress = (self.progress + 0.1).min(1.0);
                    if self.progress >= 1.0 {
                        self.interrogating = false;
                        self.dev.set("Activate", 0.0);
                    }
                }
                Some(self.progress)
            }
            _ => self.dev.read_field(f),
        }
    }
    fn write(&mut self, f: &str, v: f64, tick: u64) -> bool {
        let ok = self.dev.write_field(f, v, tick);
        if f == "Activate" && v == 1.0 {
            match self.progress >= 1.0 {
                true => self.called = true,
                false => self.interrogating = true,
            }
        }
        ok
    }
}

fn run(dish: &Shared<FakeDish>, dial: Option<f64>, lever: Option<f64>, ticks: u64) -> Chip {
    let mut c = Chip::new(script("trader_dish_auto_land"))
        .pin("d0", dish)
        .pin("d3", &dev(&[("Setting", 0.0)]));
    if let Some(d) = dial {
        c = c.pin("d1", &dev(&[("Setting", d)]));
    }
    if let Some(l) = lever {
        c = c.pin("d2", &dev(&[("Open", l)]));
    }
    c.go(ticks);
    c
}

#[test]
fn finds_locks_interrogates_and_calls_down() {
    for (h, v) in [(200.0, 50.0), (10.0, 80.0), (300.0, 5.0), (95.0, 33.0)] {
        let dish = FakeDish::new(h, v, 3.0);
        run(&dish, Some(0.0), Some(1.0), 3000);
        let d = dish.borrow();
        assert_eq!(d.progress, 1.0, "({h}, {v}): interrogation completed");
        assert!(d.called, "({h}, {v}): trader called down");
        assert!(d.dev.writes_of("BestContactFilter").contains(&777.0), "locked to the contact");
    }
}

#[test]
fn lever_off_interrogates_but_does_not_call() {
    let dish = FakeDish::new(200.0, 50.0, 3.0);
    run(&dish, Some(0.0), Some(0.0), 3000);
    assert_eq!((dish.borrow().progress, dish.borrow().called), (1.0, false));
}

#[test]
fn dial_filters_the_trader_type() {
    let dish = FakeDish::new(200.0, 50.0, 3.0);
    run(&dish, Some(5.0), Some(1.0), 1500);
    let d = dish.borrow();
    assert!(!d.dev.writes_of("BestContactFilter").contains(&777.0));
    assert!(!(d.interrogating || d.called));
}

#[test]
fn the_same_trader_is_not_interrogated_twice() {
    let dish = FakeDish::new(200.0, 50.0, 3.0);
    let c = run(&dish, Some(0.0), Some(1.0), 6000);
    let presses = dish.writes_of("Activate").iter().filter(|&&v| v == 1.0).count();
    assert_eq!(presses, 2, "one interrogate + one call");
    assert_eq!((c.status() / 100.0).floor(), 1.0, "back to scanning");
}

#[test]
fn missing_dish_reports_900_without_halting() {
    let mut c = Chip::new(script("trader_dish_auto_land"));
    c.go(10);
    assert_eq!(c.status(), 900.0);
}
