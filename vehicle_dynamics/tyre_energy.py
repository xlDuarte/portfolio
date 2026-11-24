"""Tyre sliding energy and a lumped two-node thermal model driven by the simulated lap.

Sliding power per tyre (pure-slip approximation, no combined-slip interaction):

    P_slide = |F_y| · v · |sin α| + |F_x| · |κ| · v

with α and κ found by inverting the Magic Formula on its rising branch for the force each tyre
carries. Axle forces come from the quasi-steady-state lap (steady yaw balance for F_y, power or
brake balance for F_x) and are shared between the two tyres of an axle in proportion to their
force capacity μ(F_z)F_z, so a saturated axle has both tyres at their peak. Rolling hysteresis adds
P_roll = c_rr F_z v to the carcass.

Thermal model per tyre (two lumped nodes: tread surface s and bulk/carcass b):

    C_s dT_s/dt = η P_slide − h(v) A_t (T_s − T_air) − G (T_s − T_b) − g_c A_c (T_s − T_track)
    C_b dT_b/dt = G (T_s − T_b) + P_roll − h(v) A_w (T_b − T_air) − h_i A_i (T_b − T_air)

(A_t tread, A_w sidewalls, A_i inner liner). The forced-convection slope h₁ in h(v) = h₀ + h₁v is
the only tuned value: it is set so the rear carcass settles near a nominal 105 °C
(:func:`calibrate_convection`), a declared hypothesis, not a measurement.

Every parameter is a declared order-of-magnitude hypothesis (see :class:`ThermalParams`); there
is no public tyre-temperature measurement to calibrate against, so the temperatures are a model
output, not validated. The sliding *energy* per lap is what links to the measured degradation.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .qss import LapResult
from .vehicle import Car, G

AXLES = ("dianteiro", "traseiro")


def _invert_rising(curve, target, fz, x_max):
    """Slip value giving |force| = target on the rising branch of curve(x, fz), vectorised (bisection)."""
    # peak of the rising branch: scan a coarse grid, then the target is capped just below it so a
    # saturated tyre sits at its peak slip instead of jumping to the bound
    grid = np.linspace(0.0, x_max, 121)
    vals = np.abs(np.stack([curve(np.full_like(fz, g), fz) for g in grid]))
    k = np.argmax(vals, axis=0)
    peak = np.take_along_axis(vals, k[None], axis=0)[0]
    x_peak = grid[k]
    target = np.minimum(np.abs(target), 0.999 * peak)
    lo = np.zeros_like(target)
    hi = x_peak.astype(float) * np.ones_like(target)
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        f = np.abs(curve(mid, fz))
        go_up = f < target
        lo, hi = np.where(go_up, mid, lo), np.where(go_up, hi, mid)
    return 0.5 * (lo + hi)


def tyre_forces(car: Car, res: LapResult, grade=None):
    """Per-tyre vertical load, lateral and longitudinal force (N) at every point of the lap.

    Order of tyres: FL, FR, RL, RR (left/right by the sign convention of ``Car.wheel_loads``).
    """
    v, ax, ay = res.v, res.ax, res.ay
    grade = np.zeros_like(v) if grade is None else grade
    fz = np.array(car.wheel_loads(ax, ay, v))
    fz = np.maximum(fz, 1.0)
    m, l = car.mass, car.wheelbase
    drag, _ = car.aero(v)
    fx_total = m * ax + drag + car.crr * m * G + m * G * np.sin(grade)
    traction = fx_total >= 0
    fx_f = np.where(traction, 0.0, car.brake_balance * fx_total)
    fx_r = np.where(traction, fx_total, (1 - car.brake_balance) * fx_total)
    fy_f = m * ay * car.b / l
    fy_r = m * ay * car.a / l
    cx, cy = car.tyre.capacity(fz)
    fy = np.vstack([fy_f * cy[:2] / cy[:2].sum(axis=0), fy_r * cy[2:] / cy[2:].sum(axis=0)])
    fx = np.vstack([fx_f * cx[:2] / cx[:2].sum(axis=0), fx_r * cx[2:] / cx[2:].sum(axis=0)])
    return fz, fx, fy


def sliding_power(car: Car, res: LapResult, grade=None):
    """Sliding power per tyre (W), shape (4, n), plus slip angle (rad) and slip ratio."""
    fz, fx, fy = tyre_forces(car, res, grade)
    t = car.tyre
    alpha = _invert_rising(lambda a, f: t.fy(a, f), fy, fz, 0.30)
    kappa = _invert_rising(lambda k, f: t.fx(k, f), fx, fz, 0.30)
    v = res.v[None, :]
    p = np.abs(fy) * v * np.abs(np.sin(alpha)) + np.abs(fx) * np.abs(kappa) * v
    return p, alpha, kappa, fz


def lap_energy(car: Car, res: LapResult, ds) -> dict:
    """Sliding and rolling energy per tyre over one lap (J), integrated in time (dt = ds / v)."""
    p, alpha, kappa, fz = sliding_power(car, res)
    dt = ds / np.maximum(res.v, 1e-3)
    e_slide = (p * dt[None, :]).sum(axis=1)
    e_roll = (ThermalParams().crr_tyre * fz * res.v[None, :] * dt[None, :]).sum(axis=1)
    return {"slide_J": e_slide, "roll_J": e_roll, "power_W": p, "alpha": alpha, "kappa": kappa, "fz": fz, "dt": dt}


@dataclass(frozen=True)
class ThermalParams:
    """Order-of-magnitude hypotheses for an 18-inch slick (not measured on any real tyre)."""
    c_s: float = 3.7e3          # J/K, tread surface layer (~2 kg rubber × 1.8 kJ/kg K)
    c_b: float = 1.4e4          # J/K, bulk tread + carcass (~8 kg × 1.7 kJ/kg K)
    g_sb: float = 40.0          # W/K, conduction surface → bulk (k ≈ 0.25 W/m K, 0.9 m², 6 mm)
    area_t: float = 0.9         # m², tread surface exposed to air
    area_w: float = 0.5         # m², sidewalls (cool the carcass)
    h0: float = 8.0             # W/m² K, convection at rest
    h1: float = 2.0             # W/m² K per m/s, forced convection slope
    area_c: float = 0.035       # m², contact patch
    g_c: float = 2000.0         # W/m² K, contact conductance to the track
    area_i: float = 0.6         # m², inner liner to inflation gas/rim
    h_i: float = 15.0           # W/m² K
    eta: float = 0.5            # share of sliding power that heats the tyre (rest to the track and wear debris)
    crr_tyre: float = 0.010     # rolling-loss coefficient that heats the carcass


def thermal_stint(power_W, fz, v, dt, t_air: float, t_track: float, laps: int, tp: ThermalParams = ThermalParams(),
                  t0: float = 70.0, substeps: int = 4):
    """Integrate the two-node model over ``laps`` repetitions of the lap (explicit Euler with substeps).

    Returns per-tyre surface and bulk temperature at each point of the last lap and the
    lap-by-lap means. t0 is the blanket temperature at the start of the stint.
    """
    n_tyres, n = power_W.shape
    ts = np.full(n_tyres, t0, float)
    tb = np.full(n_tyres, t0, float)
    lap_means = []
    for k in range(laps):
        trace_s = np.empty((n_tyres, n))
        trace_b = np.empty((n_tyres, n))
        acc = np.zeros(n_tyres)
        for i in range(n):
            h = tp.h0 + tp.h1 * v[i]
            p_roll = tp.crr_tyre * fz[:, i] * v[i]
            step = dt[i] / substeps
            for _ in range(substeps):
                q_s = (tp.eta * power_W[:, i] - h * tp.area_t * (ts - t_air) - tp.g_sb * (ts - tb)
                       - tp.g_c * tp.area_c * (ts - t_track))
                q_b = tp.g_sb * (ts - tb) + p_roll - (h * tp.area_w + tp.h_i * tp.area_i) * (tb - t_air)
                ts = ts + step * q_s / tp.c_s
                tb = tb + step * q_b / tp.c_b
            trace_s[:, i], trace_b[:, i] = ts, tb
            acc += ts * dt[i]
        lap_means.append({"surface": (acc / dt.sum()).tolist(), "bulk": trace_b.mean(axis=1).tolist()})
    return trace_s, trace_b, lap_means


def calibrate_convection(power_W, fz, v, dt, t_air, t_track, target_rear_bulk: float = 105.0, laps: int = 25,
                         tp: ThermalParams = ThermalParams()) -> float:
    """h₁ such that the mean rear carcass temperature on the last of ``laps`` laps equals the target.

    The steady carcass temperature falls monotonically with h₁, so bisection on [0.05, 6] suffices.
    """
    from dataclasses import replace
    lo, hi = 0.05, 6.0
    for _ in range(16):
        mid = 0.5 * (lo + hi)
        _, _, lm = thermal_stint(power_W, fz, v, dt, t_air, t_track, laps, replace(tp, h1=mid))
        rear = float(np.mean(lm[-1]["bulk"][2:]))
        lo, hi = (mid, hi) if rear > target_rear_bulk else (lo, mid)
    return 0.5 * (lo + hi)
