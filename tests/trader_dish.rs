//! Scenarios for `scripts/trader_dish_auto_land` (simulated dish, not in-game verified).
//!
//! The fake dish models the 2026 signal behaviour players describe: SignalStrength
//! is the angle in degrees between where the dish points and the contact (smaller
//! is closer), -1 when nothing is visible. Vertical runs from the zenith (0) to the
//! horizon (90). The dish turns 4° per tick, reads Idle 0 and SignalStrength -1 while it
//! turns (wiki). After it stops, SignalStrength stays -1 for `resolve` reads while SignalID
//! already shows the contact (the working 2026 tracker waits up to 8.5 s for this). WattsReachingContact falls off with the angle; interrogation needs it at
//! MinimumWattsToContact. Activate keeps the value written; only a 0 -> 1 change is a
//! press (as the working 2026 scripts pulse it). A press starts interrogation, or calls
//! the trader down once InterrogationProgress reached 1. Writing 0 stops interrogation.
mod common;
use common::*;

/// The fake trader needs this much power on target before interrogation progresses.
const MIN_W: f64 = 7000.0;

struct FakeDish {
    dev: Device,
    target: (f64, f64),
    ctype: f64,
    sid: f64,
    visible: f64,
    progress: f64,
    interrogating: bool,
    starts: u32,
    calls: u32,
    busy: f64,
    resolve: f64,
    settled: f64,
    started: Option<u64>,
    lock_at: Option<u64>,
}

impl FakeDish {
    fn new(h: f64, v: f64, ctype: f64) -> Shared<Self> {
        let dev = Device::new(&[
            ("On", 1.0),
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
            starts: 0,
            calls: 0,
            busy: 0.0,
            resolve: 0.0,
            settled: 0.0,
            started: None,
            lock_at: None,
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
            "Idle" if self.busy > 0.0 => {
                self.busy -= 1.0;
                Some(0.0)
            }
            "SignalStrength" if self.busy > 0.0 => Some(-1.0),
            "SignalStrength" if seen && self.settled < self.resolve => {
                self.settled += 1.0;
                Some(-1.0)
            }
            "SignalStrength" => Some(or_none(d)),
            "WattsReachingContact" => Some(self.dev.get("Setting") * (1.0 - d / 20.0).max(0.0)),
            "MinimumWattsToContact" => Some(MIN_W),
            "SignalID" => Some(or_none(self.sid)),
            "ContactTypeId" => Some(or_none(self.ctype)),
            "InterrogationProgress" => {
                if self.interrogating && self.read("WattsReachingContact") >= Some(MIN_W) {
                    self.progress = (self.progress + 0.1).min(1.0);
                }
                Some(self.progress)
            }
            _ => self.dev.read_field(f),
        }
    }
    fn write(&mut self, f: &str, v: f64, tick: u64) -> bool {
        if f == "Horizontal" || f == "Vertical" {
            let turn = (v - self.dev.get(f)).abs() % 360.0;
            self.busy += (turn.min(360.0 - turn) / 4.0).ceil();
            self.settled = 0.0;
        }
        if f == "BestContactFilter" && v >= 0.0 && self.lock_at.is_none() {
            self.lock_at = Some(tick);
        }
        let pressed = f == "Activate" && v == 1.0 && self.dev.get(f) == 0.0;
        let ok = self.dev.write_field(f, v, tick);
        match (f, v) {
            ("Activate", 0.0) => self.interrogating = false,
            _ if pressed && self.progress >= 1.0 => self.calls += 1,
            _ if pressed => {
                self.interrogating = true;
                self.starts += 1;
                self.started.get_or_insert(tick);
            }
            _ => {}
        }
        ok
    }
}

fn run(dish: &Shared<FakeDish>, lever: Option<f64>, ticks: u64) -> Chip {
    let mut c = Chip::new(script("trader_dish_auto_land"))
        .pin("d0", dish)
        .pin("d1", &dev(&[("Activate", 0.0)]))
        .pin("d3", &dev(&[("Setting", 0.0)]));
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
        run(&dish, None, 3000);
        let d = dish.borrow();
        assert_eq!(d.progress, 1.0, "({h}, {v}): interrogation completed");
        assert_eq!(d.calls, 1, "({h}, {v}): trader called down");
        assert!(d.dev.writes_of("BestContactFilter").contains(&777.0), "locked to the contact");
    }
}

#[test]
fn lever_on_stops_the_call_down() {
    for (lever, call) in [(None, true), (Some(0.0), true), (Some(1.0), false)] {
        let dish = FakeDish::new(200.0, 50.0, 3.0);
        run(&dish, lever, 3000);
        let d = dish.borrow();
        assert_eq!(d.progress, 1.0, "lever {lever:?}: interrogation completed");
        assert_eq!(d.calls == 1, call, "lever {lever:?}: auto-land unless the lever is on");
    }
}

#[test]
fn skip_button_drops_the_trader_and_scans_on() {
    let locking: fn(&FakeDish) -> bool = |d| d.lock_at.is_some();
    let interrogating: fn(&FakeDish) -> bool = |d| d.interrogating;
    for (phase, pressed_when, presses) in
        [("locking", locking, 0), ("interrogating", interrogating, 1)]
    {
        let dish = FakeDish::new(200.0, 50.0, 3.0);
        let mut c = run(&dish, None, 0);
        while !pressed_when(&dish.borrow()) && c.tick < 3000 {
            c.go(1);
        }
        for (v, ticks) in [(1.0, 1), (0.0, 3000)] {
            c.pins["d1"].borrow_mut().device_mut().set("Activate", v); // one-tick press
            c.go(ticks);
        }
        let d = dish.borrow();
        assert_eq!(d.starts, presses, "{phase}: skipped trader is not interrogated again");
        assert!(!d.interrogating, "{phase}: skip stops the interrogation");
        assert_eq!(d.calls, 0, "{phase}: skipped trader is not called down");
        assert_eq!((c.status() / 100.0).floor(), 1.0, "{phase}: back to scanning");
    }
}

#[test]
fn the_same_trader_is_not_interrogated_twice() {
    let dish = FakeDish::new(200.0, 50.0, 3.0);
    let c = run(&dish, None, 6000);
    let d = dish.borrow();
    assert_eq!((d.starts, d.calls), (1, 1), "one interrogation, one call-down");
    assert_eq!((c.status() / 100.0).floor(), 1.0, "back to scanning");
}

#[test]
fn missing_dish_reports_900_without_halting() {
    let mut c = Chip::new(script("trader_dish_auto_land"));
    c.go(10);
    assert_eq!(c.status(), 900.0);
}

#[test]
fn interrogates_as_soon_as_enough_power_reaches_the_trader() {
    // 3.3° off the scan point (60, 40): not within the 2° lock limit, but close enough
    // for MinimumWattsToContact at MAX_W, so no lock-on moves are needed.
    let dish = FakeDish::new(64.0, 42.0, 3.0);
    dish.borrow_mut().visible = 10.0;
    run(&dish, None, 1500);
    let d = dish.borrow();
    let (Some(lock), Some(start)) = (d.lock_at, d.started) else {
        panic!("trader locked and interrogated: {:?} {:?}", d.lock_at, d.started);
    };
    assert!(start - lock <= 1, "interrogation starts without a lock-on search ({lock} -> {start})");
}

#[test]
fn status_is_the_phase_and_shows_interrogation_progress() {
    // In-game ContactTypeId read about 5.44 million and swamped `phase * 100 + type`.
    let dish = FakeDish::new(200.0, 50.0, 5_440_920.0);
    let c = run(&dish, None, 3000);
    let shown = c.pins["db"].borrow().device().writes_of("Setting");
    let bad: Vec<_> = shown.iter().filter(|&&s| !(100.0..=900.0).contains(&s)).collect();
    assert!(bad.is_empty(), "status stays a phase code (100..900): {bad:?}");
    assert!(shown.iter().any(|s| (s - 350.0).abs() < 1e-6), "3xx shows progress %: {shown:?}");
    assert!(shown.contains(&500.0), "called down shows 500");
}

#[test]
fn waits_for_a_slow_signal_to_resolve() {
    // In-game a second trader was never found after the first landed; Medium and larger
    // contacts take up to 8.5 s to resolve after the dish stops.
    let dish = FakeDish::new(200.0, 50.0, 3.0);
    dish.borrow_mut().resolve = 16.0; // 8 s
    run(&dish, None, 6000);
    let d = dish.borrow();
    assert_eq!((d.starts, d.calls), (1, 1), "slow-resolving trader interrogated and called");
}

#[test]
fn dish_turns_off_while_a_ship_is_on_the_pad() {
    // Landing pad Mode > 1 = busy (a working 2026 pad resolver treats it so; unconfirmed).
    let dish = FakeDish::new(200.0, 50.0, 3.0);
    let pad = dev(&[("Mode", 2.0)]);
    let mut c = Chip::new(script("trader_dish_auto_land")).pin("d0", &dish).pin("d4", &pad);
    c.go(600);
    {
        let d = dish.borrow();
        assert_eq!(d.dev.get("On"), 0.0, "busy pad turns the dish off");
        assert!(d.dev.writes_of("Horizontal").is_empty(), "no scanning while the pad is busy");
        assert_eq!(c.status(), 600.0, "busy pad shows 600");
    }
    pad.borrow_mut().device_mut().set("Mode", 0.0);
    c.go(3000);
    let d = dish.borrow();
    assert_eq!(d.dev.get("On"), 1.0, "free pad turns the dish back on");
    assert_eq!(d.calls, 1, "next trader found and called down once the pad is free");
    drop(d);
    pad.borrow_mut().device_mut().set("Mode", 3.0);
    c.go(200);
    assert_eq!(dish.borrow().dev.get("On"), 0.0, "pad busy again: dish off within a scan move");
}
