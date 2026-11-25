"""Verification of phase 5a: ONS/INMET data, change-point baselines (#008), peak forecast (#064)
and the plant-climate model (#063)."""
import gzip
import hashlib
import json
import unittest
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from energy import changepoint as CP
from energy import climate as K
from energy import data as E
from energy import forecast as F

ROOT = Path(__file__).resolve().parents[1]


class CommittedData(unittest.TestCase):
    def test_files_match_manifest(self):
        for kind in ("ons", "inmet"):
            m = json.loads((ROOT / "data" / kind / "manifest.json").read_text())
            for name, h in m["files"].items():
                raw = gzip.open(ROOT / "data" / kind / (name + ".gz")).read()
                with self.subTest(file=name):
                    self.assertEqual(hashlib.sha256(raw).hexdigest(), h)

    def test_ons_series_is_complete_and_plausible(self):
        h = E.ons_hourly("SE")
        self.assertEqual(len(h), len(pd.date_range("2019-01-01", "2025-12-31 23:00", freq="h")))
        self.assertTrue(h.index.is_monotonic_increasing)
        self.assertTrue(20_000 < h.min() and h.max() < 70_000)  # MWmed, SE/CO subsystem

    def test_inmet_quality_flags(self):
        w = E.inmet_daily("A728")
        ok = w.dropna(subset=["tmin", "tmean", "tmax"])
        self.assertTrue((ok.tmin <= ok.tmean).all() and (ok.tmean <= ok.tmax).all())
        self.assertGreater(w.attrs["flagged"], 0)


class Calendar(unittest.TestCase):
    def test_easter(self):
        for y, d in ((2019, date(2019, 4, 21)), (2024, date(2024, 3, 31)), (2025, date(2025, 4, 20))):
            self.assertEqual(E.easter(y), d)

    def test_holidays(self):
        h = E.holidays([2023, 2024])
        days = set(pd.to_datetime(h.date).dt.date)
        self.assertIn(date(2024, 11, 20), days)       # Consciência Negra, national from 2024
        self.assertNotIn(date(2023, 11, 20), days)
        self.assertIn(date(2024, 2, 13), days)        # Carnaval Tuesday (ponto facultativo)
        self.assertIn(date(2024, 5, 30), days)        # Corpus Christi
        self.assertIn(date(2024, 3, 29), days)        # Good Friday


class ChangePoint(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(0)
        self.T = rng.uniform(10, 32, 800)
        self.y = 30_000 + 300 * (self.T - 21) + 900 * np.maximum(self.T - 21, 0) + rng.normal(0, 200, 800)

    def test_recovers_parameters(self):
        f = CP.fit(self.T, self.y, "4P")
        self.assertAlmostEqual(f.cps[0], 21, delta=0.3)
        self.assertAlmostEqual(f.beta[1], 300, delta=30)
        self.assertAlmostEqual(f.beta[2], 1200, delta=40)
        self.assertLess(abs(f.nmbe), 1e-9)

    def test_bic_prefers_true_shape(self):
        bic = {k: CP.fit(self.T, self.y, k).bic for k in ("2P", "3PC", "4P")}
        self.assertEqual(min(bic, key=bic.get), "4P")

    def test_effective_sample_size(self):
        f = CP.fit(self.T, self.y, "4P")
        self.assertAlmostEqual(f.n_eff, f.n * (1 - f.rho) / (1 + f.rho), places=6)


class Scores(unittest.TestCase):
    def test_crps_of_standard_normal(self):
        S = np.random.default_rng(1).normal(size=(1, 200_000))
        exact = 2 / np.sqrt(2 * np.pi) - 1 / np.sqrt(np.pi)
        self.assertAlmostEqual(F.crps_ensemble(S, np.zeros(1))[0], exact, places=2)


class Climate(unittest.TestCase):
    def test_mann_kendall(self):
        r = K.mann_kendall(np.arange(10.0))
        self.assertEqual(r["S"], 45)
        self.assertAlmostEqual(r["sen"], 1.0)
        self.assertLess(r["p"], 0.001)
        # hand computation with ties: S = 5, var = (6·5·17 − 2·2·1·9)/18, z = (S − 1)/√var
        r = K.mann_kendall(np.array([1.0, 3, 2, 4, 2, 3]))
        self.assertEqual(r["S"], 5)
        self.assertAlmostEqual(r["z"], 4 / np.sqrt(474 / 18), places=9)

    def test_fao56_example_8(self):
        # FAO-56 example 8: 20° S on 3 September → Ra = 32.2 MJ m⁻² day⁻¹
        self.assertAlmostEqual(float(K.extraterrestrial(np.array([246]), -20.0)[0]), 32.2, delta=0.1)
        self.assertAlmostEqual(float(K.daylength(np.array([80]), 0.0)[0]), 12.0, places=6)

    def test_rc_steady_state(self):
        b = K.Warehouse(q_int=0.0)
        idx = pd.date_range("2023-01-02", periods=24 * 40, freq="h")
        T, G = np.full(len(idx), 30.0), np.full(len(idx), 400.0)
        vent = 1.2 * 1005 * b.ach * b.area * b.height / 3600
        Kr, Ko = b.U_roof * b.area, b.U_wall * b.wall_area + vent
        Tsa = 30 + b.alpha * 400 / b.h_out
        Ti, _ = K.simulate(b, T, G, idx, cooling=False)
        self.assertAlmostEqual(Ti[-1], (Kr * Tsa + Ko * 30) / (Kr + Ko), places=3)
        _, Qc = K.simulate(b, T, G, idx, cooling=True)
        self.assertAlmostEqual(Qc[-1], Kr * (Tsa - b.t_set) + Ko * (30 - b.t_set), delta=1.0)

    def test_insulation_and_white_roof_reduce_cooling(self):
        w = E.inmet_daily(K.STATION)
        res, years, _, _ = K.run_years(w)
        mean = {n: np.mean([r[y]["cooling_mwh"] for y in years]) for n, r in res.items()}
        names = list(K.SCENARIOS)
        self.assertGreater(mean[names[0]], mean[names[1]])
        self.assertGreater(mean[names[1]], mean[names[2]])
        self.assertGreater(mean[names[2]], mean[names[3]])


class Published(unittest.TestCase):
    def test_json_consistency(self):
        d = json.loads((ROOT / "site/data/energy.json").read_text())
        c = d["changepoint"]
        lo, hi = c["best_ci"]["cp"]
        self.assertLessEqual(lo, c["models"][c["best"]]["cps"][0])
        self.assertLessEqual(c["models"][c["best"]]["cps"][0], hi)
        m = d["forecast"]["metrics"]
        self.assertLess(m["Temperatura observada (oráculo)"]["mape"], m["Mesmo dia da semana anterior"]["mape"])
        self.assertEqual(len(d["forecast"]["dates"]), len(d["forecast"]["actual"]))


if __name__ == "__main__":
    unittest.main()
