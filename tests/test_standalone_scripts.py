"""Behaviour scenarios for scripts/ (simulated, not in-game verified).

Each test drives a script through the situations its README promises:
threshold crossings, hysteresis bands, startup state and fault handling.
A passing test means "the IC10 logic does what the docs say under the
simulator's model" -- in-game behaviour still needs a human check.
"""

import unittest

from helpers import Chip, Device, K, analyzer, known_defect, script, switchable

VENT = "StructureActiveVent"
VALVE = "StructureDigitalValve"


def vent(name: str, **f) -> Device:
    base = {"On": 0, "Open": 0, "Lock": 0, "Mode": 0, "Setting": 0}
    base.update(f)
    return Device(base, prefab=VENT, name=name)


def gas_sensor(temp_c=20.0, pressure=100.0, **f) -> Device:
    return Device({"Temperature": temp_c + K, "Pressure": pressure, **f},
                  prefab="StructureGasSensor")


class PipeTempHotColdValves(unittest.TestCase):
    def setUp(self):
        self.pa = analyzer(20, 5000)
        self.hot, self.cold = switchable(), switchable()
        self.pump = switchable(Setting=0)
        self.chip = Chip(script("pipe_temp_hot_cold_valves"),
                         pins={"d0": self.pa, "d1": self.hot, "d2": self.cold, "d3": self.pump})

    def at(self, temp_c=None, kpa=None):
        if temp_c is not None:
            self.pa.fields["Temperature"] = temp_c + K
        if kpa is not None:
            self.pa.fields["Pressure"] = kpa
        self.chip.run(4)
        return self.cold.fields["On"], self.hot.fields["On"]

    def test_temperature_hysteresis(self):
        self.assertEqual(self.at(15), (1, 0))
        self.assertEqual(self.at(22), (1, 0))       # inside cold band: hold
        self.assertEqual(self.at(25), (0, 0))
        self.assertEqual(self.at(42), (0, 1))
        self.assertEqual(self.at(38), (0, 1))       # inside hot band: hold
        self.assertEqual(self.at(35), (0, 0))

    def test_pump_regulates_around_10_mpa(self):
        self.at(kpa=5000)
        self.assertEqual(self.pump.fields["On"], 1)
        self.at(kpa=10300)                          # above target + 250 kPa
        self.assertEqual(self.pump.fields["On"], 0, "pump must stop above 10.25 MPa")
        self.at(kpa=9900)                           # inside band: hold off
        self.assertEqual(self.pump.fields["On"], 0)
        self.at(kpa=9700)
        self.assertEqual(self.pump.fields["On"], 1)
        self.assertEqual(self.pump.fields["Setting"], 1)


class ActiveVentDualSets(unittest.TestCase):
    def setUp(self):
        self.sensor = gas_sensor(20)
        self.vin, self.vout = vent("IN", On=1, Open=1), vent("OUT", On=1, Open=1)
        self.chip = Chip(script("active_vent_dual_sets"), pins={"d0": self.sensor},
                         network=[self.vin, self.vout])

    def test_cold_start_turns_running_vents_off(self):
        self.chip.run(4)
        self.assertEqual((self.vin.fields["On"], self.vout.fields["On"]), (0, 0))
        self.assertEqual((self.vin.fields["Open"], self.vout.fields["Open"]), (0, 0))

    def test_warm_sets_intake_and_exhaust_groups(self):
        self.sensor.fields["Temperature"] = 35 + K
        self.chip.run(4)
        self.assertEqual([self.vin.fields[k] for k in ("Mode", "Setting", "Open", "On", "Lock")],
                         [0, 60000, 1, 1, 1])
        self.assertEqual([self.vout.fields[k] for k in ("Mode", "Setting", "Open", "On", "Lock")],
                         [1, 0, 1, 1, 1])


class PipePressureActiveVent(unittest.TestCase):
    def test_fill_cycle(self):
        pa = analyzer(20, 9950)
        v = vent("PIPE_VENT", On=1, Open=1)
        chip = Chip(script("pipe_pressure_active_vent"), pins={"d0": pa}, network=[v])
        chip.run(4)
        self.assertEqual(v.fields["On"], 0, "startup stops the vents")
        pa.fields["Pressure"] = 5000
        chip.run(4)
        self.assertEqual((v.fields["Mode"], v.fields["Setting"], v.fields["On"]), (1, 10000, 1))
        pa.fields["Pressure"] = 10000
        chip.run(4)
        self.assertEqual(v.fields["On"], 0)
        pa.fields["Pressure"] = 9950                # inside hysteresis: stay idle
        chip.run(6)
        self.assertEqual(v.fields["On"], 0)


class RoomPressureActiveVent(unittest.TestCase):
    def setUp(self):
        self.s = gas_sensor(20, 100)
        self.v = vent("ROOM_VENT")
        self.chip = Chip(script("room_pressure_active_vent"), pins={"d0": self.s},
                         network=[self.v])

    def p(self, kpa, ticks=8):
        self.s.fields["Pressure"] = kpa
        self.chip.run(ticks)
        return self.v.fields["On"], self.v.fields["Mode"]

    def test_bands(self):
        self.assertEqual(self.p(80), (1, 0))        # intake (outward into room)
        self.assertEqual(self.v.fields["Setting"], 120)
        self.assertEqual(self.p(120)[0], 0)
        self.assertEqual(self.p(130), (1, 1))       # exhaust
        self.assertEqual(self.v.fields["Setting"], 90)
        self.assertEqual(self.p(90)[0], 0)

    def test_very_high_pressure_exhausts(self):
        # A 2.5 MPa room must be exhausted, never treated as "low".
        self.assertEqual(self.p(2500), (1, 1))


class RoomCo2ActiveVent(unittest.TestCase):
    def setUp(self):
        self.s = gas_sensor(20, 101, RatioCarbonDioxide=0.3)
        self.v = switchable()
        self.chip = Chip(script("room_co2_below_20pct_active_vent"),
                         pins={"d0": self.s, "d1": self.v})

    def test_low_co2_or_low_pressure_opens(self):
        self.chip.run(4)
        self.assertEqual(self.v.fields["On"], 0)
        self.s.fields["RatioCarbonDioxide"] = 0.1
        self.chip.run(4)
        self.assertEqual((self.v.fields["On"], self.v.fields["Open"]), (1, 1))
        self.assertEqual((self.v.fields["Mode"], self.v.fields["Setting"]), (0, 100))
        self.s.fields.update(RatioCarbonDioxide=0.3, Pressure=80)
        self.chip.run(4)
        self.assertEqual(self.v.fields["On"], 1)

    def test_high_pressure_room_does_not_open(self):
        self.s.fields["Pressure"] = 2500
        self.chip.run(4)
        self.assertEqual(self.v.fields["On"], 0)


class ValveHysteresis(unittest.TestCase):
    def _cycle(self, chip, reader, valves, points):
        for temp, want in points:
            reader.fields["Temperature"] = temp + K
            chip.run(4)
            for v in valves:
                self.assertEqual(v.fields["On"], want, f"at {temp}C")

    def test_liquid_temp_valve(self):
        r = analyzer(25)
        v = Device({"On": 0, "PrefabHash": -517628750})
        chip = Chip(script("liquid_temp_valve"), pins={"d0": r}, network=[v])
        self._cycle(chip, r, [v], [(15, 1), (25, 1), (31, 0), (25, 0), (19, 1)])

    def test_pipe_temp_valve(self):
        r = analyzer(20)
        v = Device({"On": 1, "Lock": 0}, prefab=VALVE, name="cold")
        other = Device({"On": 1}, prefab=VALVE, name="hot")
        chip = Chip(script("pipe_temp_valve"), pins={"d0": r}, network=[v, other])
        self._cycle(chip, r, [v], [(20, 0), (5, 1), (20, 1), (31, 0)])
        self.assertEqual(other.fields["On"], 1, "only valves named exactly 'cold' change")

    def test_phase_change_temp_valve(self):
        r = Device({"Temperature": 20 + K})
        v = Device({"On": 1, "Lock": 1}, prefab=VALVE, name="cold")
        chip = Chip(script("phase_change_temp_valve"), pins={"d0": r}, network=[v])
        self._cycle(chip, r, [v], [(20, 0), (31, 1), (30, 0)])
        self.assertEqual(v.fields["Lock"], 0)


class OnOffControllers(unittest.TestCase):
    def test_pipe_heater_below_20c(self):
        pa, h = analyzer(25), switchable()
        chip = Chip(script("pipe_heater_below_20c"), pins={"d0": pa, "d1": h})
        chip.run(4); self.assertEqual(h.fields["On"], 0)
        pa.fields["Temperature"] = 15 + K
        chip.run(4); self.assertEqual(h.fields["On"], 1)
        pa.fields["Error"] = 1
        chip.run(4); self.assertEqual(h.fields["On"], 0, "analyzer error forces OFF")

    def test_room_heater_below_20c(self):
        s, h = gas_sensor(15), switchable()
        chip = Chip(script("room_heater_below_20c"), pins={"d0": s, "d1": h})
        chip.run(4); self.assertEqual(h.fields["On"], 1)
        s.fields["Temperature"] = 21 + K
        chip.run(4); self.assertEqual(h.fields["On"], 0)

    def test_gas_sensor_glass_door_30c(self):
        s, d = gas_sensor(31), switchable(Lock=1)
        chip = Chip(script("gas_sensor_glass_door_30c"), pins={"d0": s, "d1": d})
        chip.run(4)
        self.assertEqual((d.fields["Open"], d.fields["Lock"], d.fields["On"]), (1, 0, 1))
        s.fields["Temperature"] = 30 + K
        chip.run(4); self.assertEqual(d.fields["Open"], 1, "exactly 30C holds state")
        s.fields["Temperature"] = 29 + K
        chip.run(4); self.assertEqual(d.fields["Open"], 0)

    def test_room_cooler_steamless_vent(self):
        s = gas_sensor(31, RatioSteam=0)
        c, v = switchable(), switchable()
        chip = Chip(script("room_cooler_steamless_vent"), pins={"d0": s, "d1": c, "d2": v})
        chip.run(4)
        self.assertEqual((c.fields["On"], v.fields["On"], v.fields["Open"]), (1, 1, 1))
        s.fields.update(Temperature=25 + K, RatioSteam=0.1)
        chip.run(4)
        self.assertEqual((c.fields["On"], v.fields["On"]), (0, 0))

    def test_pipe_pressure_gas_mixer(self):
        pa, m = analyzer(20, 5000, On=0), switchable()
        chip = Chip(script("pipe_pressure_gas_mixer"), pins={"d0": pa, "d1": m})
        chip.run(4)
        self.assertEqual((pa.fields["On"], chip.status), (1, 4), "turns analyzer on first")
        chip.run(4); self.assertEqual(m.fields["On"], 1)
        pa.fields["Pressure"] = 10001
        chip.run(4); self.assertEqual(m.fields["On"], 0)
        pa.fields.update(Pressure=100, Error=1)
        chip.run(4); self.assertEqual((m.fields["On"], chip.status), (0, 3))

    def test_pipe_volatiles_gas_fuel_generator(self):
        pa, g = analyzer(20, RatioMethane=0), switchable()
        chip = Chip(script("pipe_volatiles_gas_fuel_generator"), pins={"d0": pa, "d1": g})
        chip.run(4); self.assertEqual(g.fields["On"], 0)
        pa.fields["RatioMethane"] = 0.01
        chip.run(4); self.assertEqual(g.fields["On"], 1)

    def test_no_volatiles_valve(self):
        pa, v = analyzer(20, RatioMethane=0.2), switchable()
        chip = Chip(script("no_volatiles_valve"), pins={"d0": pa, "d1": v})
        chip.run(4); self.assertEqual(v.fields["On"], 1)   # On while methane present
        pa.fields["RatioMethane"] = 0
        chip.run(4); self.assertEqual(v.fields["On"], 0)

    def test_no_volatiles_no_steam_valve(self):
        pa, v = analyzer(20, 50, RatioMethane=0, RatioSteam=0), switchable()
        chip = Chip(script("no_volatiles_no_steam_valve"), pins={"d0": pa, "d1": v})
        chip.run(4); self.assertEqual(v.fields["On"], 1)
        pa.fields["RatioSteam"] = 0.01
        chip.run(4); self.assertEqual(v.fields["On"], 0)
        pa.fields.update(RatioSteam=0, Pressure=0.5)
        chip.run(4); self.assertEqual(v.fields["On"], 0, "needs > 1 kPa")

    def test_volatiles_purge_valve(self):
        pa = analyzer(20, RatioMethane=0.5, RatioOxygen=0.1)
        v = switchable()
        chip = Chip(script("volatiles_purge_valve"), pins={"d0": pa, "d1": v})
        chip.run(4); self.assertEqual(v.fields["On"], 1)   # 0.1 < 0.33 * 0.5
        pa.fields["RatioOxygen"] = 0.2
        chip.run(4); self.assertEqual(v.fields["On"], 0)

    def test_volatiles_purge_active_vent(self):
        pa = analyzer(20, RatioMethane=0.5, RatioOxygen=0.1)
        v = switchable(Mode=1)
        chip = Chip(script("volatiles_purge_active_vent"), pins={"d0": pa, "d1": v})
        chip.run(4)
        self.assertEqual((v.fields["Mode"], v.fields["On"], v.fields["Open"]), (0, 1, 1))
        pa.fields["RatioOxygen"] = 0.4
        chip.run(4); self.assertEqual(v.fields["On"], 0)

    def test_large_battery_mean_gas_generator(self):
        gen = switchable()
        bats = [Device({"Ratio": r}, prefab="StructureBatteryLarge") for r in (0.2, 0.3)]
        chip = Chip(script("large_battery_mean_gas_generator"), pins={"d0": gen}, network=bats)
        chip.run(4); self.assertEqual(gen.fields["On"], 1)  # mean 0.25 < 0.30
        bats[0].fields["Ratio"] = 0.5
        chip.run(4); self.assertEqual(gen.fields["On"], 0)
        chip.network.clear()
        chip.run(4); self.assertEqual(gen.fields["On"], 0, "no batteries: fail-safe OFF")

    def test_air_conditioner_25c(self):
        ac = switchable(Setting=0, Mode=0)
        chip = Chip(script("air_conditioner_25c"), housing=ac)
        chip.run(4)
        self.assertAlmostEqual(ac.fields["Setting"], 25 + K)
        self.assertEqual((ac.fields["Mode"], ac.fields["On"]), (1, 1))
        chip.run(10)
        self.assertEqual(len(ac.writes), 3, "no repeated writes once settled")


class VentFillControllers(unittest.TestCase):
    def test_liquid_pipe_fill_percent_active_vent(self):
        pa = Device({"Volume": 100, "VolumeOfLiquid": 30})
        v = switchable(Mode=1)
        chip = Chip(script("liquid_pipe_fill_percent_active_vent"), pins={"d0": pa, "d1": v})
        chip.run(4)
        self.assertEqual((v.fields["Mode"], v.fields["On"], v.fields["Open"]), (0, 1, 1))
        pa.fields["VolumeOfLiquid"] = 60
        chip.run(4); self.assertEqual(v.fields["On"], 0)

    def test_pipe_half_full_active_vent(self):
        pa, v = analyzer(20, 40), switchable()
        chip = Chip(script("pipe_half_full_active_vent"), pins={"d0": pa, "d1": v})
        for kpa, want in [(40, 1), (52, 1), (56, 0), (52, 0), (49, 1)]:
            pa.fields["Pressure"] = kpa
            chip.run(4)
            self.assertEqual((v.fields["On"], v.fields["Open"]), (want, want), f"{kpa} kPa")


class SafetyAndUtility(unittest.TestCase):
    def test_landingpad_volatiles_pressure_valve(self):
        pa = analyzer(20, 1000)
        pad = Device({"RatioMethane": 1.0, "On": 0})
        valve = switchable(Lock=1)
        chip = Chip(script("landingpad_volatiles_pressure_valve"),
                    pins={"d0": pa, "d1": pad, "d2": valve})
        chip.run(4)
        self.assertEqual((pad.fields["On"], valve.fields["On"], valve.fields["Lock"],
                          chip.status), (1, 1, 0, 10))
        pa.fields["Pressure"] = 25000
        chip.run(4)
        self.assertEqual((pad.fields["On"], valve.fields["On"], chip.status), (0, 0, 30))
        pa.fields["Pressure"] = 1000
        pad.fields["RatioMethane"] = 0.5
        chip.run(4)
        self.assertEqual((pad.fields["On"], chip.status), (0, 20))
        chip.pins["d3"] = Device({"Setting": 1})
        chip.run(4)
        self.assertEqual((pad.fields["On"], chip.status), (1, 40), "manual override")

    def test_hardsuit_helmet_manual_close_is_respected(self):
        suit = Device({"TemperatureExternal": 20 + K, "PressureExternal": 100})
        helmet = Device({"Open": 0, "Lock": 0})
        chip = Chip(script("hardsuit_helmet_temp_pressure_open"), pins={"d0": helmet},
                    housing=suit)
        chip.run(4); self.assertEqual(helmet.fields["Open"], 1)
        helmet.fields["Open"] = 0                    # player closes it
        chip.run(6); self.assertEqual(helmet.fields["Open"], 0)
        suit.fields["PressureExternal"] = 50         # unsafe
        chip.run(4); self.assertEqual(helmet.fields["Open"], 0)
        suit.fields["PressureExternal"] = 100        # safe again: auto-open
        chip.run(4); self.assertEqual(helmet.fields["Open"], 1)
        suit.fields["TemperatureExternal"] = 50 + K
        chip.run(4); self.assertEqual(helmet.fields["Open"], 0)

    def test_led_display_clock_digits(self):
        hrs = Device({"On": 0, "Mode": 0, "Setting": 0})
        mins = Device({"On": 0, "Mode": 0, "Setting": 0})
        day = Device({"Horizontal": 97.5})          # floors to 97 deg -> 06:28 (4 min/deg)
        chip = Chip(script("led_display_hms_clock"), pins={"d0": hrs, "d1": mins, "d3": day})
        chip.run(4)
        self.assertEqual(hrs.fields["Mode"], 10)
        self.assertEqual(hrs.fields["Setting"], ord("0") * 256 + ord("6"))
        self.assertEqual(mins.fields["Setting"], ord("2") * 256 + ord("8"))

    def test_purge_valve_led_matrix(self):
        lever = Device({"Open": 1})
        reader = Device({"Pressure": 5, "Error": 0})
        valve, vnt, outlet = switchable(), switchable(), switchable()
        led = Device({"On": 0, "Color": 0})
        chip = Chip(script("purge_valve"), pins={"d0": lever, "d1": reader, "d2": valve,
                                                 "d3": vnt, "d4": outlet, "d5": led})
        chip.run(4)
        self.assertEqual([valve.fields["On"], vnt.fields["On"], outlet.fields["On"],
                          led.fields["Color"]], [1, 1, 1, 4])           # red
        lever.fields["Open"] = 0
        chip.run(4)
        self.assertEqual((valve.fields["On"], led.fields["Color"]), (0, 5))  # yellow
        lever.fields["Open"], reader.fields["Pressure"] = 1, 0
        chip.run(4)
        self.assertEqual((valve.fields["On"], led.fields["Color"]), (0, 2))  # green

    def test_dual_analyzer_furnace_pulse(self):
        liq, gas = Device({"Temperature": 90 + K}), Device({"Temperature": 20 + K})
        valve, furnace = switchable(), Device({"Activate": 0})
        chip = Chip(script("dual_analyzer_furnace_pulse"),
                    pins={"d0": liq, "d1": gas, "d2": valve, "d3": furnace})
        chip.run(5)
        self.assertEqual(furnace.writes_of("Activate")[:2], [1, 0])
        self.assertEqual(valve.writes_of("On")[:2], [1, 0])
        self.assertEqual(furnace.fields["Activate"], 0)

    def test_pipe_furnace_valve_below_20c(self):
        pa = analyzer(15)
        valve = switchable()
        furnace = Device({"Temperature": 50 + K, "On": 0, "Activate": 0, "Lock": 0,
                          "SettingInput": 0, "SettingOutput": 0})
        chip = Chip(script("pipe_furnace_valve_below_20c"),
                    pins={"d0": pa, "d1": valve, "d2": furnace})
        chip.run(4)
        self.assertEqual([valve.fields["On"], furnace.fields["On"], furnace.fields["Activate"],
                          furnace.fields["SettingInput"], furnace.fields["SettingOutput"]],
                         [1, 1, 1, 5, 5])
        furnace.fields["Temperature"] = 120 + K
        chip.run(4); self.assertEqual(furnace.fields["SettingInput"], 0)
        pa.fields["Temperature"] = 25 + K
        chip.run(4)
        self.assertEqual([valve.fields["On"], furnace.fields["On"], furnace.fields["Activate"]],
                         [0, 0, 0])


if __name__ == "__main__":
    unittest.main()
