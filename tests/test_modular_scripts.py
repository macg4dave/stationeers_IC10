"""Behaviour scenarios for modular scripts/ (simulated, multi-chip lockstep).

Chips that share Logic Memory run tick-by-tick against one data network, so
the tests exercise the real cross-chip contracts (tokens, slots, housings).
"""

import unittest

from helpers import Chip, Device, housing, known_defect, memory, script

MOD = "modular scripts"


def lockstep(chips, ticks):
    for _ in range(ticks):
        for c in chips:
            c.step_tick()


class PotatoHarvieActuator(unittest.TestCase):
    def setUp(self):
        self.hv = Device({"Lock": 0, "On": 1, "Activate": 0, "ImportCount": 0,
                          "Plant": 0, "Harvest": 0}, prefab="StructureHarvie")
        self.lit = Device({"On": 0})
        self.ctype = Device({"Setting": 1})
        self.slot0 = Device({"Setting": 1 | 8})        # occupied + healthy, no daylight
        self.chip = Chip(script(f"{MOD}/PotatoHarvieTest/potato_harvie_test_worker_actuator.ic10"),
                         pins={"d0": self.hv, "d1": self.lit, "d2": self.ctype, "d3": self.slot0},
                         network=[self.hv])

    def test_light_dark_cycle(self):
        self.chip.run(20)
        self.assertEqual((self.lit.fields["On"], self.chip.status), (1, 212), "light phase")
        self.chip.run(650)
        self.assertEqual((self.lit.fields["On"], self.chip.status), (0, 213), "dark phase")
        self.chip.run(400)
        self.assertEqual(self.lit.fields["On"], 1, "cycle restarts after TOTAL_TICKS")

    def test_mode_off_turns_light_off(self):
        self.chip.run(20)
        self.ctype.fields["Setting"] = 0
        self.chip.run(3)
        self.assertEqual((self.lit.fields["On"], self.chip.status), (0, 200))

    def test_mature_plant_harvest_pulse_and_cooldown(self):
        self.slot0.fields["Setting"] = 1 | 2 | 8      # occupied + mature + healthy
        self.chip.run(30)
        pulses = [t for t, f, v in self.hv.writes if f == "Harvest" and v == 1]
        self.assertTrue(pulses, "mature plant must be harvested")
        self.assertEqual(self.hv.writes_of("Harvest")[:2], [1, 0], "pulse 1 then 0")
        gaps = [b - a for a, b in zip(pulses, pulses[1:])]
        self.assertTrue(all(g >= 5 for g in gaps), f"cooldown between pulses: {gaps}")


class SatTraderTrackMaster(unittest.TestCase):
    def setUp(self):
        self.dishw, self.alertw = housing(on=1), housing(on=1)
        self.ctok, self.ctype = Device({"Setting": 0}), Device({"Setting": 0})
        self.dial, self.led = Device({"Setting": 2}), Device({"Setting": 0, "On": 0})
        self.chip = Chip(script(f"{MOD}/SatTraderTrack/sat_trader_track_master.ic10"),
                         pins={"d0": self.dishw, "d1": self.alertw, "d2": self.ctok,
                               "d3": self.ctype, "d4": self.dial, "d5": self.led})

    def test_dial_change_publishes_token(self):
        self.chip.run(3)
        self.assertEqual((self.ctype.fields["Setting"], self.ctok.fields["Setting"]), (2, 1))
        self.assertEqual((self.led.fields["Setting"], self.chip.status), (2, 1))
        self.chip.run(5)
        self.assertEqual(self.ctok.fields["Setting"], 1, "no new token without a change")

    def test_reenables_dish_worker(self):
        self.chip.run(3)
        self.dishw.fields["On"] = 0
        self.chip.run(3)
        self.assertEqual(self.dishw.fields["On"], 1)

    def test_no_redundant_worker_writes(self):
        self.chip.run(10)
        self.assertEqual(self.dishw.writes_of("On"), [], "worker already on: no writes")


def dish(**f):
    base = {"On": 1, "Setting": 0, "Horizontal": 0, "Vertical": 0, "Idle": 1,
            "InterrogationProgress": 0, "SignalStrength": 0, "ContactTypeId": 0,
            "SignalID": 0, "BestContactFilter": 0, "MinimumWattsToContact": 0,
            "WattsReachingContact": 0, "Activate": 0}
    base.update(f)
    return Device(base)


class SatTraderTrackDish(unittest.TestCase):
    def make(self, sel):
        self.d, self.dl = dish(), dish(On=0)
        self.sel = Device({"Setting": sel})
        pins = {"d0": self.d, "d1": self.dl, "d3": self.sel,
                "d4": Device({"Open": 0}), "d5": Device({"Setting": 0, "Color": 0})}
        return Chip(script(f"{MOD}/SatTraderTrack/sat_trader_track_worker_dish.ic10"), pins=pins)

    def sweep(self, sel):
        self.make(sel).run(60)
        return sorted(set(self.d.writes_of("Horizontal")))

    def test_typed_mode_sweeps_when_no_signal(self):
        self.assertGreater(len(self.sweep(sel=3)), 3)

    @known_defect("D6")
    def test_any_mode_sweeps_when_no_signal(self):
        self.assertGreater(len(self.sweep(sel=0)), 3, "dish must keep sweeping in 'any' mode")


class IngotPrinterMaster(unittest.TestCase):
    def test_copies_selector_pick_into_slot0(self):
        sel = housing("selector_worker", setting=-654790771)
        fin = housing("finstd_worker")
        s0, s1 = memory("slot0"), memory("slot1")
        chip = Chip(script(f"{MOD}/ingot_printer/ingot_printer_master.ic10"),
                    network=[sel, fin, s0, s1])
        chip.run(3)
        self.assertEqual((s0.fields["Setting"], chip.status), (-654790771, -654790771))
        sel.fields["Setting"] = 640                   # selector status code, not a pick
        chip.run(3)
        self.assertEqual((s0.fields["Setting"], chip.status), (-654790771, 260))
        fin.fields["PrefabHash"] = 0                  # finstd housing missing
        chip.run(3)
        self.assertEqual(chip.status, 251)


class AutolatheVendStockHandshake(unittest.TestCase):
    """stock worker -> machine worker -> prep worker over shared Logic Memory."""

    FIRST_ITEM = 1225836666

    def setUp(self):
        names = ["cmd_token", "cmd_type", "slot0", "slot1", "slot2", "slot3", "slot4"]
        self.mem = {n: memory(n) for n in names}
        self.vend = Device({"On": 1}, slots=[{"Occupied": 0} for _ in range(102)])
        self.mach = Device({"On": 0, "Activate": 0, "Open": 1, "RecipeHash": 0,
                            "ExportCount": 0})
        self.stack = Device({"On": 0, "Mode": 1, "Setting": 1, "ExportCount": 0})
        net = list(self.mem.values())
        d = f"{MOD}/AutolatheVendStock/autolathe_vend_stock_"
        self.stock = Chip(script(d + "worker_stock.ic10"), pins={"d0": self.vend}, network=net)
        self.machine = Chip(script(d + "worker_machine.ic10"),
                            pins={"d0": self.mach, "d1": self.stack}, network=net)
        self.prep = Chip(script(d + "worker_machine_prep.ic10"), pins={"d0": self.mach},
                         network=net)
        self.chips = [self.stock, self.machine, self.prep]

    def m(self, name):
        return self.mem[name].fields["Setting"]

    @known_defect("D7")
    def test_missing_item_is_printed_and_command_consumed(self):
        # In-game chip update order within a tick is not something scripts can
        # rely on, so the handshake must work with either worker running first.
        for order in ("machine_first", "prep_first"):
            with self.subTest(order=order):
                self.setUp()
                if order == "prep_first":
                    self.chips = [self.stock, self.prep, self.machine]
                self._handshake()

    def _handshake(self):
        lockstep(self.chips, 110)                     # one full 100-slot scan
        self.assertEqual(self.m("slot0"), self.FIRST_ITEM)
        self.assertEqual(self.m("cmd_token"), 1)
        lockstep(self.chips, 10)
        self.assertEqual(self.m("cmd_type"), 0, "machine worker consumed the command")
        self.assertEqual(self.m("slot4"), 1, "run in progress")
        self.assertEqual((self.mach.fields["On"], self.mach.fields["Open"],
                          self.mach.fields["RecipeHash"]), (1, 0, self.FIRST_ITEM))
        self.assertEqual(self.m("slot3"), 1, "prep reports ready")
        self.assertEqual(self.mach.fields["Activate"], 1)
        # machine exports one item, stacker flushes it
        self.mach.fields.update(ExportCount=1, Activate=0)
        self.stack.fields["ExportCount"] = 1
        lockstep(self.chips, 5)
        self.assertEqual((self.m("slot4"), self.m("slot3"), self.machine.status), (0, 0, 140))

    def test_machine_worker_restart_releases_run_lock(self):
        lockstep(self.chips, 120)
        self.assertEqual(self.m("slot4"), 1)
        self.machine = Chip(self.machine.program, pins=self.machine.pins,
                            network=self.machine.network)   # chip reset mid-run
        self.chips[1] = self.machine
        lockstep(self.chips, 3)
        self.assertEqual(self.m("slot4"), 0, "restarted worker must not leave slot4 stuck")


if __name__ == "__main__":
    unittest.main()
