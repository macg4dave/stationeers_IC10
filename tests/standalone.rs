//! Behaviour scenarios for `scripts/` (simulated, not in-game verified).
//!
//! Each test drives a script through what its README promises: threshold
//! crossings, hysteresis bands, startup state and fault handling. Passing means the
//! IC10 logic matches the docs under the simulator's model; in-game behaviour still
//! needs a human check.
mod common;
use common::*;

const VENT: &str = "StructureActiveVent";
const VALVE: &str = "StructureDigitalValve";

fn vent(name: &str, extra: &[(&str, f64)]) -> Shared<Device> {
    let mut d =
        Device::new(&[("On", 0.0), ("Open", 0.0), ("Lock", 0.0), ("Mode", 0.0), ("Setting", 0.0)]);
    d.fields.extend(fields(extra));
    share(d.prefab(VENT).named(name))
}

fn gas_sensor(temp_c: f64, kpa: f64, extra: &[(&str, f64)]) -> Shared<Device> {
    let mut d = Device::new(&[("Temperature", temp_c + K), ("Pressure", kpa)]);
    d.fields.extend(fields(extra));
    share(d.prefab("StructureGasSensor"))
}

fn chip(name: &str, pins: &[(&str, &Shared<Device>)]) -> Chip {
    pins.iter().fold(Chip::new(script(name)), |c, (pin, d)| c.pin(pin, d))
}

fn temp(d: &Shared<Device>, c: f64) {
    d.set("Temperature", c + K);
}

// ------------------------------------------------------------ heating and cooling

#[test]
fn pipe_heater_hold_20c() {
    let (pa, h) = (analyzer(25.0, 100.0, &[]), switchable(&[]));
    let mut c = chip("pipe_heater_hold_20c", &[("d0", &pa), ("d1", &h)]);
    for (t, want) in [(25.0, 0.0), (15.0, 1.0), (21.0, 1.0), (23.0, 0.0), (21.0, 0.0), (19.0, 1.0)]
    {
        temp(&pa, t);
        c.go(4);
        assert_eq!(h.get("On"), want, "{t}C");
    }
    pa.set("Error", 1.0);
    c.go(4);
    assert_eq!(h.get("On"), 0.0, "analyzer error forces OFF");
}

#[test]
fn room_heater_hold_20c() {
    let (s, h) = (gas_sensor(15.0, 100.0, &[]), switchable(&[]));
    let mut c = chip("room_heater_hold_20c", &[("d0", &s), ("d1", &h)]);
    c.go(4);
    assert_eq!(h.get("On"), 1.0);
    temp(&s, 21.0);
    c.go(4);
    assert_eq!(h.get("On"), 1.0, "20..22C band holds");
    temp(&s, 23.0);
    c.go(4);
    assert_eq!(h.get("On"), 0.0);
    s.set("Temperature", 0.0);
    c.go(4);
    assert_eq!((h.get("On"), c.status()), (0.0, 9.0), "no reading");
}

#[test]
fn air_conditioner_hold_25c() {
    let ac = switchable(&[]);
    let mut c = Chip::new(script("air_conditioner_hold_25c")).pin("db", &ac);
    c.go(4);
    assert!((ac.get("Setting") - (25.0 + K)).abs() < 1e-9);
    assert_eq!(read(&ac, &["Mode", "On"]), [1.0, 1.0]);
    c.go(10);
    assert_eq!(ac.borrow().writes.len(), 3, "no repeated writes once settled");
}

#[test]
fn room_cooler_and_steam_vent() {
    let s = gas_sensor(31.0, 100.0, &[("RatioSteam", 0.0)]);
    let (cool, v) = (switchable(&[]), switchable(&[]));
    let mut c = chip("room_cooler_and_steam_vent", &[("d0", &s), ("d1", &cool), ("d2", &v)]);
    c.go(4);
    assert_eq!((cool.get("On"), v.get("On"), v.get("Open"), c.status()), (1.0, 1.0, 1.0, 3.0));
    s.set("RatioSteam", 0.0005);
    temp(&s, 29.0);
    c.go(4);
    assert_eq!((cool.get("On"), v.get("On")), (1.0, 1.0), "both inside their bands");
    s.set("RatioSteam", 0.002);
    temp(&s, 27.0);
    c.go(4);
    assert_eq!((cool.get("On"), v.get("On"), c.status()), (0.0, 0.0, 0.0));
}

#[test]
fn room_door_open_when_hot() {
    let (s, d) = (gas_sensor(31.0, 100.0, &[]), switchable(&[("Lock", 1.0)]));
    let mut c = chip("room_door_open_when_hot", &[("d0", &s), ("d1", &d)]);
    c.go(4);
    assert_eq!(read(&d, &["Open", "Lock", "On"]), [1.0, 0.0, 1.0]);
    for (t, want, why) in
        [(29.0, 1.0, "band holds open"), (27.0, 0.0, "closes"), (29.0, 0.0, "band holds closed")]
    {
        temp(&s, t);
        c.go(4);
        assert_eq!(d.get("Open"), want, "{why}");
    }
}

#[test]
fn furnace_heat_pipe_below_20c() {
    let (pa, valve) = (analyzer(15.0, 100.0, &[]), switchable(&[]));
    let furnace = dev(&[
        ("Temperature", 50.0 + K),
        ("On", 0.0),
        ("Activate", 0.0),
        ("Lock", 0.0),
        ("SettingInput", 0.0),
        ("SettingOutput", 0.0),
    ]);
    let mut c =
        chip("furnace_heat_pipe_below_20c", &[("d0", &pa), ("d1", &valve), ("d2", &furnace)]);
    c.go(4);
    assert_eq!(valve.get("On"), 1.0);
    assert_eq!(
        read(&furnace, &["On", "Activate", "SettingInput", "SettingOutput"]),
        [1.0, 1.0, 5.0, 5.0]
    );
    temp(&furnace, 120.0);
    c.go(4);
    assert_eq!(furnace.get("SettingInput"), 0.0);
    temp(&pa, 25.0);
    c.go(4);
    assert_eq!((valve.get("On"), furnace.get("On"), furnace.get("Activate")), (0.0, 0.0, 0.0));
}

#[test]
fn furnace_pulse_when_pipes_cold() {
    let (liq, gas) = (dev(&[("Temperature", 90.0 + K)]), dev(&[("Temperature", 20.0 + K)]));
    let (valve, furnace) = (switchable(&[]), dev(&[("Activate", 0.0)]));
    let pins = [("d0", &liq), ("d1", &gas), ("d2", &valve), ("d3", &furnace)];
    chip("furnace_pulse_when_pipes_cold", &pins).go(5);
    assert_eq!(furnace.writes_of("Activate")[..2], [1.0, 0.0]);
    assert_eq!(valve.writes_of("On")[..2], [1.0, 0.0]);
    assert_eq!(furnace.get("Activate"), 0.0);
}

// ------------------------------------------------------ valves driven by temperature

fn valve_cycle(
    c: &mut Chip,
    reader: &Shared<Device>,
    valve: &Shared<Device>,
    points: &[(f64, f64)],
) {
    for &(t, want) in points {
        temp(reader, t);
        c.go(4);
        assert_eq!(valve.get("On"), want, "at {t}C");
    }
}

#[test]
fn liquid_valves_open_when_cold() {
    let r = analyzer(25.0, 100.0, &[]);
    let v = dev(&[("On", 1.0), ("PrefabHash", -517628750.0)]);
    let mut c = chip("liquid_valves_open_when_cold", &[("d0", &r)]).net(&v);
    c.go(4);
    assert_eq!(v.get("On"), 0.0, "in-band start closes valves left open");
    v.set("On", 1.0); // a valve that missed the write
    c.go(30);
    assert_eq!(v.get("On"), 0.0, "periodic resend corrects it");
    valve_cycle(&mut c, &r, &v, &[(15.0, 1.0), (25.0, 1.0), (31.0, 0.0), (25.0, 0.0), (19.0, 1.0)]);
}

#[test]
fn pipe_valves_open_when_cold() {
    let r = analyzer(20.0, 100.0, &[]);
    let v = share(Device::new(&[("On", 1.0), ("Lock", 0.0)]).prefab(VALVE).named("cold"));
    let other = share(Device::new(&[("On", 1.0)]).prefab(VALVE).named("hot"));
    let mut c = chip("pipe_valves_open_when_cold", &[("d0", &r)]).net(&v).net(&other);
    valve_cycle(&mut c, &r, &v, &[(20.0, 0.0), (5.0, 1.0), (20.0, 1.0), (31.0, 0.0)]);
    assert_eq!(other.get("On"), 1.0, "only valves named exactly 'cold' change");
}

#[test]
fn phase_change_cooling_valve() {
    let r = dev(&[("Temperature", 20.0 + K)]);
    let v = share(Device::new(&[("On", 1.0), ("Lock", 1.0)]).prefab(VALVE).named("cold"));
    let mut c = chip("phase_change_cooling_valve", &[("d0", &r)]).net(&v);
    valve_cycle(&mut c, &r, &v, &[(20.0, 0.0), (31.0, 1.0), (29.0, 1.0), (27.0, 0.0), (29.0, 0.0)]);
    assert_eq!(v.get("Lock"), 0.0);
}

#[test]
fn pipe_sort_hot_cold_with_pump() {
    let pa = analyzer(20.0, 5000.0, &[]);
    let (cold, hot, pump) = (switchable(&[]), switchable(&[]), switchable(&[]));
    let heaters = [pipe_heater(), pipe_heater()];
    let mut c = chip(
        "pipe_sort_hot_cold_with_pump",
        &[("d0", &pa), ("d1", &hot), ("d2", &cold), ("d3", &pump)],
    );
    c = heaters.iter().fold(c, |c, h| c.net(h));
    for (t, want) in [
        (15.0, (1.0, 0.0)),
        (22.0, (1.0, 0.0)),
        (25.0, (0.0, 0.0)),
        (42.0, (0.0, 1.0)),
        (38.0, (0.0, 1.0)),
        (35.0, (0.0, 0.0)),
    ] {
        temp(&pa, t);
        c.go(4);
        assert_eq!((cold.get("On"), hot.get("On")), want, "{t}C (bands hold inside)");
        for h in &heaters {
            assert_eq!(h.get("On"), want.0, "{t}C: pipe heaters follow the cold valve");
        }
    }
    for (kpa, want, why) in [
        (5000.0, 1.0, "fills"),
        (10300.0, 0.0, "stops above 10.25 MPa"),
        (9900.0, 0.0, "band holds off"),
        (9700.0, 1.0, "restarts"),
    ] {
        pa.set("Pressure", kpa);
        c.go(4);
        assert_eq!(pump.get("On"), want, "{why}");
    }
    assert_eq!(pump.get("Setting"), 1.0);
    pa.set("Error", 1.0);
    c.go(4);
    assert_eq!((pump.get("On"), c.status()), (0.0, 9.0), "analyzer error stops the pump");
    pa.set("Error", 0.0);
    temp(&pa, 15.0);
    c.go(4);
    assert_eq!(heaters[0].get("On"), 1.0, "cold gas heats again");
    pa.set("Error", 1.0);
    c.go(4);
    assert_eq!(heaters[0].get("On"), 0.0, "analyzer error turns the pipe heaters off");
}

fn pipe_heater() -> Shared<Device> {
    share(Device::new(&[("On", 0.0)]).prefab("StructurePipeHeater"))
}

#[test]
fn pipe_sort_hot_cold_with_pump_runs_without_a_pump() {
    let pa = analyzer(15.0, 5000.0, &[]);
    let (cold, hot) = (switchable(&[]), switchable(&[]));
    let mut c = chip("pipe_sort_hot_cold_with_pump", &[("d0", &pa), ("d1", &hot), ("d2", &cold)]);
    c.go(4);
    assert_eq!((cold.get("On"), c.status()), (1.0, 1.0), "valves work with d3 empty");
    temp(&pa, 42.0);
    c.go(4);
    assert_eq!((hot.get("On"), c.status()), (1.0, 2.0), "hot path, no pump bit");
    pa.set("Error", 1.0);
    c.go(4);
    assert_eq!((c.halted.is_none(), c.status()), (true, 9.0), "analyzer error, no halt");
}

// ------------------------------------------------------------------ pressure and air

#[test]
fn room_vents_hold_pressure() {
    let s = gas_sensor(20.0, 100.0, &[]);
    let v = vent("ROOM_VENT", &[]);
    let mut c = chip("room_vents_hold_pressure", &[("d0", &s)]).net(&v);
    let mut at = |kpa: f64| {
        s.set("Pressure", kpa);
        c.go(8);
        (v.get("On"), v.get("Mode"), v.get("Setting"))
    };
    assert_eq!(at(80.0), (1.0, 0.0, 120.0), "low: blow in");
    for _ in 0..8 {
        at(100.0); // 64 ticks (32 s) still filling
    }
    assert_eq!(v.writes_of("Mode").len(), 1, "a running vent is set once, not re-sent");
    assert_eq!(at(120.0).0, 0.0);
    assert_eq!(at(130.0), (1.0, 1.0, 90.0), "high: pull out");
    assert_eq!(at(90.0).0, 0.0);
    assert_eq!(at(2500.0).0, 1.0, "a 2.5 MPa room is exhausted, never treated as low");
    assert_eq!(v.get("Mode"), 1.0);
}

#[test]
fn room_vents_swap_air_when_hot() {
    let s = gas_sensor(20.0, 100.0, &[]);
    let vin = vent("IN", &[("On", 1.0), ("Open", 1.0)]);
    let vout = vent("OUT", &[("On", 1.0), ("Open", 1.0)]);
    let mut c = chip("room_vents_swap_air_when_hot", &[("d0", &s)]).net(&vin).net(&vout);
    c.go(4);
    assert_eq!(read(&vin, &["On", "Open"]), [0.0, 0.0], "cold start turns running vents off");
    assert_eq!(read(&vout, &["On", "Open"]), [0.0, 0.0]);
    temp(&s, 35.0);
    c.go(4);
    let keys = ["Mode", "Setting", "Open", "On", "Lock"];
    assert_eq!(read(&vin, &keys), [0.0, 60000.0, 1.0, 1.0, 1.0]);
    assert_eq!(read(&vout, &keys), [1.0, 0.0, 1.0, 1.0, 1.0]);
}

#[test]
fn pipe_vents_fill_to_10mpa() {
    let pa = analyzer(20.0, 9950.0, &[]);
    let v = vent("PIPE_VENT", &[("On", 1.0), ("Open", 1.0)]);
    let mut c = chip("pipe_vents_fill_to_10mpa", &[("d0", &pa)]).net(&v);
    c.go(4);
    assert_eq!(v.get("On"), 0.0, "startup stops the vents");
    pa.set("Pressure", 5000.0);
    c.go(4);
    assert_eq!(read(&v, &["Mode", "Setting", "On"]), [1.0, 10000.0, 1.0]);
    pa.set("Pressure", 10000.0);
    c.go(4);
    assert_eq!(v.get("On"), 0.0);
    pa.set("Pressure", 9950.0);
    c.go(6);
    assert_eq!(v.get("On"), 0.0, "inside hysteresis: stay idle");
}

#[test]
fn pipe_vent_fill_to_half() {
    let (pa, v) = (analyzer(20.0, 40.0, &[]), switchable(&[]));
    let mut c = chip("pipe_vent_fill_to_half", &[("d0", &pa), ("d1", &v)]);
    for (kpa, want) in [(40.0, 1.0), (52.0, 1.0), (56.0, 0.0), (52.0, 0.0), (49.0, 1.0)] {
        pa.set("Pressure", kpa);
        c.go(4);
        assert_eq!(read(&v, &["On", "Open"]), [want, want], "{kpa} kPa");
    }
}

#[test]
fn greenhouse_co2_pressure_vent() {
    let s = gas_sensor(20.0, 101.0, &[("RatioCarbonDioxide", 0.3)]);
    let v = switchable(&[]);
    let mut c = chip("greenhouse_co2_pressure_vent", &[("d0", &s), ("d1", &v)]);
    c.go(4);
    assert_eq!(v.get("On"), 0.0);
    s.set("RatioCarbonDioxide", 0.1);
    c.go(4);
    assert_eq!(read(&v, &["On", "Open", "Mode", "Setting"]), [1.0, 1.0, 0.0, 100.0]);
    s.set("RatioCarbonDioxide", 0.3);
    s.set("Pressure", 80.0);
    c.go(4);
    assert_eq!(v.get("On"), 1.0, "low pressure also tops up");
    s.set("Pressure", 2500.0);
    c.go(4);
    assert_eq!(v.get("On"), 0.0, "a high-pressure room never opens");
}

#[test]
fn liquid_pipe_top_up_vent() {
    let pa = dev(&[("Volume", 100.0), ("VolumeOfLiquid", 30.0)]);
    let v = switchable(&[("Mode", 1.0)]);
    let mut c = chip("liquid_pipe_top_up_vent", &[("d0", &pa), ("d1", &v)]);
    c.go(4);
    assert_eq!(read(&v, &["Mode", "On", "Open"]), [0.0, 1.0, 1.0]);
    pa.set("VolumeOfLiquid", 60.0);
    c.go(4);
    assert_eq!(v.get("On"), 0.0);
}

#[test]
fn gas_mixer_stop_at_10mpa() {
    let (pa, m) = (analyzer(20.0, 5000.0, &[("On", 0.0)]), switchable(&[]));
    let mut c = chip("gas_mixer_stop_at_10mpa", &[("d0", &pa), ("d1", &m)]);
    c.go(4);
    assert_eq!(pa.writes_of("On"), [1.0], "turns the analyzer on first");
    for (kpa, want, why) in [
        (5000.0, 1.0, "runs"),
        (10001.0, 0.0, "stops"),
        (9700.0, 0.0, "9.5..10 MPa band holds off"),
        (9400.0, 1.0, "restarts"),
    ] {
        pa.set("Pressure", kpa);
        c.go(4);
        assert_eq!(m.get("On"), want, "{why}");
    }
    pa.set("Pressure", 100.0);
    pa.set("Error", 1.0);
    c.go(4);
    assert_eq!((m.get("On"), c.status()), (0.0, 3.0));
}

// ------------------------------------------------------------------ methane and fuel

#[test]
fn pipe_valve_open_when_methane() {
    let (pa, v) = (analyzer(20.0, 100.0, &[("RatioMethane", 0.2)]), switchable(&[]));
    let mut c = chip("pipe_valve_open_when_methane", &[("d0", &pa), ("d1", &v)]);
    c.go(4);
    assert_eq!(v.get("On"), 1.0);
    pa.set("RatioMethane", 0.0);
    c.go(4);
    assert_eq!(v.get("On"), 0.0);
}

#[test]
fn pipe_valve_open_when_clean() {
    let pa = analyzer(20.0, 50.0, &[("RatioMethane", 0.0), ("RatioSteam", 0.0)]);
    let v = switchable(&[]);
    let mut c = chip("pipe_valve_open_when_clean", &[("d0", &pa), ("d1", &v)]);
    c.go(4);
    assert_eq!(v.get("On"), 1.0);
    pa.set("RatioSteam", 0.01);
    c.go(4);
    assert_eq!(v.get("On"), 0.0);
    pa.set("RatioSteam", 0.0);
    pa.set("Pressure", 0.5);
    c.go(4);
    assert_eq!(v.get("On"), 0.0, "needs > 1 kPa");
}

#[test]
fn pipe_methane_purge_valve() {
    let pa = analyzer(20.0, 100.0, &[("RatioMethane", 0.5), ("RatioOxygen", 0.1)]);
    let v = switchable(&[]);
    let mut c = chip("pipe_methane_purge_valve", &[("d0", &pa), ("d1", &v)]);
    c.go(4);
    assert_eq!(v.get("On"), 1.0, "0.1 < 0.33 * 0.5");
    pa.set("RatioOxygen", 0.2);
    c.go(4);
    assert_eq!(v.get("On"), 0.0);
    pa.set("RatioOxygen", 0.1);
    c.go(4);
    pa.set("Error", 1.0);
    c.go(4);
    assert_eq!((v.get("On"), c.status()), (0.0, 9.0), "analyzer error closes it");
}

#[test]
fn pipe_methane_purge_vent() {
    let pa = analyzer(20.0, 100.0, &[("RatioMethane", 0.5), ("RatioOxygen", 0.1)]);
    let v = switchable(&[("Mode", 1.0)]);
    let mut c = chip("pipe_methane_purge_vent", &[("d0", &pa), ("d1", &v)]);
    c.go(4);
    assert_eq!(read(&v, &["Mode", "On", "Open"]), [0.0, 1.0, 1.0]);
    pa.set("RatioOxygen", 0.4);
    c.go(4);
    assert_eq!(v.get("On"), 0.0);
}

#[test]
fn power_generator_on_methane() {
    let (pa, g) = (analyzer(20.0, 100.0, &[("RatioMethane", 0.0)]), switchable(&[]));
    let mut c = chip("power_generator_on_methane", &[("d0", &pa), ("d1", &g)]);
    c.go(4);
    assert_eq!(g.get("On"), 0.0);
    pa.set("RatioMethane", 0.01);
    c.go(4);
    assert_eq!(g.get("On"), 1.0);
}

#[test]
fn landing_pad_methane_unload() {
    let pa = analyzer(20.0, 1000.0, &[]);
    let pad = dev(&[("RatioMethane", 1.0), ("On", 0.0)]);
    let valve = switchable(&[("Lock", 1.0)]);
    let mut c = chip("landing_pad_methane_unload", &[("d0", &pa), ("d1", &pad), ("d2", &valve)]);
    c.go(4);
    assert_eq!(
        (pad.get("On"), valve.get("On"), valve.get("Lock"), c.status()),
        (1.0, 1.0, 0.0, 10.0)
    );
    for (kpa, on, status, why) in [
        (25000.0, 0.0, 30.0, "cutoff"),
        (19500.0, 0.0, 30.0, "stays cut off above 19 MPa"),
        (18000.0, 1.0, 10.0, "re-arms"),
    ] {
        pa.set("Pressure", kpa);
        c.go(4);
        assert_eq!((pad.get("On"), c.status()), (on, status), "{why}");
    }
    pad.set("RatioMethane", 0.5);
    c.go(4);
    assert_eq!((pad.get("On"), c.status()), (0.0, 20.0), "impure gas");
    c.set_pin("d3", &dev(&[("Setting", 1.0)]));
    c.go(4);
    assert_eq!((pad.get("On"), c.status()), (1.0, 40.0), "manual override");
}

#[test]
fn liquid_pipe_purge_lever() {
    let lever = dev(&[("Open", 1.0)]);
    let reader = dev(&[("Pressure", 5.0), ("Error", 0.0)]);
    let (valve, vnt, outlet) = (switchable(&[]), switchable(&[]), switchable(&[]));
    let led = dev(&[("On", 0.0), ("Color", 0.0)]);
    let pins = [
        ("d0", &lever),
        ("d1", &reader),
        ("d2", &valve),
        ("d3", &vnt),
        ("d4", &outlet),
        ("d5", &led),
    ];
    let mut c = chip("liquid_pipe_purge_lever", &pins);
    c.go(4);
    assert_eq!(
        [valve.get("On"), vnt.get("On"), outlet.get("On"), led.get("Color")],
        [1.0, 1.0, 1.0, 4.0],
        "red"
    );
    lever.set("Open", 0.0);
    c.go(4);
    assert_eq!((valve.get("On"), led.get("Color")), (0.0, 5.0), "yellow");
    lever.set("Open", 1.0);
    reader.set("Pressure", 0.0);
    c.go(4);
    assert_eq!((valve.get("On"), led.get("Color")), (0.0, 2.0), "green");
}

// ------------------------------------------------------- power, suit, display, logistics

#[test]
fn power_generator_on_low_battery() {
    let gen_ = switchable(&[]);
    let bats: Vec<_> = [0.2, 0.3]
        .map(|r| share(Device::new(&[("Ratio", r)]).prefab("StructureBatteryLarge")))
        .into();
    let mut c =
        bats.iter().fold(chip("power_generator_on_low_battery", &[("d0", &gen_)]), |c, b| c.net(b));
    c.go(4);
    assert_eq!(gen_.get("On"), 1.0, "mean 0.25 < 0.30");
    bats[0].set("Ratio", 0.5);
    c.go(4);
    assert_eq!(gen_.get("On"), 1.0, "keeps charging until 80%");
    bats.iter().for_each(|b| b.set("Ratio", 0.85));
    c.go(4);
    assert_eq!(gen_.get("On"), 0.0);
    bats[0].set("Ratio", 0.5);
    c.go(4);
    assert_eq!(gen_.get("On"), 0.0, "30..80% band holds off");
    c.network.clear();
    c.go(4);
    assert_eq!(gen_.get("On"), 0.0, "no batteries: fail-safe OFF");
}

#[test]
fn suit_helmet_auto_open_respects_a_manual_close() {
    let suit = dev(&[("TemperatureExternal", 20.0 + K), ("PressureExternal", 100.0)]);
    let helmet = dev(&[("Open", 0.0), ("Lock", 0.0)]);
    let mut c = Chip::new(script("suit_helmet_auto_open")).pin("d0", &helmet).pin("db", &suit);
    c.go(4);
    assert_eq!(helmet.get("Open"), 1.0);
    helmet.set("Open", 0.0); // player closes it
    c.go(6);
    assert_eq!(helmet.get("Open"), 0.0);
    suit.set("PressureExternal", 50.0); // unsafe
    c.go(4);
    assert_eq!(helmet.get("Open"), 0.0);
    suit.set("PressureExternal", 100.0); // safe again: auto-open
    c.go(4);
    assert_eq!(helmet.get("Open"), 1.0);
    suit.set("TemperatureExternal", 50.0 + K);
    c.go(4);
    assert_eq!(helmet.get("Open"), 0.0);
}

#[test]
fn display_clock_from_sun() {
    let led = || {
        share(
            Device::new(&[("On", 0.0), ("Mode", 0.0), ("Setting", 0.0)])
                .prefab("StructureConsoleLED5"),
        )
    };
    let (hrs, mins) = (led(), led());
    // In-game at sunrise (2026-11-22), flat sensor, top to 0: H 4, V 81. Sun 9 deg up.
    let day = share(
        Device::new(&[("Horizontal", 4.0), ("Vertical", 81.0), ("On", 0.0)])
            .prefab("StructureDaylightSensor"),
    );
    let mut c = Chip::new(script("display_clock_from_sun"))
        .pin("d0", &hrs)
        .pin("d1", &mins)
        .pin("d3", &day);
    c.go(4);
    let pair = |a: char, b: char| f64::from(a as u32 * 256 + b as u32);
    let shows = |h: &str, m: &str| {
        let p = |t: &str| pair(t.as_bytes()[0] as char, t.as_bytes()[1] as char);
        (p(h), p(m))
    };
    let now = || (hrs.get("Setting"), mins.get("Setting"));
    assert_eq!(hrs.get("Mode"), 10.0);
    assert_eq!(now(), shows("06", "39"), "the in-game sunrise reading is early morning");
    assert_eq!((day.get("On"), c.status()), (1.0, 1.0), "sensor switched on; running");
    // The sun `theta` deg along its path from sunrise (sensor H 0), path tilted by `tilt`.
    let sun = |theta: f64, tilt: f64| {
        let (t, k) = (theta.to_radians(), tilt.to_radians());
        let (x, y, z) = (t.cos(), t.sin() * k.sin(), t.sin() * k.cos());
        (y.atan2(x).to_degrees(), z.acos().to_degrees())
    };
    for tilt in [0.0, 25.0] {
        for (theta, want) in [
            (10.1, ("06", "40")),
            (60.1, ("10", "00")), // H still 0 when untilted: azimuth alone stalls here
            (100.1, ("12", "40")),
            (200.1, ("19", "20")),
            (300.1, ("02", "00")),
        ] {
            let (h, v) = sun(theta, tilt);
            day.set("Horizontal", h);
            day.set("Vertical", v);
            c.go(2);
            assert_eq!(now(), shows(want.0, want.1), "{theta} deg along a {tilt} deg path");
        }
    }
    let wrong = share(Device::new(&[("Horizontal", 0.0)]).prefab("StructureGasSensor"));
    c.set_pin("d3", &wrong);
    c.go(4);
    assert_eq!(
        (c.status(), hrs.get("Setting")),
        (9.0, pair('0', '2')),
        "wrong device: clock holds"
    );
    let (h2, m2) = (led(), led());
    c.set_pin("d0", &h2);
    c.set_pin("d1", &m2);
    c.set_pin("d3", &day);
    c.go(4);
    assert_eq!(
        (h2.get("Setting"), m2.get("Setting")),
        shows("02", "00"),
        "displays replaced while waiting are written"
    );
    let sent = (h2.writes_of("Setting").len(), m2.writes_of("Setting").len());
    c.go(20);
    let now = (h2.writes_of("Setting").len(), m2.writes_of("Setting").len());
    assert_eq!(now, sent, "no rewrite while the time holds");
    let path =
        ic10_tools::repo::root().join("scripts/display_clock_from_sun/display_clock_from_sun.ic10");
    let src = std::fs::read_to_string(path).expect("script is readable");
    for (from, to, h, want) in [
        ("define RISE_DEG 0", "define RISE_DEG 90", 94.0, shows("06", "39")),
        ("define SHIFT_MIN 0", "define SHIFT_MIN 30", 4.0, shows("07", "09")),
    ] {
        let (h3, m3) = (led(), led());
        let sensor = share(
            Device::new(&[("Horizontal", h), ("Vertical", 81.0), ("On", 1.0)])
                .prefab("StructureDaylightSensor"),
        );
        let mut c = Chip::new(parse(&src.replace(from, to)))
            .pin("d0", &h3)
            .pin("d1", &m3)
            .pin("d3", &sensor);
        c.go(4);
        assert_eq!((h3.get("Setting"), m3.get("Setting")), want, "{to}");
    }
    // Optional wall sensor on d2: the housing shows wall-guess height minus flat height.
    // In-game at sunrise (2026-11-22): flat H 4, V 81 (9 deg up); wall facing 0: H 22, V 171.
    for (turn, want, why) in [
        ("define WALL_TURN 0", -1.0, "the guess with WALL_TURN 0 is within 1 deg"),
        ("define WALL_TURN 180", -17.0, "WALL_TURN 180 turns the guess"),
    ] {
        let (h3, m3) = (led(), led());
        let sensor = |h: f64, v: f64| {
            share(
                Device::new(&[("Horizontal", h), ("Vertical", v), ("On", 1.0)])
                    .prefab("StructureDaylightSensor"),
            )
        };
        let (flat, wall) = (sensor(4.0, 81.0), sensor(22.0, 171.0));
        let mut c = Chip::new(parse(&src.replace("define WALL_TURN 0", turn)))
            .pin("d0", &h3)
            .pin("d1", &m3)
            .pin("d2", &wall)
            .pin("d3", &flat);
        c.go(4);
        assert_eq!(c.status(), want, "{why}");
        assert_eq!((h3.get("Setting"), m3.get("Setting")), shows("06", "39"), "clock unchanged");
        let gas = share(Device::new(&[("Horizontal", 0.0)]).prefab("StructureGasSensor"));
        c.set_pin("d2", &gas);
        c.go(4);
        assert_eq!(c.status(), 1.0, "a wrong device on d2 is ignored");
    }
}

#[test]
fn vending_export_gives_up_when_the_item_never_arrives() {
    let occupied = |n: usize| (0..n).map(|_| fields(&[("Occupied", 0.0)])).collect::<Vec<_>>();
    let vend = share(Device::new(&[("On", 0.0), ("RequestHash", 0.0)]).slots(occupied(2)));
    let mut stack_slots = occupied(2);
    stack_slots.push(fields(&[("Quantity", 0.0), ("MaxQuantity", 50.0)]));
    let stk = share(
        Device::new(&[
            ("On", 0.0),
            ("Mode", 0.0),
            ("ClearMemory", 0.0),
            ("Setting", 0.0),
            ("Output", 0.0),
        ])
        .slots(stack_slots),
    );
    let sort = share(
        Device::new(&[
            ("On", 0.0),
            ("Mode", 0.0),
            ("ClearMemory", 0.0),
            ("Output", 0.0),
            ("ImportCount", 0.0),
        ])
        .slots(occupied(3)),
    );
    let (mh, mc) = (dev(&[("Setting", 12345.0)]), dev(&[("Setting", 10.0)]));
    let pins = [("d0", &vend), ("d1", &stk), ("d2", &sort), ("d3", &mh), ("d4", &mc)];
    let mut c = chip("vending_export_exact_count", &pins);
    c.go(10);
    assert_eq!((c.status(), mc.get("Setting")), (1.0, 0.0), "job started");
    assert_eq!(vend.get("RequestHash"), 12345.0);
    c.go(60);
    assert_eq!(c.status(), 2.0, "gave up after the timeout instead of hanging");
}

// ------------------------------------------------------------------------- solar

/// (prefab hash, half turn added because the type is built flipped)
const PANELS: [(f64, f64); 6] = [
    (-2045627372.0, 0.0), // StructureSolarPanel
    (-934345724.0, 0.0),  // StructureSolarPanelReinforced (Heavy)
    (-539224550.0, 0.0),  // StructureSolarPanelDual
    (-1545574413.0, 0.0), // StructureSolarPanelDualReinforced (Heavy Dual)
    (939649277.0, 180.0), // StructureSolarPanel1x5 (moves in-game, user)
    // Heavy 1x5: PrefabHash read in-game by the user; prefab name unknown.
    (-2049226859.0, 180.0),
];

/// A sensor plus one panel of every type in every direction group, and one panel with
/// an unknown name that must never move.
/// (chip, sensor, (data-port direction, panel) list, stray panel)
type SolarRig = (Chip, Shared<Device>, Vec<(f64, Shared<Device>)>, Shared<Device>);

fn solar(h: f64, v: f64) -> SolarRig {
    let sensor = share(
        Device::new(&[("Horizontal", h), ("Vertical", v), ("On", 1.0), ("Mode", 0.0)])
            .prefab("StructureDaylightSensor"),
    );
    let panel = |prefab: f64, name: &str| {
        share(
            Device::new(&[("Horizontal", 0.0), ("Vertical", 0.0), ("PrefabHash", prefab)])
                .named(name),
        )
    };
    let mut panels = vec![];
    // 1x5 panels are built flipped: one named 0 has its data port at 180 (user, in-game).
    for (prefab, flip) in PANELS {
        for name in [0.0, 90.0, 180.0, 270.0] {
            panels.push(((name + flip) % 360.0, panel(prefab, &format!("{name}"))));
        }
    }
    let stray = panel(PANELS[0].0, "45");
    let chip =
        panels.iter().fold(chip("solar_panels_track_sun", &[("d0", &sensor)]), |c, p| c.net(&p.1));
    (chip.net(&stray), sensor, panels, stray)
}

#[test]
fn solar_panels_track_sun_aims_every_type_and_group() {
    // Sun at world 30 deg, 40 deg from the zenith (50 deg above the horizon).
    let (mut c, _, panels, stray) = solar(30.0, 40.0);
    c.go(4);
    assert_eq!(c.status(), 1.0, "day");
    for (port, p) in &panels {
        let want = (30.0 + 270.0 - port + 360.0) % 360.0; // local angle; data port is local 270
        assert_eq!(read(p, &["Horizontal", "Vertical"]), [want, 50.0], "port {port}");
    }
    assert_eq!(read(&stray, &["Horizontal", "Vertical"]), [0.0, 0.0], "unknown names untouched");
    let ticks: Vec<u64> = panels
        .iter()
        .flat_map(|(_, p)| p.borrow().writes.iter().map(|w| w.0).collect::<Vec<_>>())
        .collect();
    assert!(ticks.iter().all(|&t| t == ticks[0]), "one re-aim fits in one tick: {ticks:?}");
}

#[test]
fn solar_panels_track_sun_follows_the_sun_below_the_horizon_at_night() {
    let (mut c, sensor, panels, _) = solar(100.0, 20.0);
    c.go(4);
    sensor.set("Horizontal", 250.0);
    sensor.set("Vertical", 130.0); // 40 deg below the horizon
    c.go(4);
    assert_eq!(c.status(), 2.0, "night");
    let (port, p) = &panels[0];
    assert_eq!(*port, 0.0);
    assert_eq!(
        read(p, &["Horizontal", "Vertical"]),
        [(250.0 + 270.0) % 360.0, 15.0],
        "lowest tilt, facing the sun"
    );
    sensor.set("Vertical", 95.0);
    c.go(4);
    assert_eq!(c.status(), 2.0, "5 deg below the horizon is night");
    sensor.set("Vertical", 89.0);
    c.go(4);
    assert_eq!(
        (c.status(), p.get("Vertical")),
        (1.0, 15.0),
        "just above the horizon: clamped to 15"
    );
}

#[test]
fn solar_panels_track_sun_skips_tiny_moves_but_resends() {
    let (mut c, sensor, panels, _) = solar(30.0, 40.0);
    c.go(4);
    let p = &panels[0].1;
    let sent = p.writes_of("Horizontal").len();
    sensor.set("Horizontal", 30.2); // under STEP (0.5 deg)
    c.go(5);
    assert_eq!(p.writes_of("Horizontal").len(), sent, "no rewrite for a 0.2 deg move");
    sensor.set("Horizontal", 31.0); // 1 deg from the last aim
    c.go(2);
    assert_eq!(p.get("Horizontal"), 301.0, "a 1 deg move re-aims at once");
    let sent = p.writes_of("Horizontal").len();
    c.go(3);
    c.go(20);
    assert_eq!(p.writes_of("Horizontal").len(), sent + 1, "periodic resend reaches new panels");
    sensor.set("Horizontal", 359.9);
    c.go(4);
    sensor.set("Horizontal", 0.1); // wraps past north: a 0.2 deg move, not 359.8
    let before = p.writes_of("Horizontal").len();
    c.go(4);
    assert_eq!(p.writes_of("Horizontal").len(), before, "wrap-around is a small move");
}

#[test]
fn solar_panels_track_sun_rejects_a_wrong_sensor_and_turns_the_sensor_on() {
    let (mut c, sensor, panels, _) = solar(30.0, 40.0);
    sensor.set("On", 0.0);
    c.go(4);
    assert_eq!((sensor.get("On"), c.status()), (1.0, 1.0), "switched the sensor on");
    let wrong =
        share(Device::new(&[("Horizontal", 0.0), ("Vertical", 0.0)]).prefab("StructureGasSensor"));
    c.set_pin("d0", &wrong);
    let sent = panels[0].1.writes_of("Horizontal").len();
    c.go(30);
    assert_eq!(c.status(), 9.0, "wrong device on d0");
    assert_eq!(panels[0].1.writes_of("Horizontal").len(), sent, "panels left alone");
    assert_eq!(Chip::new(script("solar_panels_track_sun")).go(3).status(), 9.0, "no sensor");
}

// ------------------------------------------------------------------------- lights

/// Flat Daylight Sensor readings for clock time `hhmm` on a sun path through the zenith
/// that rises at sensor `Horizontal` 0 (06:00), as in `display_clock_from_sun`.
fn sun_at(hhmm: f64) -> (f64, f64) {
    let mins = (hhmm / 100.0).floor() * 60.0 + hhmm % 100.0 + 0.5;
    let t = ((mins - 360.0) / 4.0).to_radians();
    let (x, z) = (t.cos(), t.sin());
    (if x >= 0.0 { 0.0 } else { 180.0 }, z.acos().to_degrees())
}

#[test]
fn lights_on_when_dark() {
    let (h, v) = sun_at(1200.0);
    let sensor = share(
        Device::new(&[("Horizontal", h), ("Vertical", v), ("On", 0.0)])
            .prefab("StructureDaylightSensor"),
    );
    let light = |prefab: &str, on: f64| share(Device::new(&[("On", on)]).prefab(prefab));
    let lights: Vec<_> = [
        "StructureWallLight",
        "StructureWallLightBattery",
        "StructureLightLong",
        "StructureLightLongAngled",
        "StructureLightLongWide",
        "StructureLightRound",
        "StructureLightRoundAngled",
        "StructureLightRoundSmall",
    ]
    .iter()
    .map(|p| light(p, 1.0))
    .collect();
    let grow = light("StructureGrowLight", 1.0);
    let mut c =
        lights.iter().fold(chip("lights_on_when_dark", &[("d0", &sensor)]), |c, l| c.net(l));
    c = c.net(&grow);
    let on = |ls: &[Shared<Device>]| ls.iter().map(|l| l.get("On")).collect::<Vec<_>>();
    c.go(4);
    assert_eq!(sensor.get("On"), 1.0, "switched the sensor on");
    assert_eq!((c.status(), on(&lights)), (0.0, vec![0.0; 8]), "midday: every light type off");
    assert_eq!(grow.get("On"), 1.0, "other devices are left alone");
    for (hhmm, want) in [
        (1759.0, 0.0),
        (1800.0, 1.0),
        (2300.0, 1.0),
        (0.0, 1.0),
        (300.0, 1.0),
        (629.0, 1.0),
        (630.0, 0.0),
        (1000.0, 0.0),
    ] {
        let (h, v) = sun_at(hhmm);
        sensor.set("Horizontal", h);
        sensor.set("Vertical", v);
        c.go(4);
        assert_eq!((c.status(), on(&lights)), (want, vec![want; 8]), "{hhmm}: on 18:00-06:30");
    }
    let sent = lights[0].writes_of("On").len();
    c.go(20);
    assert_eq!(lights[0].writes_of("On").len(), sent, "no rewrite while nothing changes");
    lights[3].set("On", 1.0);
    c.go(2);
    assert_eq!(lights[3].get("On"), 0.0, "a light switched on by hand in daytime goes off");
    let wrong = share(Device::new(&[("Vertical", 120.0)]).prefab("StructureGasSensor"));
    c.set_pin("d0", &wrong);
    c.go(6);
    assert_eq!((c.status(), lights[0].get("On")), (9.0, 0.0), "wrong device: lights hold");
}

#[test]
fn lights_on_when_dark_settings() {
    let path =
        ic10_tools::repo::root().join("scripts/lights_on_when_dark/lights_on_when_dark.ic10");
    let src = std::fs::read_to_string(path).expect("script is readable");
    // (setting edits, clock time) -> lamp On
    let run = |edits: &[(&str, &str)], hhmm: f64, rise: f64| {
        let text = edits.iter().fold(src.clone(), |t, (from, to)| t.replace(from, to));
        let (h, v) = sun_at(hhmm);
        let sensor = share(
            Device::new(&[("Horizontal", h + rise), ("Vertical", v), ("On", 1.0)])
                .prefab("StructureDaylightSensor"),
        );
        let lamp = share(Device::new(&[("On", 0.0)]).prefab("StructureWallLight"));
        let mut c = Chip::new(parse(&text)).pin("d0", &sensor).net(&lamp);
        c.go(4);
        lamp.get("On")
    };
    let night_shift =
        [("define ON_AT 1800", "define ON_AT 100"), ("define OFF_AT 630", "define OFF_AT 500")];
    for (hhmm, want) in [(30.0, 0.0), (100.0, 1.0), (459.0, 1.0), (500.0, 0.0), (1900.0, 0.0)] {
        assert_eq!(run(&night_shift, hhmm, 0.0), want, "{hhmm}: ON_AT before OFF_AT, 01:00-05:00");
    }
    let rise = [("define RISE_DEG 0", "define RISE_DEG 90")];
    assert_eq!(run(&rise, 1900.0, 90.0), 1.0, "RISE_DEG turns the sun path like the clock");
    assert_eq!(run(&rise, 1700.0, 90.0), 0.0, "RISE_DEG: 17:00 is day");
    assert_eq!(run(&rise, 615.0, 90.0), 1.0, "RISE_DEG: 06:15, before OFF_AT, still on");
    let shift = [("define SHIFT_MIN 0", "define SHIFT_MIN 120")];
    assert_eq!(run(&shift, 1700.0, 0.0), 1.0, "SHIFT_MIN 120: 17:00 reads 19:00");
}

#[test]
fn power_apc_on_high_battery() {
    let apc = switchable(&[]);
    let bat = |prefab: &str, max: f64| {
        share(Device::new(&[("Charge", 0.0), ("Maximum", max)]).prefab(prefab))
    };
    // A large battery holds 10x a small one, so it dominates the total.
    let (small, large) = (bat("StructureBattery", 100.0), bat("StructureBatteryLarge", 1000.0));
    let mut c = chip("power_apc_on_high_battery", &[("d0", &apc)]).net(&small).net(&large);
    for (s, l, want, why) in [
        (100.0, 500.0, 0.0, "55%: off"),
        (100.0, 650.0, 0.0, "per-battery average 82.5%, but the total is 68.2%: off"),
        (0.0, 800.0, 1.0, "72.7% of the total: on"),
        (100.0, 600.0, 1.0, "63.6%: inside the band, stays on"),
        (0.0, 650.0, 0.0, "59.1%: off"),
        (100.0, 700.0, 1.0, "72.7%: on again"),
    ] {
        small.set("Charge", s);
        large.set("Charge", l);
        c.go(4);
        assert_eq!((apc.get("On"), c.status()), (want, want), "{why}");
    }
    let sent = apc.writes_of("On").len();
    c.go(20);
    assert_eq!(apc.writes_of("On").len(), sent, "no rewrite while nothing changes");
    c.network.clear();
    c.go(4);
    assert_eq!((apc.get("On"), c.status()), (0.0, 2.0), "no batteries: APC off");
    assert_eq!(Chip::new(script("power_apc_on_high_battery")).go(3).status(), 9.0, "no APC");
}
