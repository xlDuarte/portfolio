"""Verification of race_strategy (pace model, strategy optimisers) and the tyre energy/thermal model."""
import math
import unittest

import numpy as np

from race_strategy.pace import Design, crps_samples, gibbs, split_rhat
from race_strategy.strategy import (H, S, Pace, Plan, equivalence_key, plan_cost, plan_matrix, plans, sdp,
                                    simulate_policy, stint_cost)


class _Table:
    """Minimal stand-in for LapTable used by Design.of."""

    def __init__(self, driver, compound, age, lap, time):
        self.driver, self.compound, self.age, self.lap, self.time = driver, compound, age, lap, time

    def __len__(self):
        return len(self.lap)


def synthetic_laps(seed=0, t_errors=False):
    rng = np.random.default_rng(seed)
    drivers = [f"D{i:02d}" for i in range(10)]
    u = rng.normal(0, 0.5, 10)
    truth = {"intercept": 95.0, "hard": 0.3, "age_soft": 0.12, "age_hard": 0.07, "race_lap": -0.06}
    rows = []
    for k, d in enumerate(drivers):
        stop = int(rng.integers(15, 25))
        for lap in range(2, 51):
            hard = lap > stop
            age = (lap - stop - 1) if hard else lap - 1
            mu = (truth["intercept"] + truth["hard"] * hard + (truth["age_hard"] if hard else truth["age_soft"]) * age
                  + truth["race_lap"] * (lap - 30) + u[k])
            e = rng.standard_t(3) * 0.2 if t_errors else rng.normal(0, 0.3)
            rows.append((d, "HARD" if hard else "SOFT", age, lap, mu + e))
    cols = list(zip(*rows))
    return _Table(*(np.array(c) for c in cols)), truth


class TestPaceModel(unittest.TestCase):
    def check_recovery(self, t_errors, grid):
        table, truth = synthetic_laps(1, t_errors)
        post = gibbs(Design.of(table), chains=3, iters=1500, burn=500, seed=3, nu_grid=grid)
        b = post.beta
        for j, name in enumerate(("intercept", "hard", "age_soft", "age_hard", "race_lap")):
            lo, hi = np.quantile(b[:, :, j], [0.005, 0.995])
            self.assertTrue(lo <= truth[name] <= hi, (name, lo, hi, truth[name]))
            self.assertLess(split_rhat(b[:, :, j]), 1.05)

    def test_recovers_parameters_gaussian(self):
        self.check_recovery(False, [1e6])

    def test_recovers_parameters_student_t(self):
        self.check_recovery(True, None)

    def test_crps_matches_gaussian_closed_form(self):
        rng = np.random.default_rng(4)
        samples = rng.normal(0.0, 1.0, (40000, 1))
        y = np.array([0.7])
        z = y[0]
        phi = math.exp(-z * z / 2) / math.sqrt(2 * math.pi)
        Phi = 0.5 * (1 + math.erf(z / math.sqrt(2)))
        exact = z * (2 * Phi - 1) + 2 * phi - 1 / math.sqrt(math.pi)
        self.assertAlmostEqual(float(crps_samples(samples, y)[0]), exact, places=2)


class TestStrategy(unittest.TestCase):
    p = Pace(delta_h=0.2, beta_s=0.13, beta_h=0.09, v_driver=0.01)

    def test_stint_cost_closed_form(self):
        brute = sum(float(self.p.lap(np.array(H), np.array(a))) for a in range(4, 4 + 17))
        self.assertAlmostEqual(stint_cost(self.p, H, 4, 17), brute, places=9)

    def test_plan_matrix_equals_direct_cost(self):
        pl = plans(30, max_stops=2, min_stint=5)
        A, k = plan_matrix(pl, 30, start_age=3)
        theta = np.array([self.p.delta_h, self.p.beta_s, self.p.beta_h, self.p.v_driver])
        vec = A @ theta + k * 21.0
        for j in range(0, len(pl), max(1, len(pl) // 40)):
            self.assertAlmostEqual(vec[j], plan_cost(self.p, pl[j], 21.0, 30, 3), places=8)

    def test_every_plan_uses_two_compounds(self):
        self.assertTrue(all(len(set(x.compounds)) >= 2 for x in plans(30, max_stops=3, min_stint=5)))

    def test_equivalent_plans_cost_the_same(self):
        a, b = Plan((S, H, S), (10, 20)), Plan((S, S, H), (10, 20))
        self.assertEqual(equivalence_key(a, 30), equivalence_key(b, 30))
        self.assertAlmostEqual(plan_cost(self.p, a, 20, 30), plan_cost(self.p, b, 20, 30), places=9)

    def test_sdp_without_safety_car_equals_best_static_plan(self):
        laps = 30
        best = min(plan_cost(self.p, x, 20.0, laps, 3) for x in plans(laps, max_stops=3, min_stint=1) if x.compounds[0] == S)
        res = sdp(self.p, 20.0, 10.0, 0.0, 3, laps, S, 3)
        self.assertAlmostEqual(res.expected, best, places=6)

    def test_sdp_expectation_matches_monte_carlo(self):
        laps = 30
        res = sdp(self.p, 20.0, 10.0, 0.03, 3, laps, S, 3)
        mc = simulate_policy(self.p, res.policy, 20.0, 10.0, 0.03, np.random.default_rng(2), 4000, 3, laps)
        self.assertLess(abs(mc.mean() - res.expected), 3 * mc.std() / math.sqrt(len(mc)) + 1e-6)

    def test_safety_car_risk_never_hurts_the_flexible_policy(self):
        laps = 30
        e0 = sdp(self.p, 20.0, 10.0, 0.0, 3, laps, S, 3).expected
        e1 = sdp(self.p, 20.0, 10.0, 0.05, 3, laps, S, 3).expected
        self.assertLessEqual(e1, e0 + 1e-9)        # SC laps cost nothing extra and make stops cheaper


class TestTyreThermal(unittest.TestCase):
    def test_steady_state_matches_linear_solution(self):
        from vehicle_dynamics.tyre_energy import ThermalParams, thermal_stint
        tp = ThermalParams()
        n, v, P, fz = 400, 50.0, 4000.0, 4000.0
        power = np.full((1, n), P)
        loads = np.full((1, n), fz)
        speed = np.full(n, v)
        dt = np.full(n, 0.25)
        t_air, t_track = 20.0, 30.0
        _, _, lm = thermal_stint(power, loads, speed, dt, t_air, t_track, laps=60, tp=tp, t0=60.0)
        h = tp.h0 + tp.h1 * v
        a = np.array([[h * tp.area_t + tp.g_sb + tp.g_c * tp.area_c, -tp.g_sb],
                      [-tp.g_sb, tp.g_sb + h * tp.area_w + tp.h_i * tp.area_i]])
        rhs = np.array([tp.eta * P + h * tp.area_t * t_air + tp.g_c * tp.area_c * t_track,
                        tp.crr_tyre * fz * v + (h * tp.area_w + tp.h_i * tp.area_i) * t_air])
        ts, tb = np.linalg.solve(a, rhs)
        self.assertAlmostEqual(lm[-1]["surface"][0], ts, places=1)
        self.assertAlmostEqual(lm[-1]["bulk"][0], tb, places=1)


if __name__ == "__main__":
    unittest.main()
