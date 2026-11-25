"""Verification of phase 4b: C-MAPSS RUL model (#097) and hydraulic-rig physics (#036, #037)."""
import gzip
import hashlib
import json
import unittest
from pathlib import Path

import numpy as np

from degradation import cmapss as C
from degradation import hydraulics as H

ROOT = Path(__file__).resolve().parents[1]


class CmapssData(unittest.TestCase):
    def test_committed_files_match_manifest(self):
        m = json.loads((ROOT / "data/cmapss/manifest.json").read_text())
        for name, h in m["files"].items():
            p = ROOT / "data/cmapss" / name
            raw = p.read_bytes() if p.exists() else gzip.open(str(p) + ".gz").read()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), h, name)

    def test_published_sizes(self):
        for fd, rows, test_rows in (("FD001", 20631, 13096), ("FD003", 24720, 16596)):
            tr, te, rul = C.load(fd)
            self.assertEqual((len(tr.unit), len(tr.units), len(te.unit), len(te.units), len(rul)), (rows, 100, test_rows, 100, 100))

    def test_health_indicator_runs_from_zero_to_one(self):
        tr, _, _ = C.load("FD001")
        hi = C.HealthIndicator.fit(tr)
        s = hi(tr.X)
        start = s[tr.cycle <= 10].mean()
        end = np.mean([s[(tr.unit == k) & (tr.cycle == tr.cycle[tr.unit == k].max())][0] for k in tr.units])
        self.assertLess(abs(start), 0.15)
        self.assertGreater(end, 0.9)


class Scores(unittest.TestCase):
    def test_crps_of_standard_normal(self):
        x = np.random.default_rng(0).standard_normal(20000)
        self.assertAlmostEqual(C.crps_samples(x, 0.0), (np.sqrt(2) - 1) / np.sqrt(np.pi), delta=0.01)

    def test_nasa_score_asymmetry(self):
        self.assertAlmostEqual(C.nasa_score([10], [0]), np.e - 1, places=12)
        self.assertAlmostEqual(C.nasa_score([0], [13]), np.e - 1, places=12)

    def test_weibull_mle_recovers_parameters(self):
        x = 200 * np.random.default_rng(1).weibull(3.0, size=4000)
        w = C.weibull_mle(x)
        self.assertLess(abs(w["shape"] - 3.0), 0.15)
        self.assertLess(abs(w["scale"] - 200), 4)
        self.assertLess(w["shape_ci95"][0], 3.0)
        self.assertGreater(w["shape_ci95"][1], 3.0)


class DegradationModelOnItsOwnData(unittest.TestCase):
    """A fleet simulated from the model itself: the predictive intervals must cover the truth."""

    @classmethod
    def setUpClass(cls):
        rng = np.random.default_rng(3)
        mu0, S0 = np.array([0.0, np.log(0.01), np.log(0.02)]), np.diag([0.05, 0.2, 0.05]) ** 2
        sigma, D = 0.05, 1.0
        rows = []
        for k in range(1, 121):
            a, lb, lg = rng.multivariate_normal(mu0, S0)
            b, g = np.exp(lb), np.exp(lg)
            tf = np.log1p(g * (D - a) / b) / g
            t = np.arange(1, int(tf) + 1, dtype=float)
            s = a + b * np.expm1(g * t) / g + rng.normal(0, sigma, len(t))
            rows += [(k, ti, si) for ti, si in zip(t, s)]
        u = np.array([r[0] for r in rows]); t = np.array([r[1] for r in rows]); s = np.array([r[2] for r in rows])
        X = s[:, None]
        cls.fleet = C.Fleet(u, t, X)
        cls.hi = C.HealthIndicator(np.zeros(1), np.ones(1), np.array([0.0, 1.0]))   # S is observed directly

    def test_interval_coverage(self):
        train = C.Fleet(self.fleet.unit[self.fleet.unit <= 80], self.fleet.cycle[self.fleet.unit <= 80], self.fleet.X[self.fleet.unit <= 80])
        m = C.DegradationModel.fit(train, None, self.hi)
        rng = np.random.default_rng(4)
        hits, errs = [], []
        for k in range(81, 121):
            t, X = self.fleet.of(k)
            cut = int(rng.integers(len(t) // 3, len(t) - 1))
            r = m.rul_samples(t[:cut], X[:cut], n=2000, rng=rng)
            true = t[-1] - t[cut - 1]
            lo, hi = np.quantile(r, [0.05, 0.95])
            hits.append(lo <= true <= hi); errs.append(np.median(r) - true)
        self.assertGreater(np.mean(hits), 0.75)
        self.assertLess(abs(np.median(errs)), 15)


class Hydraulics(unittest.TestCase):
    def test_walther_passes_through_reference_points(self):
        self.assertAlmostEqual(float(H.walther(40.0)), H.NU40, places=6)
        self.assertAlmostEqual(float(H.walther(100.0)), H.NU100, places=6)
        self.assertGreater(float(H.walther(30.0)), float(H.walther(50.0)))

    def test_arrhenius_doubling(self):
        ea = H.ea_for_doubling(65.0, 10.0)
        self.assertAlmostEqual(float(H.arrhenius_factor(70.0, 60.0, ea)), 2.0, places=9)
        self.assertTrue(55e3 < ea < 75e3)

    def test_compensation_recovers_known_model(self):
        T = np.random.default_rng(5).uniform(30, 60, 300)
        q = 8.0 - 6.0 / H.walther(T)
        c = H.Compensation().fit(q, T)
        self.assertAlmostEqual(c.Qth, 8.0, places=6)
        self.assertAlmostEqual(c.K, 6.0, places=5)
        self.assertLess(np.abs(c.deficit(q, T)).max(), 1e-9)

    def test_real_excerpt_flow_drops_with_leakage(self):
        z = np.load(ROOT / "tests/fixtures/hydraulic_excerpt.npz")
        F = H.plateau_features(z["PS1_10"].astype(float), z["FS1"].astype(float), z["EPS1_10"].astype(float))
        prof = z["profile"]
        self.assertFalse(np.isnan(F[:, 0]).any())
        for cooler in (20, 100):
            q = [np.median(F[(prof[:, 0] == cooler) & (prof[:, 2] == k), 0]) for k in (0, 1, 2)]
            self.assertGreater(q[0], q[1]); self.assertGreater(q[1], q[2])
            eta = [np.median(F[(prof[:, 0] == cooler) & (prof[:, 2] == k), 2]) for k in (0, 1, 2)]
            self.assertGreater(eta[0], eta[2])


if __name__ == "__main__":
    unittest.main()
