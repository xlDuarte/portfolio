"""Verification of phase 5b: furnace heat balance and machining energy (#029), bath kinetics and
replenishment (#070)."""
import json
import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np

from thermal import bath as B
from thermal import furnace as F
from thermal import machining as M

ROOT = Path(__file__).resolve().parents[1]


class Materials(unittest.TestCase):
    def test_en1993_specific_heat(self):
        self.assertAlmostEqual(float(F.steel_cp(20)), 425 + 0.773 * 20 - 1.69e-3 * 400 + 2.22e-6 * 8000, places=6)
        self.assertAlmostEqual(float(F.steel_cp(735)), 5000.0, places=6)      # peak of the norm's curve
        self.assertAlmostEqual(float(F.steel_cp(734.99999)), 5000.0, delta=0.1)  # continuous at 735 °C
        self.assertEqual(float(F.steel_cp(1000)), 650.0)
        self.assertAlmostEqual(float(F.steel_k(20)), 54 - 0.666, places=6)
        self.assertEqual(float(F.steel_k(900)), 27.3)

    def test_air_properties_near_room_temperature(self):
        rho, mu, k, cp, Pr = F.air(300.0)
        self.assertAlmostEqual(float(rho), 1.177, delta=0.005)
        self.assertAlmostEqual(float(mu), 1.846e-5, delta=0.02e-5)
        self.assertAlmostEqual(float(Pr), 0.71, delta=0.02)


class Walls(unittest.TestCase):
    def test_view_factor_aligned_squares(self):
        self.assertAlmostEqual(F.view_factor_parallel(1, 1), 0.1998, places=4)   # Incropera fig. 13.4
        self.assertLess(F.view_factor_parallel(0.1, 0.1), 0.01)
        self.assertGreater(F.view_factor_parallel(100, 100), 0.98)

    def test_layer_integral_is_exact(self):
        lay = F.LINING[0]
        T1, q = 860.0, 400.0
        T2 = lay.cold_face(T1, q)
        integral = lay.k0 * (T1 - T2) + lay.k1 / 2 * (T1**2 - T2**2)
        self.assertAlmostEqual(integral, q * lay.L, places=6)

    def test_constant_k_matches_resistance_network(self):
        lin = tuple(replace(l, k1=0.0) for l in F.LINING)
        face = F.Furnace().faces()[0]
        r = F.wall_steady(860.0, face, lin)
        R = sum(l.L / l.k0 for l in lin)
        self.assertAlmostEqual(r["q"], (860.0 - r["Ts"]) / R, delta=1e-6 * r["q"])
        self.assertAlmostEqual(r["q"], F.q_out(r["Ts"], face, 25.0, 0.9), delta=1e-4 * r["q"])

    def test_interfaces_within_service_limits(self):
        for v in F.Furnace().wall_losses().values():
            for T, lay in zip(v["interfaces"], F.LINING):
                self.assertLess(T, lay.t_max)

    def test_transient_lining_reaches_steady_flux(self):
        f = F.Furnace()
        q_ss = f.wall_losses()["Paredes laterais"]["q"]
        r = F.lining_transient(f, 400.0, mode="hold", dt=600.0)
        self.assertAlmostEqual(r["q_out"][-1], q_ss, delta=0.01 * q_ss)
        self.assertAlmostEqual(r["q_in"][-1], q_ss, delta=0.01 * q_ss)


class Cycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f, cls.c = F.Furnace(), F.Charge()
        cls.res = F.heat_charge(cls.f, cls.c)

    def test_energy_balance_closes(self):
        E = self.res["E"]
        parts = E["charge"] + E["wall"] + E["door_rad"] + E["door_conv"]
        self.assertLess(abs(E["total"] - parts) / E["total"], 0.005)

    def test_charge_energy_equals_enthalpy(self):
        h = self.c.mass * F.steel_enthalpy(self.res["T_mean_final"])
        self.assertLess(abs(self.res["E"]["charge"] - h) / h, 0.005)

    def test_power_never_exceeds_installed(self):
        self.assertLessEqual(self.res["P"].max(), self.f.P_max + 1e-6)
        self.assertGreater(self.res["power_limited_s"], 0)

    def test_door_convection_is_bounded_by_lining(self):
        d = self.f.door()
        self.assertLess(d["conv"], d["conv_unlimited"])
        self.assertLess(self.f.T_amb, d["T_gas"])
        self.assertLess(d["T_gas"], self.f.T_set)


class Machining(unittest.TestCase):
    def test_specific_energy_is_kienzle(self):
        p = M.turning_pass(80, 70, 1000, 200, 0.25, kappa_deg=90.0, kc11=1500, mc=0.22)
        self.assertAlmostEqual(p["u_J_mm3"], 1e-3 * 1500 * 0.25 ** (-0.22), places=9)
        self.assertAlmostEqual(float(M.specific_energy(0.25, 1500, 0.22)), p["u_J_mm3"], places=9)
        self.assertAlmostEqual(p["Fc"], 1500 * 5.0 * 0.25 ** 0.78, places=6)

    def test_idle_share_falls_with_removal_rate(self):
        s = M.removal_rate_sweep(1500, 0.22)
        self.assertTrue(np.all(np.diff(s["share_idle"]) < 0))
        self.assertTrue(np.all(np.diff(s["e"]) < 0))


class Bath(unittest.TestCase):
    def test_noise_free_prediction_reproduces_simulation(self):
        b = B.Bath()
        sim = B.simulate(b, hours=24 * 7)
        t = np.arange(1, len(sim["C"]))
        # the simulation clips at the addition; prediction adds the same mass back
        pred = B.predict((b.k_d, b.q, b.r), t, sim["prod"], sim["a"], b.C_set, b.V, sim["adds"])
        self.assertLess(np.max(np.abs(pred - sim["C"][t])), 1e-9)

    def test_two_bands_make_drag_out_identifiable(self):
        b = B.Bath()
        se = {}
        for key, bands in (("one", None), ("two", [(30, 26), (22, 18)])):
            sim = B.simulate(b, bands=bands)
            t, y = B.titrations(sim)
            se[key] = B.fit(t, y, sim["prod"], sim["a"], b.C_set, b.V, sim["adds"])["se"]
        self.assertLess(se["two"][1], se["one"][1] / 4)
        self.assertLess(se["two"][2], se["one"][2] / 4)

    def test_lead_time_variance_formula(self):
        d = np.random.default_rng(0).gamma(4, 5, 5000)
        c = B.classical(d)
        EL, VL = c["EL"], c["VL"]
        self.assertAlmostEqual(c["sdL"] ** 2, EL * d.var(ddof=1) + d.mean() ** 2 * VL, places=6)
        self.assertLess(B.classical(d, lead_variance=False)["s"], c["s"])


class Published(unittest.TestCase):
    def test_json_consistency(self):
        d = json.loads((ROOT / "site/data/thermal.json").read_text())
        f = d["furnace"]
        self.assertLess(abs(f["closure_pct"]), 0.5)
        self.assertLessEqual(f["mc"]["p5"], f["kwh_per_t"])
        self.assertLessEqual(f["kwh_per_t"], f["mc"]["p95"])
        for w in f["weekend"]:
            self.assertLessEqual(w["ready_at_h"], w["stop_h"] + 1e-9)
            self.assertGreater(w["saving_kwh"], 0)
        p = d["bath"]["policies"]
        self.assertGreaterEqual(p["simulated_optimum"]["cycle_service"], 0.99)
        self.assertLess(p["fixed_lead"]["cycle_service"], 0.99)
        lo, hi = d["bath"]["fits"]["single"]["demand_ci"]
        self.assertLessEqual(lo, d["bath"]["fits"]["single"]["demand_true"])
        self.assertLessEqual(d["bath"]["fits"]["single"]["demand_true"], hi)


if __name__ == "__main__":
    unittest.main()
