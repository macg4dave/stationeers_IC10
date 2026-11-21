//! Shared helpers for the behaviour scenarios.
#![allow(dead_code)] // each test file uses a different subset

#[allow(unused_imports)] // each test file uses a different subset
pub use ic10_tools::engine::{
    Chip, Device, Logic, Program, Shared, analyse, fields, hash, load, parse, share,
};
use ic10_tools::repo;

/// Kelvin offset.
pub const K: f64 = 273.15;

/// A shipped script by repo-relative path, or `scripts/<name>` shorthand.
pub fn script(rel: &str) -> Program {
    let root = repo::root();
    let path = match rel.ends_with(".ic10") {
        true => root.join(rel),
        false => root.join("scripts").join(rel).join(format!("{rel}.ic10")),
    };
    assert!(path.exists(), "script not found: {}", path.display());
    load(&path)
}

pub fn dev(pairs: &[(&str, f64)]) -> Shared<Device> {
    share(Device::new(pairs))
}

/// Pipe Analyzer / Gas Sensor style reader.
pub fn analyzer(temp_c: f64, kpa: f64, extra: &[(&str, f64)]) -> Shared<Device> {
    let mut d =
        Device::new(&[("Temperature", temp_c + K), ("Pressure", kpa), ("Error", 0.0), ("On", 1.0)]);
    d.fields.extend(fields(extra));
    share(d.prefab("StructurePipeAnalysizer"))
}

/// Device with On/Open/Lock/Mode/Setting (valve, vent, heater...).
pub fn switchable(extra: &[(&str, f64)]) -> Shared<Device> {
    let mut d =
        Device::new(&[("On", 0.0), ("Open", 0.0), ("Lock", 0.0), ("Mode", 0.0), ("Setting", 0.0)]);
    d.fields.extend(fields(extra));
    share(d)
}

pub fn memory(name: &str, value: f64) -> Shared<Device> {
    share(Device::new(&[("Setting", value)]).prefab("StructureLogicMemory").named(name))
}

pub fn housing(name: &str, setting: f64) -> Shared<Device> {
    share(
        Device::new(&[("Setting", setting), ("On", 1.0)])
            .prefab("StructureCircuitHousing")
            .named(name),
    )
}

/// Field access on a shared device without spelling out `borrow()`.
pub trait Probe {
    fn get(&self, f: &str) -> f64;
    fn set(&self, f: &str, v: f64);
    fn writes_of(&self, f: &str) -> Vec<f64>;
}

impl<T: Logic> Probe for Shared<T> {
    fn get(&self, f: &str) -> f64 {
        self.borrow().device().get(f)
    }
    fn set(&self, f: &str, v: f64) {
        self.borrow_mut().device_mut().set(f, v);
    }
    fn writes_of(&self, f: &str) -> Vec<f64> {
        self.borrow().device().writes_of(f)
    }
}

/// Read several fields at once, for compact assertions.
pub fn read<T: Logic>(d: &Shared<T>, names: &[&str]) -> Vec<f64> {
    names.iter().map(|n| d.get(n)).collect()
}

pub trait Run {
    /// Run `ticks` ticks and fail the test if the chip halted.
    fn go(&mut self, ticks: u64) -> &mut Self;
}

impl Run for Chip {
    fn go(&mut self, ticks: u64) -> &mut Self {
        self.run(ticks);
        assert_eq!(self.halted, None, "chip halted at tick {}", self.tick);
        self
    }
}
