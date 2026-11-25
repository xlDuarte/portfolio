"""Verification of the Plackett–Luce ranking model (#111) and the sector benchmark (#014)."""
import unittest

import numpy as np

from race_strategy import benchmark as B
from race_strategy import ranking as RK
from race_strategy.data import lap_table, load


def synthetic_events(w, n_events=60, n_drivers=12, seed=0):
    """Events whose finishing orders are exact Plackett–Luce draws with utilities w·(−X)."""
    rng = np.random.default_rng(seed)
    out = []
    for e in range(n_events):
        X = rng.uniform(1, 20, size=(n_drivers, len(w)))
        s = RK.features(X, list(range(len(w)))) @ w
        order = np.argsort(-(s + rng.gumbel(size=n_drivers)))
        pos = np.empty(n_drivers, int)
        pos[order] = np.arange(1, n_drivers + 1)
        out.append({"id": e, "name": f"E{e}", "year": 2023 + e // 30, "date": f"{e:04d}", "codes": [f"D{i}" for i in range(n_drivers)],
                    "X": X, "pos": pos})
    return out


class PlackettLuce(unittest.TestCase):
    def test_gradient_matches_finite_differences(self):
        ev = synthetic_events(np.array([0.2, 0.05]), n_events=8)
        w = np.array([0.1, -0.03])
        f, g = RK.neg_loglik(w, ev, [0, 1], 5, 1e-3)
        h = 1e-6
        num = [(RK.neg_loglik(w + h * e, ev, [0, 1], 5, 1e-3)[0] - RK.neg_loglik(w - h * e, ev, [0, 1], 5, 1e-3)[0]) / (2 * h)
               for e in np.eye(2)]
        self.assertTrue(np.allclose(g, num, rtol=1e-5, atol=1e-6))

    def test_mle_recovers_true_weights(self):
        w_true = np.array([0.25, 0.08])
        ev = synthetic_events(w_true, n_events=150, seed=1)
        w, se, _ = RK.fit(ev, [0, 1], k=12, l2=1e-6)
        self.assertTrue(np.all(np.abs(w - w_true) < 3 * se), (w, se))

    def test_probabilities_are_coherent(self):
        ev = synthetic_events(np.array([0.2, 0.05]), n_events=1, seed=2)[0]
        p = RK.probabilities(np.array([0.2, 0.05]), ev, [0, 1], np.random.default_rng(3), n_samples=40000)
        self.assertAlmostEqual(float(np.sum(p["win"])), 1.0, places=9)
        self.assertAlmostEqual(float(np.sum(p["podium"])), 3.0, places=9)
        self.assertAlmostEqual(float(np.sum(p["top10"])), 10.0, places=9)
        self.assertTrue(np.all(p["podium"] >= p["win"] - 0.01) and np.all(p["top10"] >= p["podium"]))

    def test_walk_forward_uses_only_the_past(self):
        ev = synthetic_events(np.array([0.2, 0.05]), n_events=40, seed=4)
        a = RK.walk_forward(ev, [0, 1], first_year=2024)
        changed = [dict(e) for e in ev]
        changed[-1] = {**changed[-1], "pos": changed[-1]["pos"][::-1].copy()}     # tamper with the last event
        b = RK.walk_forward(changed, [0, 1], first_year=2024)
        self.assertEqual(a[0]["win"], b[0]["win"])                                 # earlier forecasts unchanged

    def test_calibrated_forecasts_have_small_ece(self):
        rng = np.random.default_rng(5)
        preds = []
        for _ in range(400):
            p = rng.dirichlet(np.ones(10))
            winner = rng.choice(10, p=p)
            pos = np.full(10, 10); pos[winner] = 1
            preds.append({"win": p.tolist(), "pos": pos.tolist()})
        rel = RK.reliability(preds, "win")
        self.assertLess(rel["ece"], 0.03)
        self.assertLess(abs(rel["spiegelhalter_z"]), 3)


class SectorBenchmark(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load()
        t = lap_table(cls.data)
        cls.t = t.subset(t.clean)
        cls.S = B.sector_times(cls.data, cls.t)

    def test_sectors_sum_to_lap_time(self):
        ok = np.all(np.isfinite(self.S), axis=1)
        self.assertGreater(ok.mean(), 0.99)
        self.assertLess(np.abs(self.S[ok].sum(axis=1) - self.t.time[ok]).max(), 0.01)

    def test_benchmark_is_centred_and_ranks_are_permutations(self):
        tt, SS, posts, lap = B.fit_sectors(self.t, self.S, chains=2, iters=600, burn=200)
        total = sum(B.benchmark(p) for p in posts)
        self.assertLess(np.abs(total.mean(axis=1)).max(), 1e-9)
        rp = B.rank_probabilities(total)
        self.assertAlmostEqual(float(rp["p_fastest"].sum()), 1.0, places=9)
        self.assertAlmostEqual(float(rp["mean_rank"].sum()), sum(range(1, len(lap.drivers) + 1)), places=6)
        # the sum of sector benchmarks agrees with the whole-lap model
        self.assertGreater(np.corrcoef(total.mean(0), B.benchmark(lap).mean(0))[0, 1], 0.99)


if __name__ == "__main__":
    unittest.main()
