"""Verification of the bearing-diagnostics chain (phase 4a: #004, #104, #052).

Runs without the 130 MB download: synthetic signals with known truth plus the committed 2 s
excerpts of four real CWRU records (tests/fixtures/cwru_excerpt.npz).
"""
import unittest

import numpy as np

from bearings import dsp
from bearings import signatures as G
from bearings.data import FS, load_fixture, manifest, windows
from bearings.diagnosis import TYPES, indicators
from bearings.kinematics import FAULT_FREQ, SKF_6205
from bearings.learn import Novelty, Softmax, auc, ledoit_wolf
from bearings.simulate import fault_signal


class Kinematics(unittest.TestCase):
    def test_orders_match_cwru_published_values(self):
        o = SKF_6205.orders()
        for k, v in {"BPFI": 5.4152, "BPFO": 3.5848, "FTF": 0.39828, "2BSF": 4.7135}.items():
            self.assertAlmostEqual(o[k], v, delta=2e-4, msg=k)

    def test_identities(self):
        o = SKF_6205.orders()
        self.assertAlmostEqual(o["BPFO"] + o["BPFI"], SKF_6205.n_balls, places=12)
        self.assertAlmostEqual(o["BPFO"], SKF_6205.n_balls * o["FTF"], places=12)


class SignalProcessing(unittest.TestCase):
    def test_cpw_flattens_magnitude_and_keeps_phase(self):
        x = fault_signal("OR", 6, mesh_amp=4.0, rng=np.random.default_rng(1))
        y = dsp.cpw(x)
        Y, X = np.fft.rfft(y), np.fft.rfft(x - x.mean())
        self.assertLess(np.std(np.abs(Y[1:-1])), 1e-9)
        self.assertLess(np.max(np.abs(np.angle(Y[1:-1] / X[1:-1]))), 1e-6)

    def test_envelope_finds_simulated_defect(self):
        rng = np.random.default_rng(2)
        fq = SKF_6205.frequencies(29.95)
        for kind in ("OR", "IR"):
            f, S = dsp.ses(dsp.cpw(fault_signal(kind, 12, rng=rng)), FS, 600)
            h = {t: dsp.harmonic_prominence(f, S, fq[FAULT_FREQ[t]]) for t in TYPES}
            self.assertEqual(max(h, key=h.get), kind)
            self.assertGreater(h[kind], 6.0)               # well above the 1 % false-alarm level (≈ 4.6 dB)
        f, S = dsp.ses(dsp.cpw(fault_signal("N", 0, rng=rng)), FS, 600)
        self.assertLess(max(dsp.harmonic_prominence(f, S, fq[FAULT_FREQ[t]]) for t in TYPES), 5.0)

    def test_spectral_kurtosis_points_at_the_resonance(self):
        x = fault_signal("OR", 9, fn=3500, rng=np.random.default_rng(3))
        fc, bw, k = dsp.sk_band(x, FS)
        self.assertLess(abs(fc - 3500), bw)
        self.assertGreater(k, 1.0)
        noise = np.random.default_rng(4).standard_normal(12000)
        self.assertLess(dsp.sk_band(noise, FS)[2], 0.5)        # SK of Gaussian noise ≈ 0


class RealExcerpts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.recs = {r.cls: r for r in load_fixture()}

    def test_fixture_matches_manifest(self):
        ids = {r["id"]: r for r in manifest()["records"]}
        self.assertEqual(len(ids), 40)
        for r in self.recs.values():
            self.assertEqual(ids[r.id]["class"], r.cls)
            self.assertEqual(len(r.x), 24000)

    def test_envelope_diagnosis_on_real_records(self):
        Hn, _ = indicators(self.recs["N"], "cpw")
        for kind in ("IR", "OR"):
            H, _ = indicators(self.recs[kind], "cpw")
            self.assertTrue(np.all(np.array(TYPES)[H.argmax(1)] == kind), kind)
            self.assertGreater(H.max(1).min(), Hn.max() + 2.0)

    def test_order_signature_is_speed_invariant(self):
        """The same simulated defect at two speeds matches better on the order axis than in Hz."""
        rng = np.random.default_rng(5)
        a = fault_signal("IR", 12, fr=29.95, rng=rng)
        b = fault_signal("IR", 12, fr=28.75, rng=rng)
        so = G.signature(a, 29.95, "order") @ G.signature(b, 28.75, "order")
        sh = G.signature(a, 29.95, "hz") @ G.signature(b, 28.75, "hz")
        self.assertGreater(so, sh + 0.1)


class Learners(unittest.TestCase):
    def test_auc(self):
        self.assertEqual(auc(np.array([0, 1, 2.0]), np.array([3, 4.0])), 1.0)
        self.assertEqual(auc(np.array([1.0, 1.0]), np.array([1.0])), 0.5)
        rng = np.random.default_rng(6)
        n, p = rng.standard_normal(4000), rng.standard_normal(4000) + 1
        self.assertAlmostEqual(auc(n, p), 0.7602, delta=0.015)   # Φ(1/√2)

    def test_ledoit_wolf_and_novelty(self):
        rng = np.random.default_rng(7)
        X = rng.standard_normal((40, 30))
        C, d = ledoit_wolf(X)
        self.assertTrue(0 <= d <= 1)
        self.assertGreater(np.linalg.eigvalsh(C).min(), 0)
        m = Novelty().fit(X)
        self.assertGreater(m.score(X + 5).mean(), 10 * m.score(X).mean())

    def test_softmax_separates_classes(self):
        rng = np.random.default_rng(8)
        X = np.vstack([rng.standard_normal((100, 2)) + c for c in ([0, 0], [6, 0], [0, 6])])
        y = np.repeat(np.array(["a", "b", "c"]), 100)
        self.assertGreater(np.mean(Softmax().fit(X, y).predict(X) == y), 0.98)

    def test_windows(self):
        self.assertEqual(windows(np.arange(25), 10).tolist(), [list(range(10)), list(range(10, 20))])


if __name__ == "__main__":
    unittest.main()
