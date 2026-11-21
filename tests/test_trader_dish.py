"""Scenarios for scripts/trader_dish_auto_land (simulated dish, not in-game verified).

The fake dish models the 2026 signal behaviour described by players:
SignalStrength = angle in degrees between where the dish points and the contact
(smaller is closer), -1 when nothing is visible. Vertical is measured from the
zenith (0) to the horizon (90). Activate pressed while idle starts interrogation,
pressed after InterrogationProgress reached 1 calls the trader down.
"""

import math
import unittest

from helpers import Chip, Device, script


class FakeDish(Device):
    def __init__(self, h, v, ctype=3, sid=777, visible_deg=40):
        super().__init__({"Horizontal": 0, "Vertical": 0, "Setting": 0, "Activate": 0,
                          "BestContactFilter": -1, "Idle": 1, "TargetPadIndex": 0,
                          "SignalStrength": -1, "SignalID": -1, "ContactTypeId": -1,
                          "InterrogationProgress": 0},
                         prefab="StructureLargeSatelliteDish")
        self.target = (h, v)
        self.ctype, self.sid, self.visible = ctype, sid, visible_deg
        self.progress, self.interrogating, self.called = 0.0, False, False

    def distance(self):
        h1, v1 = map(math.radians, (self.fields["Horizontal"], self.fields["Vertical"]))
        h2, v2 = map(math.radians, self.target)
        c = math.cos(v1) * math.cos(v2) + math.sin(v1) * math.sin(v2) * math.cos(h1 - h2)
        return math.degrees(math.acos(max(-1.0, min(1.0, c))))

    def read(self, f):
        d = self.distance()
        seen = d <= self.visible
        if f == "SignalStrength":
            return d if seen else -1
        if f == "SignalID":
            return self.sid if seen else -1
        if f == "ContactTypeId":
            return self.ctype if seen else -1
        if f == "InterrogationProgress":
            if self.interrogating and d <= 6 and self.fields["Setting"] >= 10000:
                self.progress = min(1.0, self.progress + 0.1)
                if self.progress >= 1:
                    self.interrogating = False
                    self.fields["Activate"] = 0
            return self.progress
        return super().read(f)

    def write(self, f, value, tick):
        super().write(f, value, tick)
        if f == "Activate" and value == 1:
            if self.progress >= 1:
                self.called = True
            elif not self.interrogating:
                self.interrogating = True


def run(dish, dial=None, lever=None, ticks=3000):
    pins = {"d0": dish, "d3": Device({"Setting": 0})}
    if dial is not None:
        pins["d1"] = Device({"Setting": dial})
    if lever is not None:
        pins["d2"] = Device({"Open": lever})
    chip = Chip(script("trader_dish_auto_land"), pins=pins)
    chip.run(ticks)
    return chip


class TraderDishAutoLand(unittest.TestCase):
    def test_finds_locks_interrogates_and_calls_down(self):
        for target in [(200, 50), (10, 80), (300, 5), (95, 33)]:
            with self.subTest(target=target):
                dish = FakeDish(*target)
                run(dish, dial=0, lever=1)
                self.assertEqual(dish.progress, 1, "interrogation completed")
                self.assertTrue(dish.called, "trader called down")
                self.assertIn(777, dish.writes_of("BestContactFilter"), "locked to the contact")

    def test_lever_off_interrogates_but_does_not_call(self):
        dish = FakeDish(200, 50)
        run(dish, dial=0, lever=0)
        self.assertEqual(dish.progress, 1)
        self.assertFalse(dish.called)

    def test_dial_filters_trader_type(self):
        dish = FakeDish(200, 50, ctype=3)
        run(dish, dial=5, lever=1, ticks=1500)
        self.assertNotIn(777, dish.writes_of("BestContactFilter"))
        self.assertFalse(dish.interrogating or dish.called)

    def test_same_trader_is_not_interrogated_twice(self):
        dish = FakeDish(200, 50)
        chip = run(dish, dial=0, lever=1, ticks=6000)
        self.assertEqual(dish.writes_of("Activate").count(1), 2, "one interrogate + one call")
        self.assertEqual(chip.status // 100, 1, "back to scanning")

    def test_missing_dish_reports_900_without_halting(self):
        chip = Chip(script("trader_dish_auto_land"), pins={})
        chip.run(10)
        self.assertEqual(chip.status, 900)


if __name__ == "__main__":
    unittest.main()
