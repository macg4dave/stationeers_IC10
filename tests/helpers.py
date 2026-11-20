"""Shared helpers for IC10 behaviour tests (stdlib unittest only)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from ic10_engine import Chip, ChipError, Device, ic10_hash, load  # noqa: E402,F401

K = 273.15  # Kelvin offset


def known_defect(ref: str):
    """Mark a scenario that reproduces a defect listed in docs/engineering_audit.md.

    The fix commit for `ref` removes the marker, so the test then guards it.
    """
    import unittest

    def wrap(fn):
        fn.__doc__ = f"[{ref}] {fn.__doc__ or ''}"
        return unittest.expectedFailure(fn)
    return wrap


def script(rel: str):
    """Load a shipped script by repo-relative path (or scripts/<name> shorthand)."""
    p = ROOT / rel
    if p.is_dir() or not p.suffix:
        p = ROOT / "scripts" / rel / f"{Path(rel).name}.ic10"
    return load(p)


def analyzer(temp_c: float = 20.0, pressure_kpa: float = 100.0, **extra) -> Device:
    """Pipe Analyzer / Gas Sensor style reader."""
    return Device({"Temperature": temp_c + K, "Pressure": pressure_kpa, "Error": 0,
                   "On": 1, **extra}, prefab=extra.pop("prefab", "StructurePipeAnalysizer"))


def switchable(**fields) -> Device:
    """Device with On/Open/Lock/Mode/Setting fields (valve, vent, heater...)."""
    base = {"On": 0, "Open": 0, "Lock": 0, "Mode": 0, "Setting": 0}
    base.update(fields)
    return Device(base)


def memory(name: str, value: float = 0) -> Device:
    return Device({"Setting": value}, prefab="StructureLogicMemory", name=name)


def housing(name: str = "", setting: float = 0, on: float = 1) -> Device:
    return Device({"Setting": setting, "On": on}, prefab="StructureCircuitHousing", name=name)
