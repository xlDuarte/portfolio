"""Unit tests for scripts/telemetry_physics.py against analytic cases."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from telemetry_physics import G0, BrakeDiscModel, kinematics, resample_hold  # noqa: E402


class TestKinematics(unittest.TestCase):
    def test_uniform_circle_gives_v2_over_r(self):
        t = np.arange(0, 20, 0.25)
        r, v = 100.0, 50.0                       # m, m/s  -> a_lat = 25 m/s^2 (left turn)
        w = v / r
        k = kinematics(t, r * np.cos(w * t), r * np.sin(w * t), np.full_like(t, v))
        mid = slice(10, -10)
        np.testing.assert_allclose(k.a_lat[mid], v * v / r, rtol=0.02)
        np.testing.assert_allclose(k.a_long[mid], 0.0, atol=1e-6)

    def test_constant_braking_on_a_straight(self):
        t = np.arange(0, 3.5, 0.25)              # stops at 4.1 s; stay before standstill
        speed = 80.0 - 2 * G0 * t                # 2 g deceleration
        x = np.cumsum(speed) * 0.25
        k = kinematics(t, x, np.zeros_like(t), speed)
        np.testing.assert_allclose(k.a_long_g[3:-3], -2.0, atol=1e-6)
        np.testing.assert_allclose(k.a_lat[3:-3], 0.0, atol=1e-6)

    def test_rejects_non_uniform_clock(self):
        t = np.array([0, 0.25, 0.5, 0.8, 1.0, 1.25, 1.5, 1.75, 2.0])
        with self.assertRaises(ValueError):
            kinematics(t, t, t, t)

    def test_hold_resampling(self):
        out = resample_hold(np.array([0.0, 1.0, 2.0]), np.array([3, 4, 5]), np.array([0.5, 1.0, 1.9, 9.0]))
        self.assertEqual(out.tolist(), [3, 4, 4, 5])


class TestBrakeDisc(unittest.TestCase):
    def test_cools_towards_ambient_without_braking(self):
        m = BrakeDiscModel(spin_up_passes=1)
        t = np.arange(0, 300, 0.25)
        temp = m.simulate(t, np.full_like(t, 60.0), np.zeros_like(t), start_c=800.0)
        self.assertTrue(np.all(np.diff(temp) <= 1e-9))
        self.assertLess(temp[-1], 60.0)

    def test_energy_balance_of_a_single_stop(self):
        """Adiabatic case: temperature rise equals braking energy into the disc / heat capacity."""
        m = BrakeDiscModel(h0=0.0, h1=0.0, emissivity=0.0, cda_m2=0.0, spin_up_passes=1)
        t = np.arange(0, 3.0001, 0.25)
        a = np.full_like(t, -4 * G0)
        v = np.maximum(80.0 + a * t, 0.0)
        temp = m.simulate(t, v, a, start_c=300.0)
        p = m.disc_power(v, a)
        energy = np.trapezoid(p, t) * m.heat_to_disc
        self.assertAlmostEqual(temp[-1] - 300.0, energy / (m.disc_mass_kg * m.disc_c), delta=1.0)


if __name__ == "__main__":
    unittest.main()
