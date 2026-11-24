"""Verification of the vehicle-dynamics package against analytical results.

Each test checks the code against a closed-form answer or a conservation law, not against a
stored output, so it fails if the physics is wrong rather than if a number merely changes.
"""
import math
import unittest

import numpy as np

from vehicle_dynamics import Car, Envelope, G, MagicFormula, air_density, simulate
from vehicle_dynamics.track import Track, build_track, fourier_smooth, minimum_curvature


def circle_track(radius=80.0, n=600, ds=2.0, noise=0.0, seed=0):
    rng = np.random.default_rng(seed)
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    x = radius * np.cos(th) + rng.normal(0, noise, n)
    y = radius * np.sin(th) + rng.normal(0, noise, n)
    s = radius * th
    return build_track(s, x, y, np.zeros(n), 2 * np.pi * radius, k=20, ds=ds)


def no_aero_linear_tyre(mu=1.6, **kw):
    """Car whose grip is exactly μ·Fz on every tyre (no load sensitivity) and no aerodynamics."""
    tyre = MagicFormula(pDy1=mu, pDy2=0.0, pDx1=mu, pDx2=0.0, ppy3=0.0, ppy4=0.0)
    return Car(cla=0.0, cda=0.0, crr=0.0, tyre=tyre, **kw)


class TestMagicFormula(unittest.TestCase):
    t = MagicFormula()

    def test_origin_and_odd_symmetry(self):
        self.assertAlmostEqual(float(self.t.fy(0.0, 3500)), 0.0, places=9)
        a = np.radians([1.0, 4.0, 9.0])
        np.testing.assert_allclose(self.t.fy(-a, 3500), -self.t.fy(a, 3500), rtol=1e-12)

    def test_slope_at_origin_is_cornering_stiffness(self):
        h = 1e-6
        slope = float(self.t.fy(h, 4000) - self.t.fy(-h, 4000)) / (2 * h)
        self.assertAlmostEqual(slope / float(self.t.cornering_stiffness(4000)), 1.0, places=5)

    def test_peak_equals_D(self):
        for fz in (2000.0, 3500.0, 7000.0):
            a = np.linspace(0, 0.4, 40001)
            peak = float(np.max(self.t.fy(a, fz)))
            self.assertAlmostEqual(peak / (float(self.t.mu_y(fz)) * fz), 1.0, places=4)

    def test_load_sensitivity_lowers_friction(self):
        mu = self.t.mu_y(np.array([2000.0, 4000.0, 8000.0]))
        self.assertTrue(np.all(np.diff(mu) < 0))

    def test_scaling_factor_is_linear(self):
        self.assertAlmostEqual(float(self.t.scaled(0.8).mu_y(3000) / self.t.mu_y(3000)), 0.8, places=12)


class TestCar(unittest.TestCase):
    def test_air_density_isa(self):
        self.assertAlmostEqual(air_density(1013.25, 15.0, 0.0), 1.2250, places=3)

    def test_loads_conserve_weight_plus_downforce(self):
        car = Car()
        for ax, ay, v in [(0, 0, 0), (12.0, -25.0, 60.0), (-40.0, 30.0, 85.0)]:
            total = sum(car.wheel_loads(ax, ay, v))
            self.assertAlmostEqual(float(total), car.mass * G + float(car.aero(v)[1]), places=6)

    def test_longitudinal_transfer(self):
        car = Car(cla=0.0)
        fl, fr, rl, rr = car.wheel_loads(10.0, 0.0, 0.0)
        static_front = car.mass * G * car.b / car.wheelbase
        self.assertAlmostEqual(float(fl + fr), static_front - car.mass * 10.0 * car.h_cg / car.wheelbase, places=6)

    def test_skidpad_limit_is_mu_g(self):
        car = no_aero_linear_tyre(1.6)
        self.assertAlmostEqual(float(car.ay_max(np.array([20.0]))[0]) / (1.6 * G), 1.0, places=3)

    def test_power_limited_acceleration(self):
        car = no_aero_linear_tyre(50.0, power=500e3)          # grip so high that power always binds
        for v in (30.0, 60.0):
            ax, _ = car.ax_limits(np.array([v]), np.array([0.0]))
            self.assertAlmostEqual(float(ax[0]) / (500e3 / (car.mass * v)), 1.0, places=3)

    def test_braking_limited_by_front_axle_with_fixed_balance(self):
        # front saturates when β m a = μ (m g b/ℓ + m a h/ℓ)  →  a = μ g (b/ℓ) / (β − μ h/ℓ)
        car = no_aero_linear_tyre(1.5, brake_balance=0.75)
        l = car.wheelbase
        expected = 1.5 * G * (car.b / l) / (0.75 - 1.5 * car.h_cg / l)
        _, axn = car.ax_limits(np.array([30.0]), np.array([0.0]))
        self.assertAlmostEqual(-float(axn[0]) / expected, 1.0, places=3)

    def test_grade_shifts_acceleration_by_g_sin_theta(self):
        car = no_aero_linear_tyre(50.0, power=500e3)
        flat, _ = car.ax_limits(np.array([40.0]), np.array([0.0]), 0.0)
        hill, _ = car.ax_limits(np.array([40.0]), np.array([0.0]), math.radians(3.0))
        self.assertAlmostEqual(float(flat[0] - hill[0]), G * math.sin(math.radians(3.0)), places=3)

    def test_top_speed_balances_power_and_drag(self):
        car = Car(crr=0.0)
        v = car.top_speed()
        self.assertAlmostEqual(0.5 * car.rho * car.cda * v ** 3 / car.power, 1.0, places=6)


class TestTrack(unittest.TestCase):
    def test_circle_curvature_length_and_turning(self):
        tr = circle_track(80.0)
        self.assertAlmostEqual(tr.length / (2 * math.pi * 80.0), 1.0, places=5)
        np.testing.assert_allclose(tr.kappa, 1 / 80.0, rtol=1e-4)
        self.assertAlmostEqual(math.degrees(float(np.sum(tr.kappa * tr.ds))), 360.0, places=2)

    def test_fourier_derivative(self):
        length = 100.0
        s = np.linspace(0, length, 400, endpoint=False)
        f = fourier_smooth(s, np.sin(2 * np.pi * 3 * s / length), length, 10, lambdas=[1e-9])
        w = 2 * np.pi * 3 / length
        np.testing.assert_allclose(f(s, 2), -w * w * np.sin(w * s), atol=1e-6)

    def test_gcv_smoothing_recovers_radius_from_noisy_samples(self):
        tr = circle_track(120.0, n=900, noise=0.5, seed=3)
        self.assertLess(abs(float(np.median(tr.kappa)) * 120.0 - 1.0), 0.01)

    def test_minimum_curvature_reduces_curvature_within_bounds(self):
        th = np.linspace(0, 2 * np.pi, 800, endpoint=False)
        r = 200 + 40 * np.cos(3 * th)                     # three-lobed closed curve
        x, y = r * np.cos(th), r * np.sin(th)
        seg = np.hypot(np.diff(np.r_[x, x[0]]), np.diff(np.r_[y, y[0]]))
        s = np.concatenate([[0.0], np.cumsum(seg)[:-1]])
        tr = build_track(s, x, y, np.zeros_like(x), float(seg.sum()), k=40, ds=4.0)
        new, off = minimum_curvature(tr, 5.0)
        self.assertLess(np.sum(new.kappa ** 2 * new.ds), np.sum(tr.kappa ** 2 * tr.ds))
        self.assertLessEqual(float(np.abs(off).max()), 5.0 + 1e-6)


class TestLapSimulation(unittest.TestCase):
    def test_constant_radius_lap_time(self):
        tr = circle_track(80.0)
        car = no_aero_linear_tyre(1.6)
        res = simulate(car, tr)
        expected = 2 * math.pi * 80.0 / math.sqrt(1.6 * G * 80.0)
        self.assertAlmostEqual(res.lap_time / expected, 1.0, places=3)

    def test_more_grip_is_never_slower(self):
        th = np.linspace(0, 2 * np.pi, 800, endpoint=False)
        r = 300 + 120 * np.cos(2 * th)
        x, y = r * np.cos(th), r * np.sin(th)
        seg = np.hypot(np.diff(np.r_[x, x[0]]), np.diff(np.r_[y, y[0]]))
        s = np.concatenate([[0.0], np.cumsum(seg)[:-1]])
        tr = build_track(s, x, y, np.zeros_like(x), float(seg.sum()), k=40, ds=4.0)
        base = Car()
        t1 = simulate(base, tr).lap_time
        t2 = simulate(base.with_(lambda_muy=1.1, lambda_mux=1.1), tr).lap_time
        t3 = simulate(base.with_(mass=base.mass + 50), tr).lap_time
        self.assertLess(t2, t1)
        self.assertGreater(t3, t1)

    def test_envelope_table_matches_direct_solution(self):
        car = Car()
        env = Envelope.of(car)
        for v, frac in [(30.0, 0.0), (55.5, 0.4), (80.0, 0.8)]:
            ay = float(car.ay_max(np.array([v]))[0]) * frac
            axp, axn, _, _ = env.lookup(v, ay)
            dp, dn = car.ax_limits(np.array([v]), np.array([ay]))
            self.assertLess(abs(axp - float(dp[0])), 0.05 * G)
            self.assertLess(abs(axn - float(dn[0])), 0.05 * G)


class TestCalibration(unittest.TestCase):
    def test_recovers_known_parameters_from_synthetic_trace(self):
        """Simulate a lap with known θ, add noise, fit, and require each estimate within 3 SE."""
        from vehicle_dynamics.calibrate import PARAMS, car_from, fit_lap
        from vehicle_dynamics.openf1 import LapTrace
        th = np.linspace(0, 2 * np.pi, 900, endpoint=False)
        r = 420 + 150 * np.cos(2 * th) + 60 * np.sin(5 * th)
        x, y = r * np.cos(th), r * np.sin(th)
        seg = np.hypot(np.diff(np.r_[x, x[0]]), np.diff(np.r_[y, y[0]]))
        s = np.concatenate([[0.0], np.cumsum(seg)[:-1]])
        tr = build_track(s, x, y, np.zeros_like(x), float(seg.sum()), k=40, ds=4.0)
        base = Car()
        truth = np.array([0.95, 0.75, 3.8, 1.4, 600e3])
        res = simulate(car_from(truth, base), tr)
        rng = np.random.default_rng(7)
        s_meas = np.sort(rng.uniform(0, tr.length, 300))
        v_meas = np.interp(s_meas, res.s, res.v) + rng.normal(0, 1.0, s_meas.size)
        lap = LapTrace(0, "SYN", "teste", 1, res.lap_time, s_meas, v_meas, s_meas / 60.0, True)
        fit = fit_lap(lap, tr, base)
        z = np.abs(fit.theta - truth) / fit.se
        self.assertTrue(np.all(z < 3.0), dict(zip(PARAMS, np.round(z, 2))))
        self.assertLess(abs(fit.lap_time_sim - res.lap_time), 0.3)


if __name__ == "__main__":
    unittest.main()
