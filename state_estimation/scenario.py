"""Ground truth from the calibrated Bahrain lap, simulated sensors and Monte Carlo evaluation.

There is no public IMU or sideslip measurement for Formula 1, so the estimators are evaluated
against a simulated truth whose inputs come from the real lap: the speed profile and the path
curvature of the calibrated quasi-steady-state lap of phase 1. A driver model closes the loop on
speed and yaw rate. The truth uses the per-wheel tyre model with lateral load transfer; the filters
use the axle model. Sensor specifications are declared hypotheses typical of automotive MEMS units.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
from scipy.stats import chi2

from vehicle_dynamics import Car, MagicFormula

from .bicycle import BicycleParams, derivatives, steady_state_steer

ROOT = Path(__file__).resolve().parents[1]
LAPSIM = ROOT / "site" / "motorsport" / "data" / "lapsim-bahrain.json"


@dataclass(frozen=True)
class Sensors:
    """1σ noise (hypotheses): automotive-grade MEMS IMU, steering encoder, wheel-speed sensor."""
    rate_hz: float = 50.0
    gyro: float = np.radians(0.3)          # rad/s white noise
    gyro_bias0: float = np.radians(0.5)    # rad/s initial bias spread
    gyro_bias_rw: float = np.radians(0.02)  # rad/s per √s random walk
    accel: float = 0.05 * 9.80665          # m/s² on a_x and a_y
    steer: float = np.radians(0.1)         # rad on the road-wheel angle
    wheel_speed: float = 0.2               # m/s


def load_calibrated():
    d = json.loads(LAPSIM.read_text(encoding="utf-8"))
    spec = dict(d["car"])
    tyre = MagicFormula(**spec.pop("tyre"))
    return d, Car(**spec, tyre=tyre)


@dataclass
class Truth:
    t: np.ndarray
    x: np.ndarray               # (T, 3) v_x, v_y, r at sensor rate
    delta: np.ndarray
    ax: np.ndarray              # body longitudinal acceleration input
    ay: np.ndarray
    s: np.ndarray               # distance travelled (m)
    lam: float

    @property
    def beta(self):
        return np.arctan2(self.x[:, 1], self.x[:, 0])


def make_truth(lam_scale: float = 1.0, speed_factor: float = 0.97, duration: float | None = None,
               dt: float = 0.002, rate_hz: float = 50.0, iz: float = 1200.0,
               yaw_gain: float = 0.3) -> tuple[Truth, BicycleParams, object]:
    """Integrate the per-wheel model along the Bahrain line with a speed and yaw-rate driver model.

    lam_scale multiplies the calibrated friction of the *truth* car (e.g. 0.9 = worn tyres the
    filter does not know about). The driver targets speed_factor × the QSS speed, leaving margin
    because the per-wheel car has less grip than the axle model the QSS envelope used.
    """
    d, car = load_calibrated()
    tyre_true = car.tyre.scaled(lambda_muy=car.tyre.lambda_muy * lam_scale)
    p = BicycleParams.from_car(car, iz=iz)
    tr = d["track"]
    s_tab, k_tab, L = np.array(tr["s"]), np.array(tr["kappa"]), tr["length_m"]
    v_tab = np.array(d["sim"]["v_kmh"]) / 3.6 * speed_factor * np.sqrt(lam_scale)
    kfun = lambda s: np.interp(s % L, s_tab, k_tab, period=L)
    vfun = lambda s: np.interp(s % L, s_tab, v_tab, period=L)
    dvds = np.gradient(v_tab, s_tab)
    dvfun = lambda s: np.interp(s % L, s_tab, dvds, period=L)
    T_end = (duration if duration is not None else float(d["sim"]["t"][-1]) / speed_factor)
    n = int(T_end / dt)
    every = int(round(1.0 / (rate_hz * dt)))
    # steady-state steer table δ_ss(v, r) at a_x = 0 (vectorised once; the yaw feedback absorbs the rest)
    vg = np.linspace(5.0, 100.0, 96)
    rg = np.linspace(-2.0, 2.0, 161)
    VV, RR = np.meshgrid(vg, rg, indexing="ij")
    D_tab, _ = steady_state_steer(p, tyre_true, VV, RR, np.zeros_like(VV))

    def delta_ss(v, r):
        i = np.clip((v - vg[0]) / (vg[1] - vg[0]), 0, len(vg) - 1.001)
        j = np.clip((r - rg[0]) / (rg[1] - rg[0]), 0, len(rg) - 1.001)
        i0, j0 = int(i), int(j)
        ti, tj = i - i0, j - j0
        return ((D_tab[i0, j0] * (1 - tj) + D_tab[i0, j0 + 1] * tj) * (1 - ti)
                + (D_tab[i0 + 1, j0] * (1 - tj) + D_tab[i0 + 1, j0 + 1] * tj) * ti)

    x = np.array([vfun(0.0), 0.0, vfun(0.0) * kfun(0.0)])
    s = 0.0
    delta_f = 0.0
    out_t, out_x, out_d, out_ax, out_ay, out_s = [], [], [], [], [], []
    for i in range(n):
        v_ref = vfun(s)
        r_ref = x[0] * kfun(s + 0.15 * x[0])         # preview of 0.15 s
        ax = v_ref * dvfun(s) + 2.0 * (v_ref - x[0])
        delta_cmd = delta_ss(x[0], r_ref) + yaw_gain * (r_ref - x[2])
        delta_f += dt / 0.05 * (delta_cmd - delta_f)    # steering actuator / driver lag, τ = 50 ms
        u = np.array([delta_f, ax])
        k1, ay = derivatives(p, tyre_true, x, u, True)
        k2, _ = derivatives(p, tyre_true, x + 0.5 * dt * k1, u, True)
        k3, _ = derivatives(p, tyre_true, x + 0.5 * dt * k2, u, True)
        k4, _ = derivatives(p, tyre_true, x + dt * k3, u, True)
        if i % every == 0:
            out_t.append(i * dt); out_x.append(x.copy()); out_d.append(delta_f); out_ax.append(ax)
            out_ay.append(float(ay)); out_s.append(s)
        x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        s += x[0] * dt
    return Truth(np.array(out_t), np.array(out_x), np.array(out_d), np.array(out_ax), np.array(out_ay),
                 np.array(out_s), car.tyre.lambda_muy * lam_scale), p, car.tyre


def sensors(truth: Truth, sens: Sensors, n_runs: int, seed: int):
    """Noisy inputs U (N, T, 2) and measurements Z (N, T, 3) plus the true gyro bias (N, T)."""
    rng = np.random.default_rng(seed)
    T = len(truth.t)
    dt = 1.0 / sens.rate_hz
    bias = rng.normal(0, sens.gyro_bias0, (n_runs, 1)) + np.cumsum(
        rng.normal(0, sens.gyro_bias_rw * np.sqrt(dt), (n_runs, T)), axis=1)
    U = np.stack([truth.delta[None, :] + rng.normal(0, sens.steer, (n_runs, T)),
                  truth.ax[None, :] + rng.normal(0, sens.accel, (n_runs, T))], axis=-1)
    Z = np.stack([truth.x[None, :, 2] + bias + rng.normal(0, sens.gyro, (n_runs, T)),
                  truth.ay[None, :] + rng.normal(0, sens.accel, (n_runs, T)),
                  truth.x[None, :, 0] + rng.normal(0, sens.wheel_speed, (n_runs, T))], axis=-1)
    return U, Z, bias


def consistency(err, P, n_runs, alpha=0.05):
    """Average NEES over runs at each time and the two-sided χ² acceptance band (Bar-Shalom et al., 2001)."""
    nees = np.einsum("nti,ntij,ntj->nt", err, np.linalg.inv(P), err)
    dof = err.shape[-1]
    lo, hi = chi2.ppf([alpha / 2, 1 - alpha / 2], n_runs * dof) / n_runs
    avg = nees.mean(axis=0)
    return avg, (lo, hi)


def integrator_baseline(Z, U, dt):
    """β̇ = a_y / v_x − r from raw sensors (gyro bias included): the estimate a filter must beat."""
    beta = np.zeros(Z.shape[:2])
    for k in range(1, Z.shape[1]):
        beta[:, k] = beta[:, k - 1] + dt * (Z[:, k, 1] / np.maximum(Z[:, k, 2], 5.0) - Z[:, k, 0])
    return beta
