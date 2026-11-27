"""Verification of phase 5b, part 2: time-of-use tariff and load shifting (#090), Gaussian plume (#069)."""
import gzip
import hashlib
import json
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from thermal import plume as P
from thermal import tariff as T

ROOT = Path(__file__).resolve().parents[1]


class Data(unittest.TestCase):
    def test_manifests(self):
        a = json.loads((ROOT / "data/aneel/manifest.json").read_text())
        self.assertEqual(hashlib.sha256((ROOT / "data/aneel" / a["subset"]["file"]).read_bytes()).hexdigest(), a["subset"]["sha256"])
        self.assertEqual(hashlib.sha256((ROOT / "data/aneel" / a["cross_check"]["subset"]).read_bytes()).hexdigest(), a["cross_check"]["subset_sha256"])
        s = json.loads((ROOT / "data/steel/manifest.json").read_text())
        raw = gzip.decompress((ROOT / "data/steel/Steel_industry_data.csv.gz").read_bytes())
        self.assertEqual(hashlib.sha256(raw).hexdigest(), s["files"]["Steel_industry_data.csv"])
        m = json.loads((ROOT / "data/inmet_hourly/manifest.json").read_text())
        for name, v in m["files"].items():
            with self.subTest(file=name):
                raw = gzip.decompress((ROOT / "data/inmet_hourly" / name).read_bytes())
                self.assertEqual(hashlib.sha256(raw).hexdigest(), v["sha256_raw"])

    def test_steel_series_is_a_regular_year(self):
        L = T.load_steel()
        self.assertEqual(len(L), 35040)
        self.assertEqual(L.index[0], pd.Timestamp("2018-01-01 00:00"))
        self.assertEqual(L.index[-1], pd.Timestamp("2018-12-31 23:45"))
        self.assertTrue((L.index.to_series().diff().dropna() == pd.Timedelta(minutes=15)).all())

    def test_tariff_scale_against_second_mirror(self):
        tf, fb = T.tariffs(), T.fiob()
        self.assertLess(fb[("Verde", "Não se aplica")], tf["Verde"].parts["D"])
        self.assertLess(fb[("Azul", "Ponta")], tf["Azul"].parts["D_p"])
        self.assertLess(fb[("Azul", "Fora ponta")], tf["Azul"].parts["D_fp"])
        # Fio B is the bulk of the demand TUSD: the unscaled mirror (×100) would make it < 1 %
        self.assertGreater(fb[("Azul", "Ponta")] / tf["Azul"].parts["D_p"], 0.5)
        self.assertGreater(tf["Verde"].E_p, tf["Verde"].E_fp)
        self.assertAlmostEqual(tf["Verde"].E_fp, tf["Azul"].E_fp)


class Billing(unittest.TestCase):
    def setUp(self):
        idx = pd.date_range("2026-03-02", periods=96 * 7, freq="15min")   # Monday to Sunday
        self.L = pd.Series(100.0, index=idx)
        self.pk = T.peak_mask(idx)
        self.t = T.tariffs()["Verde"]

    def test_peak_window(self):
        self.assertEqual(int(self.pk.sum()), 5 * 12)                     # 3 h × 4 intervals × 5 working days

    def test_bill_by_hand(self):
        b = T.bill(self.L, self.pk, self.t, Dc_p=100.0)
        Ep = 100 * 15 / 1000                                             # MWh in the peak
        Efp = 100 * (168 - 15) / 1000
        self.assertAlmostEqual(b.energy.sum(), self.t.E_p * Ep + self.t.E_fp * Efp, places=6)
        self.assertAlmostEqual(b.demand.sum(), self.t.D_p * 100, places=6)
        self.assertEqual(b.over.sum(), 0.0)
        b2 = T.bill(self.L, self.pk, self.t, Dc_p=90.0)                  # 11 % above the contract: penalty
        self.assertAlmostEqual(b2.over.sum(), 2 * self.t.D_p * 10, places=6)
        b3 = T.bill(self.L, self.pk, self.t, Dc_p=96.0)                  # within the 5 % tolerance
        self.assertEqual(b3.over.sum(), 0.0)

    def test_lp_conserves_energy_and_saves_the_tariff_gap(self):
        S, moved = T.shift_year(self.L, self.pk, self.t, 0.3)
        day = self.L.index.normalize()
        np.testing.assert_allclose(S.groupby(day).sum(), self.L.groupby(day).sum(), rtol=1e-9)
        self.assertAlmostEqual(moved, 0.3 * 100 * 15 / 1000, places=6)
        self.assertTrue((S[self.pk] >= 0.7 * 100 - 1e-6).all())
        before = T.bill(self.L, self.pk, self.t, 100.0)
        after = T.bill(S, self.pk, self.t, 100.0)
        self.assertAlmostEqual(before.energy.sum() - after.energy.sum(), (self.t.E_p - self.t.E_fp) * moved, places=4)


class Plume(unittest.TestCase):
    def test_briggs_rural_values(self):
        sy, sz = P._briggs(np.array([3]), np.array([1000.0]))
        self.assertAlmostEqual(float(sy[0]), 0.08 * 1000 / np.sqrt(1.1), places=6)
        self.assertAlmostEqual(float(sz[0]), 0.06 * 1000 / np.sqrt(2.5), places=6)

    def test_crosswind_integral(self):
        st = P.Stack(h=40.0, Q=1.0)
        met = pd.DataFrame({"ws": [3.0], "wd": [0.0], "T": [20.0]}, index=pd.DatetimeIndex(["2024-01-01 12:00"]))
        cls = np.array([3.0])
        R = 2000.0
        dirs = np.arange(150.0, 210.0, 0.05)                              # plume travels to 180°
        C, H = P.ground_conc(st, met, cls, np.array([R]), dirs)
        integral = float(np.sum(C[0, :, 0]) * R * np.radians(0.05))
        u = P.wind_at(np.array([3.0]), cls, st.h)[0]
        _, sz = P.sigmas(cls, np.array([R]))
        expected = 1e6 * np.sqrt(2 / np.pi) / (u * sz[0]) * np.exp(-H[0] ** 2 / (2 * sz[0] ** 2))
        self.assertAlmostEqual(integral / expected, 1.0, delta=0.01)

    def test_stability_table(self):
        self.assertEqual(float(P.stability([1.0], [800.0], [True])[0]), 0.0)          # A
        self.assertEqual(float(P.stability([7.0], [100.0], [True])[0]), 3.0)          # D
        self.assertEqual(float(P.stability([1.0], [0.0], [False], "overcast")[0]), 4.0)
        self.assertEqual(float(P.stability([1.0], [0.0], [False], "clear")[0]), 5.0)

    def test_solar_elevation_at_solstice(self):
        idx = pd.date_range("2023-12-21 00:30", periods=24 * 60, freq="min")   # stamps end each averaging hour
        e = P.solar_elevation(idx, -23.04, -45.52)
        self.assertGreater(e.max(), 88.0)
        self.assertLess(e.min(), -40.0)

    def test_taubate_files(self):
        met, head = P.load_taubate()
        self.assertEqual(head["CODIGO (WMO)"], "A728")
        self.assertEqual(len(met), 24 * (365 * 3 + 366))
        self.assertTrue(met.ws.dropna().between(0, 40).all())


class Published(unittest.TestCase):
    def test_json(self):
        d = json.loads((ROOT / "site/data/tariff_plume.json").read_text())
        t = d["tariff"]
        self.assertLess(t["base"]["Verde"]["annual"], t["base"]["Azul"]["annual"])
        self.assertLess(max(t["breakeven"]["plant_hours"]), t["breakeven"]["hours"])
        annual = [s["annual"] for s in t["sweep"]["Verde"]]
        self.assertTrue(all(b < a for a, b in zip(annual, annual[1:])))
        p = d["plume"]
        self.assertAlmostEqual(p["q_allow"]["governing"], min(p["q_allow"]["by_24h"], p["q_allow"]["by_annual"]))


if __name__ == "__main__":
    unittest.main()
