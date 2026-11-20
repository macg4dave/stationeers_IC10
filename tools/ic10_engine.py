"""IC10 parser, static analyser and deterministic simulator (stdlib only).

Used by tools/ic10_lint.py (static checks) and tests/ (behaviour scenarios).

Execution model (matches the in-game chip as far as this repo relies on it)
- Line numbers are 0-based source lines; comments, blanks and labels count.
- One game tick runs up to 128 lines, or until `yield` / `sleep`. Label,
  comment and blank lines use a slot too (they are stepped over one per line).
- 2 ticks per second, so `sleep 1` pauses 2 ticks.
- `alias` executes at runtime (scripts may re-bind an alias); `define` and
  labels are resolved before the program runs.
- Absolute branches (j, beq, bnez, ...) jump to a line number or label.
  Relative branches (br*, jr) add an offset to the current line.
- `and`/`or`/`xor`/`nor`/`not` are bitwise on integer-truncated values.
- Reading an unset pin, an unknown field, or jumping outside the program
  raises ChipError, which is how the in-game chip halts with an error.

Simulator assumptions (not verified against game source; documented so tests
do not silently depend on them)
- Batch reads (`lb`, `lbn`) with no matching device return 0.
- Hash = signed CRC-32 of the UTF-8 string (verified for prefab hashes:
  e.g. HASH("StructureActiveVent") == -1129453144).
"""

from __future__ import annotations

import math
import re
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional

MAX_LINES = 128
MAX_COLS = 90
MAX_BYTES = 4096
INSTRUCTIONS_PER_TICK = 128
TICKS_PER_SECOND = 2

# ----------------------------------------------------------------- instruction set
# Operand kinds: r=register target, v=value, d=device, t=logic type,
# s=slot logic type, m=batch mode, g=reagent mode, a=absolute target,
# o=relative offset, n=new name, x=alias target (register or device), k=define value
OPCODES: Dict[str, str] = {
    "alias": "nx", "define": "nk",
    "move": "rv",
    **{op: "rvv" for op in ("add", "sub", "mul", "div", "mod", "min", "max",
                            "and", "or", "xor", "nor", "atan2", "pow")},
    **{op: "rv" for op in ("abs", "sin", "cos", "tan", "asin", "acos", "atan",
                           "sqrt", "floor", "ceil", "round", "trunc", "exp", "log",
                           "not", "rand")},
    **{op: "rvv" for op in ("seq", "sne", "slt", "sgt", "sge", "sle", "sap", "sna")},
    **{op: "rv" for op in ("seqz", "snez", "sltz", "sgtz", "sgez", "slez", "snan",
                           "snanz")},
    "select": "rvvv",
    "j": "a", "jal": "a", "jr": "o",
    **{op: "vva" for op in ("beq", "bne", "blt", "bgt", "ble", "bge")},
    **{op: "va" for op in ("beqz", "bnez", "bltz", "bgtz", "blez", "bgez")},
    **{op: "vvo" for op in ("breq", "brne", "brlt", "brgt", "brle", "brge")},
    **{op: "vo" for op in ("breqz", "brnez", "brltz", "brgtz", "brlez", "brgez")},
    **{op: "vva" for op in ("beqal", "bneal", "bltal", "bgtal", "bleal", "bgeal")},
    **{op: "va" for op in ("beqzal", "bnezal", "bltzal", "bgtzal", "blezal", "bgezal")},
    "bdns": "da", "bdse": "da", "bdnsal": "da", "bdseal": "da",
    "brdns": "do", "brdse": "do",
    "yield": "", "sleep": "v", "hcf": "",
    "l": "rdt", "s": "dtv", "ls": "rdvs", "lr": "rdgv",
    "lb": "rvtm", "lbn": "rvvtm", "sb": "vtv", "sbn": "vvtv",
    "lbs": "rvvsm", "lbns": "rvvvsm", "sbs": "vvsv",
    "push": "v", "pop": "r", "peek": "r",
}
RELATIVE_BRANCHES = {op for op, sig in OPCODES.items() if sig.endswith("o")}
ABSOLUTE_BRANCHES = {op for op, sig in OPCODES.items() if sig.endswith("a")}
UNCONDITIONAL = {"j", "jr"}
LINKING = {op for op in OPCODES if op == "jal" or op.endswith("al")}

CONSTANTS = {
    "pi": math.pi, "deg2rad": math.pi / 180, "rad2deg": 180 / math.pi,
    "epsilon": 4.94065645841247e-324, "nan": math.nan,
    "pinf": math.inf, "ninf": -math.inf,
}
BATCH_MODES = {"Average": 0, "Sum": 1, "Minimum": 2, "Maximum": 3}
REAGENT_MODES = {"Contents": 0, "Required": 1, "Recipe": 2}
REGISTERS = {f"r{i}": i for i in range(16)} | {"r16": 16, "r17": 17, "sp": 16, "ra": 17}
DEVICE_PINS = {f"d{i}" for i in range(6)} | {"db"}

_TOKEN_RE = re.compile(r'HASH\("[^"]*"\)|\S+')
_LABEL_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):$")
_HASH_RE = re.compile(r'^HASH\("([^"]*)"\)$')


def ic10_hash(text: str) -> int:
    v = zlib.crc32(text.encode("utf-8"))
    return v - 2**32 if v >= 2**31 else v


# ------------------------------------------------------------------------ parsing


@dataclass
class Line:
    index: int            # 0-based source line
    raw: str
    op: Optional[str] = None
    args: List[str] = field(default_factory=list)
    label: Optional[str] = None


@dataclass
class Program:
    path: Optional[Path]
    text: str
    lines: List[Line]
    labels: Dict[str, int]
    defines: Dict[str, str]
    aliases: Dict[str, str]           # last static binding seen (for analysis)

    @property
    def instructions(self) -> List[Line]:
        return [ln for ln in self.lines if ln.op]


def parse(text: str, path: Optional[Path] = None) -> Program:
    lines: List[Line] = []
    labels: Dict[str, int] = {}
    defines: Dict[str, str] = {}
    aliases: Dict[str, str] = {}
    for i, raw in enumerate(text.splitlines()):
        code = raw.split("#", 1)[0].strip()
        ln = Line(index=i, raw=raw)
        if code:
            m = _LABEL_RE.match(code)
            if m:
                ln.label = m.group(1)
                labels.setdefault(ln.label, i)
            else:
                toks = _TOKEN_RE.findall(code)
                ln.op, ln.args = toks[0], toks[1:]
                if ln.op == "define" and len(ln.args) == 2:
                    defines[ln.args[0]] = ln.args[1]
                elif ln.op == "alias" and len(ln.args) == 2:
                    aliases[ln.args[0]] = ln.args[1]
        lines.append(ln)
    return Program(path, text, lines, labels, defines, aliases)


def load(path: Path) -> Program:
    return parse(Path(path).read_text(encoding="utf-8"), Path(path))


def literal(token: str) -> Optional[float]:
    """Numeric literal, HASH("..."), $hex, %binary or named constant; else None."""
    m = _HASH_RE.match(token)
    if m:
        return float(ic10_hash(m.group(1)))
    if token in CONSTANTS:
        return CONSTANTS[token]
    try:
        if token.startswith("$"):
            return float(int(token[1:].replace("_", ""), 16))
        if token.startswith("%"):
            return float(int(token[1:].replace("_", ""), 2))
        return float(token)
    except ValueError:
        return None


# ------------------------------------------------------------------- simulation


class ChipError(RuntimeError):
    """The chip would halt with an error in-game."""


@dataclass
class Device:
    """A simulated device. Unknown fields raise unless `permissive`."""

    fields: Dict[str, float] = field(default_factory=dict)
    prefab: str = ""
    name: str = ""
    slots: List[Dict[str, float]] = field(default_factory=list)
    reagents: Dict[str, Dict[int, float]] = field(default_factory=dict)
    permissive: bool = False
    writes: List[tuple] = field(default_factory=list)   # (tick, field, value)

    def __post_init__(self) -> None:
        if self.prefab and "PrefabHash" not in self.fields:
            self.fields["PrefabHash"] = float(ic10_hash(self.prefab))
        if self.name and "NameHash" not in self.fields:
            self.fields["NameHash"] = float(ic10_hash(self.name))

    @property
    def prefab_hash(self) -> int:
        return int(self.fields.get("PrefabHash", 0))

    @property
    def name_hash(self) -> int:
        return int(self.fields.get("NameHash", 0))

    def read(self, f: str) -> float:
        if f in self.fields:
            return self.fields[f]
        if self.permissive:
            return 0.0
        raise ChipError(f"device has no readable field {f!r}")

    def write(self, f: str, value: float, tick: int) -> None:
        if f not in self.fields and not self.permissive:
            raise ChipError(f"device has no writable field {f!r}")
        self.fields[f] = value
        self.writes.append((tick, f, value))

    def read_slot(self, slot: int, f: str) -> float:
        if 0 <= slot < len(self.slots) and f in self.slots[slot]:
            return self.slots[slot][f]
        if self.permissive:
            return 0.0
        raise ChipError(f"device slot {slot} has no field {f!r}")

    def writes_of(self, f: str) -> List[float]:
        return [v for _, name, v in self.writes if name == f]


class Chip:
    """Runs one Program against pins d0..d5/db and a data network."""

    def __init__(self, program: Program, pins: Optional[Dict[str, Device]] = None,
                 network: Iterable[Device] = (), housing: Optional[Device] = None):
        self.program = program
        self.pins: Dict[str, Optional[Device]] = {p: None for p in DEVICE_PINS}
        self.pins["db"] = housing or Device({"Setting": 0, "On": 1}, prefab="StructureCircuitHousing")
        for k, v in (pins or {}).items():
            self.pins[k] = v
        self.network: List[Device] = list(network)
        self.reg = [0.0] * 18
        self.stack = [0.0] * 512
        self.alias: Dict[str, str] = {}
        self.pc = 0
        self.tick = 0
        self.sleep_ticks = 0
        self.executed = 0

    # -- operand resolution -------------------------------------------------
    def _name(self, token: str, depth: int = 0) -> str:
        """Resolve alias chains to r*/d* names (or return token)."""
        if depth > 8:
            raise ChipError(f"alias loop at {token!r}")
        if token in self.alias:
            return self._name(self.alias[token], depth + 1)
        return token

    def _reg_index(self, token: str) -> int:
        name = self._name(token)
        if name in REGISTERS:
            return REGISTERS[name]
        m = re.fullmatch(r"r+(\d+)", name)          # indirect rrN
        if m and name.startswith("rr"):
            idx = int(name[1:].lstrip("r") or 0)
            for _ in range(name.count("r") - 2):
                idx = int(self.reg[idx])
            return int(self.reg[idx])
        raise ChipError(f"line {self.pc}: {token!r} is not a register")

    def value(self, token: str) -> float:
        name = self._name(token)
        if name in REGISTERS:
            return self.reg[REGISTERS[name]]
        if token in self.program.defines:
            v = self.program.defines[token]
            lit = literal(v)
            return lit if lit is not None else self.value(v)
        if token in self.program.labels:
            return float(self.program.labels[token])
        lit = literal(name)
        if lit is None:
            raise ChipError(f"line {self.pc}: cannot resolve value {token!r}")
        return lit

    def device(self, token: str) -> Device:
        name = self._name(token)
        if name not in DEVICE_PINS:
            raise ChipError(f"line {self.pc}: {token!r} is not a device")
        dev = self.pins.get(name)
        if dev is None:
            raise ChipError(f"line {self.pc}: device {name} is not set")
        return dev

    def _is_set(self, token: str) -> bool:
        name = self._name(token)
        return name in DEVICE_PINS and self.pins.get(name) is not None

    def _set(self, token: str, value: float) -> None:
        self.reg[self._reg_index(token)] = float(value)

    def _batch(self, prefab: float, name: Optional[float] = None) -> List[Device]:
        out = [d for d in self.network if d.prefab_hash == int(prefab)]
        if name is not None:
            out = [d for d in out if d.name_hash == int(name)]
        return out

    @staticmethod
    def _reduce(values: List[float], mode: float) -> float:
        if not values:
            return 0.0
        mode = int(mode)
        if mode == 0:
            return sum(values) / len(values)
        if mode == 1:
            return sum(values)
        if mode == 2:
            return min(values)
        return max(values)

    def _mode(self, token: str, table: Dict[str, int]) -> float:
        return float(table[token]) if token in table else self.value(token)

    # -- execution -------------------------------------------------------------
    def run(self, ticks: int = 1) -> "Chip":
        for _ in range(ticks):
            self.step_tick()
        return self

    def step_tick(self) -> None:
        self.tick += 1
        if self.sleep_ticks > 0:
            self.sleep_ticks -= 1
            return
        n = len(self.program.lines)
        for _ in range(INSTRUCTIONS_PER_TICK):
            if not 0 <= self.pc < n:
                raise ChipError(f"program counter {self.pc} outside 0..{n - 1}")
            ln = self.program.lines[self.pc]
            if not ln.op:
                self.pc += 1
                continue
            self.executed += 1
            if self._exec(ln):
                return

    def _jump(self, target: float, link: bool = False) -> None:
        if link:
            self.reg[17] = float(self.pc + 1)
        self.pc = int(target)

    def _exec(self, ln: Line) -> bool:
        """Execute one instruction. Returns True when the tick ends."""
        op, a = ln.op, ln.args
        sig = OPCODES.get(op)
        if sig is None:
            raise ChipError(f"line {ln.index}: unknown instruction {op!r}")
        if len(a) != len(sig):
            raise ChipError(f"line {ln.index}: {op} expects {len(sig)} operands, got {len(a)}")
        v = self.value
        nxt = self.pc + 1

        if op == "alias":
            self.alias[a[0]] = a[1]
        elif op == "define":
            pass
        elif op == "move":
            self._set(a[0], v(a[1]))
        elif op in ("add", "sub", "mul", "div", "mod", "min", "max", "pow", "atan2"):
            x, y = v(a[1]), v(a[2])
            if op == "add": r = x + y
            elif op == "sub": r = x - y
            elif op == "mul": r = x * y
            elif op == "div": r = x / y if y else (math.copysign(math.inf, x) if x else math.nan)
            elif op == "mod": r = ((x % y) + y) % y if y else math.nan
            elif op == "min": r = min(x, y)
            elif op == "max": r = max(x, y)
            elif op == "pow": r = x ** y
            else: r = math.atan2(x, y)
            self._set(a[0], r)
        elif op in ("and", "or", "xor", "nor"):
            x, y = int(v(a[1])), int(v(a[2]))
            r = {"and": x & y, "or": x | y, "xor": x ^ y, "nor": ~(x | y)}[op]
            self._set(a[0], r)
        elif op in ("abs", "sin", "cos", "tan", "asin", "acos", "atan", "sqrt",
                    "floor", "ceil", "round", "trunc", "exp", "log", "not"):
            x = v(a[1])
            fn = {"abs": abs, "sin": math.sin, "cos": math.cos, "tan": math.tan,
                  "asin": math.asin, "acos": math.acos, "atan": math.atan,
                  "sqrt": math.sqrt, "floor": math.floor, "ceil": math.ceil,
                  "round": round, "trunc": math.trunc, "exp": math.exp,
                  "log": math.log, "not": lambda q: ~int(q)}[op]
            self._set(a[0], fn(x))
        elif op in ("seq", "sne", "slt", "sgt", "sge", "sle"):
            x, y = v(a[1]), v(a[2])
            r = {"seq": x == y, "sne": x != y, "slt": x < y,
                 "sgt": x > y, "sge": x >= y, "sle": x <= y}[op]
            self._set(a[0], 1.0 if r else 0.0)
        elif op in ("seqz", "snez", "sltz", "sgtz", "sgez", "slez", "snan", "snanz"):
            x = v(a[1])
            r = {"seqz": x == 0, "snez": x != 0, "sltz": x < 0, "sgtz": x > 0,
                 "sgez": x >= 0, "slez": x <= 0, "snan": math.isnan(x),
                 "snanz": not math.isnan(x)}[op]
            self._set(a[0], 1.0 if r else 0.0)
        elif op == "select":
            self._set(a[0], v(a[2]) if v(a[1]) != 0 else v(a[3]))
        elif op in ("j", "jal"):
            self._jump(v(a[0]), link=op == "jal")
            return False
        elif op == "jr":
            self._jump(self.pc + v(a[0]))
            return False
        elif op in ABSOLUTE_BRANCHES or op in RELATIVE_BRANCHES:
            base = op[2:] if op.startswith("br") else op[1:]
            link = base.endswith("al") and op not in ("bdns", "bdse")
            if link:
                base = base[:-2]
            if base in ("dns", "dse"):
                cond = (not self._is_set(a[0])) if base == "dns" else self._is_set(a[0])
            else:
                args = [v(x) for x in a[:-1]]
                cond = _branch_cond(base, args)
            if cond:
                tgt = v(a[-1])
                self._jump(self.pc + tgt if op in RELATIVE_BRANCHES else tgt, link=link)
                return False
        elif op == "yield":
            self.pc = nxt
            return True
        elif op == "sleep":
            self.sleep_ticks = max(0, math.ceil(v(a[0]) * TICKS_PER_SECOND) - 1)
            self.pc = nxt
            return True
        elif op == "hcf":
            raise ChipError(f"line {ln.index}: hcf")
        elif op == "l":
            self._set(a[0], self.device(a[1]).read(a[2]))
        elif op == "s":
            self.device(a[0]).write(a[1], v(a[2]), self.tick)
        elif op == "ls":
            self._set(a[0], self.device(a[1]).read_slot(int(v(a[2])), a[3]))
        elif op == "lr":
            dev = self.device(a[1])
            mode = a[2] if a[2] in REAGENT_MODES else next(
                k for k, n in REAGENT_MODES.items() if n == int(v(a[2])))
            self._set(a[0], dev.reagents.get(mode, {}).get(int(v(a[3])), 0.0))
        elif op == "lb":
            devs = self._batch(v(a[1]))
            self._set(a[0], self._reduce([d.read(a[2]) for d in devs], self._mode(a[3], BATCH_MODES)))
        elif op == "lbn":
            devs = self._batch(v(a[1]), v(a[2]))
            self._set(a[0], self._reduce([d.read(a[3]) for d in devs], self._mode(a[4], BATCH_MODES)))
        elif op == "sb":
            for d in self._batch(v(a[0])):
                d.write(a[1], v(a[2]), self.tick)
        elif op == "sbn":
            for d in self._batch(v(a[0]), v(a[1])):
                d.write(a[2], v(a[3]), self.tick)
        elif op == "push":
            sp = int(self.reg[16])
            if sp >= len(self.stack):
                raise ChipError("stack overflow")
            self.stack[sp] = v(a[0])
            self.reg[16] = sp + 1
        elif op in ("pop", "peek"):
            sp = int(self.reg[16]) - 1
            if sp < 0:
                raise ChipError("stack underflow")
            self._set(a[0], self.stack[sp])
            if op == "pop":
                self.reg[16] = sp
        else:
            raise ChipError(f"line {ln.index}: {op} not supported by simulator")
        self.pc = nxt
        return False

    # -- test helpers ------------------------------------------------------------
    def r(self, token: str) -> float:
        return self.value(token)

    @property
    def status(self) -> float:
        return self.pins["db"].fields.get("Setting", 0.0)


def _branch_cond(base: str, args: List[float]) -> bool:
    if base in ("eq", "ne", "lt", "gt", "le", "ge"):
        x, y = args
    else:
        x, y = args[0], 0.0
        base = base[:-1]
    return {"eq": x == y, "ne": x != y, "lt": x < y, "gt": x > y,
            "le": x <= y, "ge": x >= y}[base]


# ---------------------------------------------------------------------- analysis


@dataclass
class Finding:
    level: str          # error | warning | info
    code: str
    line: int           # 1-based for humans
    message: str

    def format(self, path: str) -> str:
        return f"{path}:{self.line}: {self.level} {self.code}: {self.message}"


BUILTIN_LOGIC_TYPES = {
    "Power", "Open", "Mode", "Error", "Lock", "On", "Setting", "Ratio", "Charge",
    "Maximum", "PrefabHash", "NameHash", "ReferenceId", "Activate", "RequiredPower",
    "Horizontal", "Vertical", "Temperature", "Pressure", "Color", "Idle",
    "ImportCount", "ExportCount", "ClearMemory", "Output", "RecipeHash",
    "RequestHash", "Quantity", "Occupied", "OccupantHash", "MaxQuantity",
    "Damage", "Class", "LineNumber", "SolarAngle", "PowerActual", "PowerPotential",
}
SLOT_LOGIC_TYPES = {
    "Occupied", "OccupantHash", "Quantity", "MaxQuantity", "Damage", "Class",
    "PrefabHash", "Mature", "Seeding", "Health", "Growth", "Efficiency", "Charge",
    "ChargeRatio", "Open", "On", "Lock", "SortingClass", "ReferenceId",
    "FilterType", "Pressure", "Temperature", "Volume",
}


def known_logic_types(catalog_dir: Optional[Path] = None) -> set:
    import json
    names = set(BUILTIN_LOGIC_TYPES)
    root = catalog_dir or Path(__file__).resolve().parents[1] / "catalog" / "devices"
    for fp in root.glob("*.json"):
        io = json.loads(fp.read_text(encoding="utf-8")).get("io", {})
        for k in ("parameters", "outputs"):
            names.update(f["name"] for f in io.get(k, []) if " " not in f["name"])
    return names


def analyse(prog: Program, logic_types: Optional[set] = None) -> List[Finding]:
    out: List[Finding] = []
    add = lambda lvl, code, ln, msg: out.append(Finding(lvl, code, ln + 1, msg))
    logic_types = logic_types if logic_types is not None else known_logic_types()

    # size limits
    raw = prog.text.encode("utf-8")
    if len(prog.lines) > MAX_LINES:
        add("error", "E020", MAX_LINES, f"{len(prog.lines)} lines (max {MAX_LINES})")
    for ln in prog.lines:
        if len(ln.raw) > MAX_COLS:
            add("error", "E021", ln.index, f"{len(ln.raw)} chars (max {MAX_COLS})")
    if len(raw) > MAX_BYTES:
        add("error", "E022", 0, f"{len(raw)} bytes (max {MAX_BYTES})")

    seen_labels: Dict[str, int] = {}
    for ln in prog.lines:
        if ln.label:
            if ln.label in seen_labels:
                add("error", "E006", ln.index, f"duplicate label {ln.label!r}")
            seen_labels[ln.label] = ln.index
            if ln.label in logic_types or ln.label in DEVICE_PINS or ln.label in REGISTERS:
                add("warning", "W010", ln.index,
                    f"label {ln.label!r} shadows a LogicType/register/pin name")

    names = set(prog.defines) | set(prog.aliases) | set(prog.labels)

    def is_value(tok: str) -> bool:
        return (tok in REGISTERS or tok in names or literal(tok) is not None
                or re.fullmatch(r"r{2,}\d+", tok) is not None)

    reg_alias = {k for k, v in prog.aliases.items() if v in REGISTERS}
    dev_alias = {k: v for k, v in prog.aliases.items() if v in DEVICE_PINS}
    guarded_pins = set()
    used_pins: Dict[str, int] = {}

    for ln in prog.instructions:
        op, a = ln.op, ln.args
        sig = OPCODES.get(op)
        if sig is None:
            add("error", "E001", ln.index, f"unknown instruction {op!r}")
            continue
        if len(a) != len(sig):
            add("error", "E002", ln.index, f"{op} expects {len(sig)} operands, got {len(a)}")
            continue
        for kind, tok in zip(sig, a):
            if kind in "vk" and not is_value(tok):
                add("error", "E013", ln.index, f"unknown identifier {tok!r}")
            elif kind == "r" and tok not in REGISTERS and tok not in reg_alias:
                add("error", "E014", ln.index, f"{tok!r} is not a register")
            elif kind == "d":
                pin = dev_alias.get(tok, tok)
                if pin not in DEVICE_PINS:
                    add("error", "E015", ln.index, f"{tok!r} is not a device pin")
                elif op in ("l", "s", "ls", "lr"):
                    used_pins.setdefault(pin, ln.index)
                elif op.startswith(("bdns", "bdse", "brdns", "brdse")):
                    guarded_pins.add(pin)
            elif kind == "t" and tok not in logic_types:
                add("warning", "W007", ln.index, f"LogicType {tok!r} not in catalog")
            elif kind == "s" and tok not in SLOT_LOGIC_TYPES and tok not in logic_types:
                add("warning", "W007", ln.index, f"slot LogicType {tok!r} not known")
            elif kind == "m" and tok not in BATCH_MODES and not is_value(tok):
                add("error", "E016", ln.index, f"unknown batch mode {tok!r}")
            elif kind == "g" and tok not in REAGENT_MODES and not is_value(tok):
                add("error", "E017", ln.index, f"unknown reagent mode {tok!r}")
            elif kind == "a":
                if tok in prog.labels or tok in REGISTERS or tok in reg_alias:
                    pass
                elif literal(tok) is not None or tok in prog.defines:
                    add("warning", "W005", ln.index,
                        f"{op} jumps to absolute line {tok}; did you mean br{op[1:]} "
                        f"(relative) or a label?")
                else:
                    add("error", "E003", ln.index, f"undefined jump target {tok!r}")
            elif kind == "o" and tok in prog.labels:
                add("error", "E004", ln.index,
                    f"{op} is relative but got label {tok!r} (line {prog.labels[tok]}); "
                    f"use b{op[2:]} for a label")
        if op == "define" and len(a) == 2 and literal(a[1]) is None:
            add("warning", "W012", ln.index,
                f"define {a[0]} refers to {a[1]!r}, not a literal; verify in-game")

    for pin, idx in sorted(used_pins.items()):
        if pin != "db" and pin not in guarded_pins:
            add("info", "I011", idx, f"{pin} is used but never guarded by bdns/bdse")

    # unreachable code after an unconditional jump, until the next label
    dead = False
    for ln in prog.lines:
        if ln.label:
            dead = False
            continue
        if not ln.op:
            continue
        if dead and ln.op not in ("alias", "define"):
            add("warning", "W009", ln.index, "unreachable after unconditional jump")
            dead = False
        if ln.op in UNCONDITIONAL or (ln.op == "j" and ln.args):
            dead = ln.op in UNCONDITIONAL

    # registers read before their first write (program order) -- a common
    # sign of a missing load, e.g. testing `cur` before `l cur dev On`.
    first_write: Dict[int, int] = {}
    first_read: Dict[int, tuple] = {}
    for ln in prog.instructions:
        sig = OPCODES.get(ln.op) or ""
        if len(sig) != len(ln.args):
            continue
        for kind, tok in zip(sig, ln.args):
            name = prog.aliases.get(tok, tok)
            if name not in REGISTERS or name in ("sp", "ra", "r16", "r17"):
                continue
            idx = REGISTERS[name]
            if kind == "r":
                first_write.setdefault(idx, ln.index)
            elif kind in "va":
                first_read.setdefault(idx, (ln.index, tok))
    for idx, (line, tok) in first_read.items():
        if idx not in first_write or first_write[idx] > line:
            add("info", "I008", line,
                f"{tok!r} is read before any write in program order "
                f"(relies on 0 at boot or on a previous loop)")
    return sorted(out, key=lambda f: (f.line, f.code))
