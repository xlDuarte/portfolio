"""Nonlinear single-track (bicycle) model with Magic Formula axle forces.

States (body frame, SI): v_x longitudinal speed, v_y lateral speed, r yaw rate.
Inputs: front steer angle δ and longitudinal acceleration a_x (from the drive/brake balance).

    v̇_x = a_x + v_y r
    v̇_y = (F_yf cos δ + F_yr) / m − v_x r
    ṙ   = (a F_yf cos δ − b F_yr) / I_z

    α_f = δ − atan((v_y + a r) / v_x),   α_r = −atan((v_y − b r) / v_x)
    a_y = (F_yf cos δ + F_yr) / m        (what an accelerometer at the CG measures, roll ignored)

The *truth* model splits each axle into two wheels with lateral load transfer and evaluates the
Magic Formula per wheel; the *filter* model uses one equivalent tyre per axle at half the axle
load. That gap, plus a friction scale the filter does not know, is the model mismatch the
estimators must tolerate. Sideslip β = atan(v_y / v_x).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from vehicle_dynamics import Car, G


@dataclass(frozen=True)
class BicycleParams:
    m: float
    a: float                    # CG to front axle (m)
    b: float                    # CG to rear axle (m)
    iz: float                   # yaw inertia (kg m²), hypothesis
    h: float
    track_f: float
    track_r: float
    roll_share_f: float
    rho: float
    cla: float
    aero_balance: float

    @classmethod
    def from_car(cls, car: Car, iz: float = 1200.0) -> "BicycleParams":
        return cls(car.mass, car.a, car.b, iz, car.h_cg, car.track_f, car.track_r, car.roll_share_f, car.rho,
                   car.cla, car.aero_balance)


def axle_loads(p: BicycleParams, vx, ax):
    """Front and rear axle loads (N) with downforce and longitudinal transfer."""
    l = p.a + p.b
    lift = 0.5 * p.rho * p.cla * vx * vx
    fzf = p.m * G * p.b / l - p.m * ax * p.h / l + lift * p.aero_balance
    fzr = p.m * G * p.a / l + p.m * ax * p.h / l + lift * (1 - p.aero_balance)
    return np.maximum(fzf, 100.0), np.maximum(fzr, 100.0)


def slip_angles(p: BicycleParams, vx, vy, r, delta):
    vx = np.maximum(vx, 1.0)
    af = delta - np.arctan((vy + p.a * r) / vx)
    ar = -np.arctan((vy - p.b * r) / vx)
    return af, ar


def lateral_forces(p: BicycleParams, tyre, vx, vy, r, delta, ax, per_wheel: bool = False):
    """Axle lateral forces (F_yf, F_yr). per_wheel=True adds lateral load transfer (truth model)."""
    af, ar = slip_angles(p, vx, vy, r, delta)
    fzf, fzr = axle_loads(p, vx, ax)
    if not per_wheel:
        return 2 * tyre.fy(af, fzf / 2), 2 * tyre.fy(ar, fzr / 2)
    # lateral transfer from the current lateral acceleration (one fixed-point pass is enough here)
    fyf0, fyr0 = 2 * tyre.fy(af, fzf / 2), 2 * tyre.fy(ar, fzr / 2)
    ay = (fyf0 * np.cos(delta) + fyr0) / p.m
    dyf = p.roll_share_f * p.m * ay * p.h / p.track_f
    dyr = (1 - p.roll_share_f) * p.m * ay * p.h / p.track_r
    fyf = tyre.fy(af, np.maximum(fzf / 2 - dyf, 50)) + tyre.fy(af, fzf / 2 + dyf)
    fyr = tyre.fy(ar, np.maximum(fzr / 2 - dyr, 50)) + tyre.fy(ar, fzr / 2 + dyr)
    return fyf, fyr


def derivatives(p: BicycleParams, tyre, x, u, per_wheel: bool = False):
    """x = (..., 3) [v_x, v_y, r];  u = (..., 2) [δ, a_x]. Returns ẋ and the lateral acceleration."""
    vx, vy, r = x[..., 0], x[..., 1], x[..., 2]
    delta, ax = u[..., 0], u[..., 1]
    fyf, fyr = lateral_forces(p, tyre, vx, vy, r, delta, ax, per_wheel)
    ay = (fyf * np.cos(delta) + fyr) / p.m
    dvx = ax + vy * r
    dvy = ay - vx * r
    dr = (p.a * fyf * np.cos(delta) - p.b * fyr) / p.iz
    return np.stack([dvx, dvy, dr], axis=-1), ay


def rk4(p, tyre, x, u, dt, per_wheel=False):
    k1, _ = derivatives(p, tyre, x, u, per_wheel)
    k2, _ = derivatives(p, tyre, x + 0.5 * dt * k1, u, per_wheel)
    k3, _ = derivatives(p, tyre, x + 0.5 * dt * k2, u, per_wheel)
    k4, _ = derivatives(p, tyre, x + dt * k3, u, per_wheel)
    return x + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)


def steady_state_steer(p: BicycleParams, tyre, vx, r, ax=0.0):
    """Steer angle and lateral speed that hold yaw rate r at speed v_x in steady state (axle model).

    From the yaw and lateral balances F_yf = m v_x r b/ℓ, F_yr = m v_x r a/ℓ, then the Magic Formula
    is inverted on its rising branch for each axle slip angle.
    """
    l = p.a + p.b
    fzf, fzr = axle_loads(p, vx, ax)
    need_f = p.m * vx * r * p.b / l
    need_r = p.m * vx * r * p.a / l

    def invert(force, fz_wheel):
        sign = np.sign(force)
        target = np.abs(force) / 2
        lo, hi = np.zeros_like(target), np.full_like(target, 0.15)
        peak = tyre.fy(hi, fz_wheel)
        target = np.minimum(target, 0.995 * peak)
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            go = tyre.fy(mid, fz_wheel) < target
            lo, hi = np.where(go, mid, lo), np.where(go, hi, mid)
        return sign * 0.5 * (lo + hi)

    af = invert(need_f, fzf / 2)
    ar = invert(need_r, fzr / 2)
    vy = p.b * r - vx * np.tan(ar)
    delta = af + np.arctan((vy + p.a * r) / vx)
    return delta, vy
