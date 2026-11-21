//! IC10 parser, static analyser and tick simulator.
//!
//! Execution model (matches the in-game chip as far as this repo relies on it):
//! - Line numbers are 0-based source lines; comments, blanks and labels count.
//! - One tick runs up to 128 lines, or until `yield` / `sleep`. Label, comment and
//!   blank lines use a slot too.
//! - 2 ticks per second, so `sleep 1` pauses 2 ticks.
//! - `alias` runs at runtime (a script may re-bind it); `define` and labels are
//!   resolved before the program runs.
//! - `j`, `beq`, `bnez`, ... jump to an absolute line or label; `br*` and `jr` add an
//!   offset to the current line.
//! - `and`/`or`/`xor`/`nor`/`not` are bitwise on integer-truncated values.
//! - Reading an unset pin or an unknown field, or running off the program, halts the
//!   chip: `Chip::halted` holds the reason, as the in-game chip shows an error.
//!
//! Simulator assumptions (not verified against game source):
//! - Batch reads (`lb`, `lbn`) with no matching device return 0.
//! - Hash = signed CRC-32 of the UTF-8 text (verified for prefab hashes).

use regex::Regex;
use std::cell::RefCell;
use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::path::Path;
use std::rc::Rc;
use std::sync::LazyLock;

pub const MAX_LINES: usize = 128;
pub const MAX_COLS: usize = 90;
pub const MAX_BYTES: usize = 4096;
pub const LINES_PER_TICK: usize = 128;
pub const TICKS_PER_SECOND: f64 = 2.0;

/// Signed CRC-32, the game's `HASH("...")`.
pub fn hash(text: &str) -> i32 {
    crc32fast::hash(text.as_bytes()) as i32
}

// ------------------------------------------------------------------ instruction set

/// Operand kinds: r register target, v value, d device, t logic type, s slot logic
/// type, m batch mode, g reagent mode, a absolute target, o relative offset,
/// n new name, x alias target, k define value.
pub fn signature(op: &str) -> Option<&'static str> {
    Some(match op {
        "alias" => "nx",
        "define" => "nk",
        "move" => "rv",
        "add" | "sub" | "mul" | "div" | "mod" | "min" | "max" | "and" | "or" | "xor" | "nor"
        | "atan2" | "pow" | "seq" | "sne" | "slt" | "sgt" | "sge" | "sle" => "rvv",
        "abs" | "sin" | "cos" | "tan" | "asin" | "acos" | "atan" | "sqrt" | "floor" | "ceil"
        | "round" | "trunc" | "exp" | "log" | "not" | "rand" | "seqz" | "snez" | "sltz"
        | "sgtz" | "sgez" | "slez" | "snan" | "snanz" => "rv",
        "select" | "sap" | "sna" => "rvvv",
        "j" | "jal" => "a",
        "jr" => "o",
        "beq" | "bne" | "blt" | "bgt" | "ble" | "bge" | "beqal" | "bneal" | "bltal" | "bgtal"
        | "bleal" | "bgeal" => "vva",
        "beqz" | "bnez" | "bltz" | "bgtz" | "blez" | "bgez" | "beqzal" | "bnezal" | "bltzal"
        | "bgtzal" | "blezal" | "bgezal" => "va",
        "breq" | "brne" | "brlt" | "brgt" | "brle" | "brge" => "vvo",
        "breqz" | "brnez" | "brltz" | "brgtz" | "brlez" | "brgez" => "vo",
        "bdns" | "bdse" | "bdnsal" | "bdseal" => "da",
        "brdns" | "brdse" => "do",
        "yield" | "hcf" => "",
        "sleep" | "push" => "v",
        "pop" | "peek" => "r",
        "l" => "rdt",
        "s" => "dtv",
        "ls" => "rdvs",
        "lr" => "rdgv",
        "lb" => "rvtm",
        "lbn" => "rvvtm",
        "sb" => "vtv",
        "sbn" => "vvtv",
        "lbs" => "rvvsm",
        "lbns" => "rvvvsm",
        "sbs" => "vvsv",
        _ => return None,
    })
}

const BATCH_MODES: [&str; 4] = ["Average", "Sum", "Minimum", "Maximum"];
const REAGENT_MODES: [&str; 3] = ["Contents", "Required", "Recipe"];

fn constant(tok: &str) -> Option<f64> {
    use std::f64::consts::PI;
    Some(match tok {
        "pi" => PI,
        "deg2rad" => PI / 180.0,
        "rad2deg" => 180.0 / PI,
        "epsilon" => 4.94065645841247e-324,
        "nan" => f64::NAN,
        "pinf" => f64::INFINITY,
        "ninf" => f64::NEG_INFINITY,
        _ => return None,
    })
}

/// `r0..r17`, `sp` (r16), `ra` (r17).
pub fn register(tok: &str) -> Option<usize> {
    match tok {
        "sp" => Some(16),
        "ra" => Some(17),
        _ => tok
            .strip_prefix('r')
            .and_then(|n| n.parse::<usize>().ok())
            .filter(|&i| i < 18 && !tok[1..].starts_with('+')),
    }
}

/// Indirect register `rrN`, `rrrN`, ...: returns (depth, N).
fn indirect(tok: &str) -> Option<(usize, usize)> {
    let digits = tok.trim_start_matches('r');
    let depth = tok.len() - digits.len();
    (depth >= 2 && digits.bytes().all(|b| b.is_ascii_digit()) && !digits.is_empty())
        .then(|| digits.parse().ok().map(|n| (depth, n)))
        .flatten()
}

pub fn is_pin(tok: &str) -> bool {
    matches!(tok, "d0" | "d1" | "d2" | "d3" | "d4" | "d5" | "db")
}

/// Numeric literal, `HASH("...")`, `$hex`, `%binary` or a named constant.
pub fn literal(tok: &str) -> Option<f64> {
    if let Some(name) = tok.strip_prefix("HASH(\"").and_then(|t| t.strip_suffix("\")")) {
        return Some(f64::from(hash(name)));
    }
    if let Some(c) = constant(tok) {
        return Some(c);
    }
    let radix = |digits: &str, base| i64::from_str_radix(&digits.replace('_', ""), base).ok();
    match tok.as_bytes().first() {
        Some(b'$') => radix(&tok[1..], 16).map(|v| v as f64),
        Some(b'%') => radix(&tok[1..], 2).map(|v| v as f64),
        _ => tok.parse::<f64>().ok(),
    }
}

// ---------------------------------------------------------------------- parsing

#[derive(Debug, Clone)]
pub struct Line {
    pub index: usize,
    pub raw: String,
    pub op: Option<String>,
    pub args: Vec<String>,
    pub label: Option<String>,
}

#[derive(Debug, Clone)]
pub struct Program {
    pub text: String,
    pub lines: Vec<Line>,
    pub labels: HashMap<String, usize>,
    pub defines: HashMap<String, String>,
    /// Last static binding of each alias (for analysis only).
    pub aliases: HashMap<String, String>,
}

static TOKEN: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r#"HASH\("[^"]*"\)|\S+"#).expect("constant regex"));
static LABEL: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^[A-Za-z_][A-Za-z0-9_]*:$").expect("constant regex"));

pub fn parse(text: &str) -> Program {
    let text = text.replace("\r\n", "\n");
    let mut prog = Program {
        text: text.clone(),
        lines: Vec::new(),
        labels: HashMap::new(),
        defines: HashMap::new(),
        aliases: HashMap::new(),
    };
    for (index, raw) in text.lines().enumerate() {
        let code = raw.split('#').next().unwrap_or("").trim();
        let mut line = Line { index, raw: raw.to_string(), op: None, args: vec![], label: None };
        if LABEL.is_match(code) {
            let name = code.trim_end_matches(':').to_string();
            prog.labels.entry(name.clone()).or_insert(index);
            line.label = Some(name);
        } else if !code.is_empty() {
            let mut toks = TOKEN.find_iter(code).map(|m| m.as_str().to_string());
            line.op = toks.next();
            line.args = toks.collect();
            if let ([name, value], Some(op)) = (line.args.as_slice(), line.op.as_deref()) {
                match op {
                    "define" => drop(prog.defines.insert(name.clone(), value.clone())),
                    "alias" => drop(prog.aliases.insert(name.clone(), value.clone())),
                    _ => {}
                }
            }
        }
        prog.lines.push(line);
    }
    prog
}

/// Parse a file; an unreadable file parses as an empty program and fails its tests.
pub fn load(path: &Path) -> Program {
    parse(&std::fs::read_to_string(path).unwrap_or_default())
}

// --------------------------------------------------------------------- devices

pub type Fields = BTreeMap<String, f64>;

pub fn fields(pairs: &[(&str, f64)]) -> Fields {
    pairs.iter().map(|(k, v)| (k.to_string(), *v)).collect()
}

/// A simulated device. Unknown fields halt the chip unless `permissive`.
#[derive(Debug, Clone, Default)]
pub struct Device {
    pub fields: Fields,
    pub slots: Vec<Fields>,
    /// (reagent mode 0..2, reagent hash) -> amount.
    pub reagents: BTreeMap<(usize, i64), f64>,
    pub permissive: bool,
    /// (tick, field, value) for every write.
    pub writes: Vec<(u64, String, f64)>,
}

impl Device {
    pub fn new(pairs: &[(&str, f64)]) -> Self {
        Device { fields: fields(pairs), ..Default::default() }
    }
    /// A device that accepts any field and reads 0 for unknown ones.
    pub fn stub() -> Self {
        Device { permissive: true, ..Default::default() }
    }
    pub fn prefab(mut self, name: &str) -> Self {
        self.fields.entry("PrefabHash".into()).or_insert(f64::from(hash(name)));
        self
    }
    pub fn named(mut self, name: &str) -> Self {
        self.fields.entry("NameHash".into()).or_insert(f64::from(hash(name)));
        self
    }
    pub fn slots(mut self, slots: Vec<Fields>) -> Self {
        self.slots = slots;
        self
    }
    /// Field value, NaN when the device has no such field.
    pub fn get(&self, f: &str) -> f64 {
        self.fields.get(f).copied().unwrap_or(f64::NAN)
    }
    pub fn set(&mut self, f: &str, v: f64) {
        self.fields.insert(f.into(), v);
    }
    pub fn writes_of(&self, f: &str) -> Vec<f64> {
        self.writes.iter().filter(|w| w.1 == f).map(|w| w.2).collect()
    }
    pub fn read_field(&self, f: &str) -> Option<f64> {
        self.fields.get(f).copied().or(self.permissive.then_some(0.0))
    }
    pub fn write_field(&mut self, f: &str, v: f64, tick: u64) -> bool {
        let ok = self.permissive || self.fields.contains_key(f);
        if ok {
            self.set(f, v);
            self.writes.push((tick, f.into(), v));
        }
        ok
    }
    fn hash_of(&self, f: &str) -> i64 {
        self.fields.get(f).copied().unwrap_or(0.0) as i64
    }
}

/// Anything a chip can talk to. Override `read`/`write` to model a device that
/// reacts (see the satellite dish in `tests/trader_dish.rs`).
pub trait Logic {
    fn device(&self) -> &Device;
    fn device_mut(&mut self) -> &mut Device;
    fn read(&mut self, f: &str) -> Option<f64> {
        self.device().read_field(f)
    }
    fn write(&mut self, f: &str, v: f64, tick: u64) -> bool {
        self.device_mut().write_field(f, v, tick)
    }
}

impl Logic for Device {
    fn device(&self) -> &Device {
        self
    }
    fn device_mut(&mut self) -> &mut Device {
        self
    }
}

pub type Shared<T> = Rc<RefCell<T>>;
pub type Pin = Shared<dyn Logic>;

pub fn share<T>(t: T) -> Shared<T> {
    Rc::new(RefCell::new(t))
}

// ------------------------------------------------------------------- simulation

/// Runs one program against pins d0..d5/db and a data network.
pub struct Chip {
    pub program: Rc<Program>,
    pub pins: BTreeMap<String, Pin>,
    pub network: Vec<Pin>,
    pub reg: [f64; 18],
    pub stack: Vec<f64>,
    pub alias: HashMap<String, String>,
    pub pc: i64,
    pub tick: u64,
    pub sleep: u64,
    pub executed: u64,
    /// Why the chip stopped, as the in-game chip would show an error.
    pub halted: Option<String>,
}

impl Chip {
    pub fn new(program: Program) -> Self {
        let housing: Pin =
            share(Device::new(&[("Setting", 0.0), ("On", 1.0)]).prefab("StructureCircuitHousing"));
        Chip {
            program: Rc::new(program),
            pins: BTreeMap::from([("db".to_string(), housing)]),
            network: vec![],
            reg: [0.0; 18],
            stack: vec![0.0; 512],
            alias: HashMap::new(),
            pc: 0,
            tick: 0,
            sleep: 0,
            executed: 0,
            halted: None,
        }
    }
    pub fn pin<T: Logic + 'static>(mut self, name: &str, dev: &Shared<T>) -> Self {
        self.set_pin(name, dev);
        self
    }
    pub fn set_pin<T: Logic + 'static>(&mut self, name: &str, dev: &Shared<T>) {
        let pin: Pin = dev.clone();
        self.pins.insert(name.into(), pin);
    }
    pub fn net<T: Logic + 'static>(mut self, dev: &Shared<T>) -> Self {
        let pin: Pin = dev.clone();
        self.network.push(pin);
        self
    }
    /// Chip reset: program restarts, devices and network stay.
    pub fn reset(&mut self) {
        let program = self.program.clone();
        let pins = std::mem::take(&mut self.pins);
        let network = std::mem::take(&mut self.network);
        *self = Chip { program, pins, network, ..Chip::new(parse("")) };
    }
    /// The IC Housing's `Setting` (the status code every script reports).
    pub fn status(&self) -> f64 {
        let setting = |d: &Pin| d.borrow().device().fields.get("Setting").copied();
        self.pins.get("db").and_then(setting).unwrap_or(0.0)
    }
    pub fn run(&mut self, ticks: u64) -> &mut Self {
        (0..ticks).for_each(|_| self.step_tick());
        self
    }

    pub fn step_tick(&mut self) {
        self.tick += 1;
        if self.halted.is_some() {
            return;
        }
        if self.sleep > 0 {
            self.sleep -= 1;
            return;
        }
        let program = self.program.clone();
        for _ in 0..LINES_PER_TICK {
            let Some(line) = usize::try_from(self.pc).ok().and_then(|pc| program.lines.get(pc))
            else {
                let last = program.lines.len() as i64 - 1;
                return self.halt(format!("program counter {} outside 0..{last}", self.pc));
            };
            match (&line.op, line.args.as_slice()) {
                (None, _) => self.pc += 1,
                (Some(op), args) => {
                    self.executed += 1;
                    if self.exec(op, args) || self.halted.is_some() {
                        return;
                    }
                }
            }
        }
    }

    fn halt(&mut self, why: String) {
        if self.halted.is_none() {
            self.halted = Some(format!("line {}: {why}", self.pc));
        }
    }

    fn name(&mut self, tok: &str) -> String {
        let mut name = tok.to_string();
        for _ in 0..9 {
            match self.alias.get(&name) {
                Some(next) => name = next.clone(),
                None => return name,
            }
        }
        self.halt(format!("alias loop at {tok:?}"));
        name
    }

    fn reg_slot(&self, name: &str) -> Option<usize> {
        if let Some(i) = register(name) {
            return Some(i);
        }
        let Some((depth, mut idx)) = indirect(name) else { return None };
        for _ in 1..depth {
            let Some(&v) = self.reg.get(idx) else { return None };
            idx = v as usize;
        }
        (idx < 18).then_some(idx)
    }

    fn value(&mut self, tok: &str) -> f64 {
        self.value_at(tok, 0)
    }

    fn value_at(&mut self, tok: &str, depth: u8) -> f64 {
        let name = self.name(tok);
        if let Some(i) = self.reg_slot(&name) {
            return self.reg[i];
        }
        let program = self.program.clone();
        if let Some(def) = program.defines.get(tok) {
            return match (literal(def), depth < 8) {
                (Some(v), _) => v,
                (None, true) => self.value_at(def, depth + 1),
                (None, false) => {
                    self.halt(format!("define loop at {tok:?}"));
                    f64::NAN
                }
            };
        }
        if let Some(&line) = program.labels.get(tok) {
            return line as f64;
        }
        literal(&name).unwrap_or_else(|| {
            self.halt(format!("cannot resolve value {tok:?}"));
            f64::NAN
        })
    }

    fn put(&mut self, tok: &str, v: f64) {
        let name = self.name(tok);
        match self.reg_slot(&name) {
            Some(i) => self.reg[i] = v,
            None => self.halt(format!("{tok:?} is not a register")),
        }
    }

    fn pin_of(&mut self, tok: &str) -> Option<Pin> {
        let name = self.name(tok);
        if !is_pin(&name) {
            self.halt(format!("{tok:?} is not a device"));
            return None;
        }
        let pin = self.pins.get(&name).cloned();
        if pin.is_none() {
            self.halt(format!("device {name} is not set"));
        }
        pin
    }

    fn is_set(&mut self, tok: &str) -> bool {
        let name = self.name(tok);
        is_pin(&name) && self.pins.contains_key(&name)
    }

    fn batch(&self, prefab: f64, name: Option<f64>) -> Vec<Pin> {
        let matches = |d: &Device| {
            d.hash_of("PrefabHash") == prefab as i64
                && name.is_none_or(|n| d.hash_of("NameHash") == n as i64)
        };
        self.network.iter().filter(|p| matches(p.borrow().device())).cloned().collect()
    }

    fn batch_read(&mut self, devs: Vec<Pin>, field: &str, mode: &str) -> f64 {
        let mode = match BATCH_MODES.iter().position(|m| *m == mode) {
            Some(i) => i as f64,
            None => self.value(mode),
        };
        let mut values = Vec::with_capacity(devs.len());
        for d in devs {
            match d.borrow_mut().read(field) {
                Some(v) => values.push(v),
                None => self.halt(format!("device has no readable field {field:?}")),
            }
        }
        if values.is_empty() {
            return 0.0;
        }
        let sum: f64 = values.iter().sum();
        match mode as i64 {
            0 => sum / values.len() as f64,
            1 => sum,
            2 => values.iter().copied().fold(f64::INFINITY, f64::min),
            _ => values.iter().copied().fold(f64::NEG_INFINITY, f64::max),
        }
    }

    fn write_all(&mut self, devs: &[Pin], field: &str, v: f64) {
        if self.halted.is_some() {
            return;
        }
        let tick = self.tick;
        for d in devs {
            if !d.borrow_mut().write(field, v, tick) {
                self.halt(format!("device has no writable field {field:?}"));
            }
        }
    }

    fn jump(&mut self, target: f64, link: bool) {
        if link {
            self.reg[17] = (self.pc + 1) as f64;
        }
        self.pc = target as i64;
    }

    /// Run one instruction. Returns true when the tick ends.
    fn exec(&mut self, op: &str, a: &[String]) -> bool {
        let Some(sig) = signature(op) else {
            self.halt(format!("unknown instruction {op:?}"));
            return true;
        };
        if a.len() != sig.len() {
            self.halt(format!("{op} expects {} operands, got {}", sig.len(), a.len()));
            return true;
        }
        let a: Vec<&str> = a.iter().map(String::as_str).collect();
        let next = self.pc + 1;
        match op {
            "alias" => drop(self.alias.insert(a[0].into(), a[1].into())),
            "define" => {}
            "move" => {
                let x = self.value(a[1]);
                self.put(a[0], x);
            }
            "add" | "sub" | "mul" | "div" | "mod" | "min" | "max" | "pow" | "atan2" | "and"
            | "or" | "xor" | "nor" | "seq" | "sne" | "slt" | "sgt" | "sge" | "sle" => {
                let (x, y) = (self.value(a[1]), self.value(a[2]));
                self.put(a[0], binary(op, x, y));
            }
            "sap" | "sna" => {
                let (x, y, c) = (self.value(a[1]), self.value(a[2]), self.value(a[3]));
                let near = (x - y).abs() <= (c * x.abs().max(y.abs())).max(f64::EPSILON * 8.0);
                self.put(a[0], f64::from(u8::from(near == (op == "sap"))));
            }
            "select" => {
                let c = self.value(a[1]);
                let x = self.value(if c != 0.0 { a[2] } else { a[3] });
                self.put(a[0], x);
            }
            "j" | "jal" => {
                let t = self.value(a[0]);
                self.jump(t, op == "jal");
                return false;
            }
            "jr" => {
                let t = self.value(a[0]);
                self.jump(self.pc as f64 + t, false);
                return false;
            }
            "yield" => {
                self.pc = next;
                return true;
            }
            "sleep" => {
                let s = self.value(a[0]);
                self.sleep = ((s * TICKS_PER_SECOND).ceil() - 1.0).max(0.0) as u64;
                self.pc = next;
                return true;
            }
            "hcf" => self.halt("hcf".into()),
            "l" => {
                if let Some(d) = self.pin_of(a[1]) {
                    let v = d.borrow_mut().read(a[2]);
                    match v {
                        Some(v) => self.put(a[0], v),
                        None => self.halt(format!("device has no readable field {:?}", a[2])),
                    }
                }
            }
            "s" => {
                let dev = self.pin_of(a[0]);
                let v = self.value(a[2]);
                if let Some(d) = dev {
                    self.write_all(&[d], a[1], v);
                }
            }
            "ls" => {
                let dev = self.pin_of(a[1]);
                let slot = self.value(a[2]) as usize;
                let got = dev.and_then(|d| {
                    let d = d.borrow();
                    let dev = d.device();
                    dev.slots
                        .get(slot)
                        .and_then(|s| s.get(a[3]).copied())
                        .or(dev.permissive.then_some(0.0))
                });
                match got {
                    Some(v) => self.put(a[0], v),
                    None => self.halt(format!("device slot {slot} has no field {:?}", a[3])),
                }
            }
            "lr" => {
                let dev = self.pin_of(a[1]);
                let mode = match REAGENT_MODES.iter().position(|m| *m == a[2]) {
                    Some(i) => i,
                    None => self.value(a[2]) as usize,
                };
                let reagent = self.value(a[3]) as i64;
                let v = dev.map_or(0.0, |d| {
                    d.borrow().device().reagents.get(&(mode, reagent)).copied().unwrap_or(0.0)
                });
                self.put(a[0], v);
            }
            "lb" | "lbn" => {
                let prefab = self.value(a[1]);
                let name = (op == "lbn").then(|| self.value(a[2]));
                let rest = &a[a.len() - 2..];
                let devs = self.batch(prefab, name);
                let v = self.batch_read(devs, rest[0], rest[1]);
                self.put(a[0], v);
            }
            "sb" | "sbn" => {
                let prefab = self.value(a[0]);
                let name = (op == "sbn").then(|| self.value(a[1]));
                let v = self.value(a[a.len() - 1]);
                let devs = self.batch(prefab, name);
                self.write_all(&devs, a[a.len() - 2], v);
            }
            "push" => {
                let sp = self.reg[16] as usize;
                let v = self.value(a[0]);
                match self.stack.get_mut(sp) {
                    Some(slot) => {
                        *slot = v;
                        self.reg[16] = (sp + 1) as f64;
                    }
                    None => self.halt("stack overflow".into()),
                }
            }
            "pop" | "peek" => match (self.reg[16] as usize).checked_sub(1) {
                Some(sp) => {
                    let v = self.stack[sp];
                    self.put(a[0], v);
                    if op == "pop" {
                        self.reg[16] = sp as f64;
                    }
                }
                None => self.halt("stack underflow".into()),
            },
            _ if sig.ends_with('a') || sig.ends_with('o') => return self.branch(op, sig, &a),
            _ => match unary(op) {
                Some(f) => {
                    let x = self.value(a[1]);
                    self.put(a[0], f(x));
                }
                None => self.halt(format!("{op} is not simulated")),
            },
        }
        self.pc = next;
        false
    }

    fn branch(&mut self, op: &str, sig: &str, a: &[&str]) -> bool {
        let relative = sig.ends_with('o');
        let base = if relative { &op[2..] } else { &op[1..] };
        let (base, link) = match base.strip_suffix("al") {
            Some(b) => (b, true),
            None => (base, false),
        };
        let cond = match base {
            "dns" => !self.is_set(a[0]),
            "dse" => self.is_set(a[0]),
            _ => {
                let x = self.value(a[0]);
                match base.strip_suffix('z') {
                    Some(cmp) => compare(cmp, x, 0.0),
                    None => {
                        let y = self.value(a[1]);
                        compare(base, x, y)
                    }
                }
            }
        };
        match cond {
            true => {
                let t = self.value(a[a.len() - 1]);
                let target = if relative { self.pc as f64 + t } else { t };
                self.jump(target, link);
            }
            false => self.pc += 1,
        }
        false
    }
}

fn compare(cmp: &str, x: f64, y: f64) -> bool {
    match cmp {
        "eq" => x == y,
        "ne" => x != y,
        "lt" => x < y,
        "gt" => x > y,
        "le" => x <= y,
        _ => x >= y,
    }
}

fn binary(op: &str, x: f64, y: f64) -> f64 {
    let (i, j) = (x as i64, y as i64);
    let flag = |b: bool| f64::from(u8::from(b));
    match op {
        "add" => x + y,
        "sub" => x - y,
        "mul" => x * y,
        "div" => x / y,
        "mod" => ((x % y) + y) % y,
        "min" => x.min(y),
        "max" => x.max(y),
        "pow" => x.powf(y),
        "atan2" => x.atan2(y),
        "and" => (i & j) as f64,
        "or" => (i | j) as f64,
        "xor" => (i ^ j) as f64,
        "nor" => !(i | j) as f64,
        "seq" => flag(x == y),
        "sne" => flag(x != y),
        "slt" => flag(x < y),
        "sgt" => flag(x > y),
        "sge" => flag(x >= y),
        _ => flag(x <= y),
    }
}

fn unary(op: &str) -> Option<fn(f64) -> f64> {
    fn flag(b: bool) -> f64 {
        f64::from(u8::from(b))
    }
    Some(match op {
        "abs" => f64::abs,
        "sin" => f64::sin,
        "cos" => f64::cos,
        "tan" => f64::tan,
        "asin" => f64::asin,
        "acos" => f64::acos,
        "atan" => f64::atan,
        "sqrt" => f64::sqrt,
        "floor" => f64::floor,
        "ceil" => f64::ceil,
        "round" => f64::round_ties_even,
        "trunc" => f64::trunc,
        "exp" => f64::exp,
        "log" => f64::ln,
        "not" => |x| !(x as i64) as f64,
        "seqz" => |x| flag(x == 0.0),
        "snez" => |x| flag(x != 0.0),
        "sltz" => |x| flag(x < 0.0),
        "sgtz" => |x| flag(x > 0.0),
        "sgez" => |x| flag(x >= 0.0),
        "slez" => |x| flag(x <= 0.0),
        "snan" => |x| flag(x.is_nan()),
        "snanz" => |x| flag(!x.is_nan()),
        _ => return None,
    })
}

// --------------------------------------------------------------------- analysis

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum Level {
    Error,
    Warning,
    Info,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Finding {
    pub level: Level,
    pub code: &'static str,
    /// 1-based, for humans.
    pub line: usize,
    pub message: String,
}

impl Finding {
    pub fn format(&self, path: &str) -> String {
        let level = match self.level {
            Level::Error => "error",
            Level::Warning => "warning",
            Level::Info => "info",
        };
        format!("{path}:{}: {level} {}: {}", self.line, self.code, self.message)
    }
}

const BUILTIN_LOGIC_TYPES: &[&str] = &[
    "Power",
    "Open",
    "Mode",
    "Error",
    "Lock",
    "On",
    "Setting",
    "Ratio",
    "Charge",
    "Maximum",
    "PrefabHash",
    "NameHash",
    "ReferenceId",
    "Activate",
    "RequiredPower",
    "Horizontal",
    "Vertical",
    "Temperature",
    "Pressure",
    "Color",
    "Idle",
    "ImportCount",
    "ExportCount",
    "ClearMemory",
    "Output",
    "RecipeHash",
    "RequestHash",
    "Quantity",
    "Occupied",
    "OccupantHash",
    "MaxQuantity",
    "Damage",
    "Class",
    "LineNumber",
    "SolarAngle",
    "PowerActual",
    "PowerPotential",
];
const SLOT_LOGIC_TYPES: &[&str] = &[
    "Occupied",
    "OccupantHash",
    "Quantity",
    "MaxQuantity",
    "Damage",
    "Class",
    "PrefabHash",
    "Mature",
    "Seeding",
    "Health",
    "Growth",
    "Efficiency",
    "Charge",
    "ChargeRatio",
    "Open",
    "On",
    "Lock",
    "SortingClass",
    "ReferenceId",
    "FilterType",
    "Pressure",
    "Temperature",
    "Volume",
];

/// Built-in LogicTypes plus every parameter/output name in `catalog/devices/*.json`.
pub fn known_logic_types(catalog_devices: &Path) -> BTreeSet<String> {
    let mut names: BTreeSet<String> = BUILTIN_LOGIC_TYPES.iter().map(|s| s.to_string()).collect();
    let pattern = format!("{}/*.json", glob::Pattern::escape(&catalog_devices.to_string_lossy()));
    for path in glob::glob(&pattern).into_iter().flatten().flatten() {
        let text = std::fs::read_to_string(&path).unwrap_or_default();
        let json: serde_json::Value = serde_json::from_str(&text).unwrap_or_default();
        for key in ["parameters", "outputs"] {
            let list = json["io"][key].as_array().cloned().unwrap_or_default();
            let found = list.iter().filter_map(|f| f["name"].as_str());
            names.extend(found.filter(|n| !n.contains(' ')).map(String::from));
        }
    }
    names
}

pub fn analyse(prog: &Program, logic_types: &BTreeSet<String>) -> Vec<Finding> {
    let mut out = Vec::new();
    let mut add = |level, code, line: usize, message: String| {
        out.push(Finding { level, code, line: line + 1, message })
    };
    use Level::{Error, Info, Warning};

    let n_lines = prog.lines.len();
    if n_lines > MAX_LINES {
        add(Error, "E020", MAX_LINES, format!("{n_lines} lines (max {MAX_LINES})"));
    }
    for ln in &prog.lines {
        let cols = ln.raw.chars().count();
        if cols > MAX_COLS {
            add(Error, "E021", ln.index, format!("{cols} chars (max {MAX_COLS})"));
        }
    }
    if prog.text.len() > MAX_BYTES {
        add(Error, "E022", 0, format!("{} bytes (max {MAX_BYTES})", prog.text.len()));
    }

    let mut seen = BTreeSet::new();
    for (ln, label) in prog.lines.iter().filter_map(|l| l.label.as_ref().map(|n| (l, n))) {
        if !seen.insert(label) {
            add(Error, "E006", ln.index, format!("duplicate label {label:?}"));
        }
        if logic_types.contains(label) || is_pin(label) || register(label).is_some() {
            add(
                Warning,
                "W010",
                ln.index,
                format!("label {label:?} shadows a LogicType/register/pin name"),
            );
        }
    }

    let is_name = |t: &str| {
        prog.defines.contains_key(t) || prog.aliases.contains_key(t) || prog.labels.contains_key(t)
    };
    let is_value = |t: &str| {
        register(t).is_some() || is_name(t) || literal(t).is_some() || indirect(t).is_some()
    };
    let reg_alias = |t: &str| prog.aliases.get(t).is_some_and(|v| register(v).is_some());
    fn pin_of<'a>(prog: &'a Program, t: &'a str) -> &'a str {
        prog.aliases.get(t).filter(|v| is_pin(v)).map_or(t, |v| v.as_str())
    }
    let mut guarded = BTreeSet::new();
    let mut used: BTreeMap<&str, usize> = BTreeMap::new();
    let mut first_write: BTreeMap<usize, usize> = BTreeMap::new();
    let mut first_read: BTreeMap<usize, (usize, &str)> = BTreeMap::new();
    let mut dead = false;

    for ln in &prog.lines {
        if ln.label.is_some() {
            dead = false;
            continue;
        }
        let Some(op) = ln.op.as_deref() else { continue };
        let a = &ln.args;
        if dead && op != "alias" && op != "define" {
            add(Warning, "W009", ln.index, "unreachable after unconditional jump".into());
            dead = false;
        }
        dead |= op == "j" || op == "jr";
        let Some(sig) = signature(op) else {
            add(Error, "E001", ln.index, format!("unknown instruction {op:?}"));
            continue;
        };
        if a.len() != sig.len() {
            let msg = format!("{op} expects {} operands, got {}", sig.len(), a.len());
            add(Error, "E002", ln.index, msg);
            continue;
        }
        for (kind, tok) in sig.chars().zip(a.iter().map(String::as_str)) {
            match kind {
                'v' | 'k' if !is_value(tok) => {
                    add(Error, "E013", ln.index, format!("unknown identifier {tok:?}"))
                }
                'r' if register(tok).is_none() && !reg_alias(tok) => {
                    add(Error, "E014", ln.index, format!("{tok:?} is not a register"))
                }
                'd' => {
                    let pin = pin_of(prog, tok);
                    if !is_pin(pin) {
                        add(Error, "E015", ln.index, format!("{tok:?} is not a device pin"));
                    } else if matches!(op, "l" | "s" | "ls" | "lr") {
                        used.entry(pin).or_insert(ln.index);
                    } else if op.starts_with("bd") || op.starts_with("brd") {
                        guarded.insert(pin);
                    }
                }
                't' if !logic_types.contains(tok) => {
                    add(Warning, "W007", ln.index, format!("LogicType {tok:?} not in catalog"))
                }
                's' if !SLOT_LOGIC_TYPES.contains(&tok) && !logic_types.contains(tok) => {
                    add(Warning, "W007", ln.index, format!("slot LogicType {tok:?} not known"))
                }
                'm' if !BATCH_MODES.contains(&tok) && !is_value(tok) => {
                    add(Error, "E016", ln.index, format!("unknown batch mode {tok:?}"))
                }
                'g' if !REAGENT_MODES.contains(&tok) && !is_value(tok) => {
                    add(Error, "E017", ln.index, format!("unknown reagent mode {tok:?}"))
                }
                'a' if prog.labels.contains_key(tok)
                    || register(tok).is_some()
                    || reg_alias(tok) => {}
                'a' if literal(tok).is_some() || prog.defines.contains_key(tok) => {
                    let msg = format!(
                        "{op} jumps to absolute line {tok}; did you mean br{} (relative) or a label?",
                        &op[1..]
                    );
                    add(Warning, "W005", ln.index, msg)
                }
                'a' => add(Error, "E003", ln.index, format!("undefined jump target {tok:?}")),
                'o' if prog.labels.contains_key(tok) => {
                    let msg = format!(
                        "{op} is relative but got label {tok:?} (line {}); use b{} for a label",
                        prog.labels[tok],
                        &op[2..]
                    );
                    add(Error, "E004", ln.index, msg)
                }
                _ => {}
            }
            // registers read before their first write, in program order
            let name = prog.aliases.get(tok).map_or(tok, |v| v.as_str());
            if let Some(idx) = register(name).filter(|&i| i < 16) {
                match kind {
                    'r' => drop(first_write.entry(idx).or_insert(ln.index)),
                    'v' | 'a' => drop(first_read.entry(idx).or_insert((ln.index, tok))),
                    _ => {}
                }
            }
        }
        if op == "define" && literal(&a[1]).is_none() {
            let msg =
                format!("define {} refers to {:?}, not a literal; verify in-game", a[0], a[1]);
            add(Warning, "W012", ln.index, msg);
        }
    }

    for (pin, line) in used {
        if pin != "db" && !guarded.contains(pin) {
            add(Info, "I011", line, format!("{pin} is used but never guarded by bdns/bdse"));
        }
    }
    for (idx, (line, tok)) in first_read {
        if first_write.get(&idx).is_none_or(|&w| w > line) {
            let msg = format!(
                "{tok:?} is read before any write in program order (relies on 0 at boot or on a previous loop)"
            );
            add(Info, "I008", line, msg);
        }
    }
    out.sort_by(|a, b| (a.line, a.code).cmp(&(b.line, b.code)));
    out
}
