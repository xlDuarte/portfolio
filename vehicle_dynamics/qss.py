"""Quasi-steady-state (QSS) lap simulation on a closed track.

Algorithm (Brayshaw & Harrison, 2005; Siegler, Deakin & Crolla, 2000):

1. Cornering limit: at every point the largest speed whose lateral demand a_y = v²|κ| is
   feasible with a_x = 0, found by bisection on v.
2. Forward pass from the slowest corner: d(v²)/ds = 2 (a_x,max(v, a_y) − g sin θ), integrated with
   Heun's method (Euler predictor, trapezoidal corrector; second order in Δs), capped by (1).
3. Backward pass: the same with a_x,min, integrated from the end, capped by (1).
4. Speed profile = min of the two passes; both are wrapped twice so the lap closes on itself.

The g-g-V limits are tabulated once per car on a grid of speed and normalised lateral acceleration
(a_y / a_y,max(v)) and interpolated bilinearly inside the passes; the grade enters as −g sin θ.
Lap time is the trapezoidal integral of Δs / v.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .track import Track
from .vehicle import Car, G

REGIMES = ("curva", "tração · potência", "tração · aderência", "frenagem")


@dataclass
class Envelope:
    v: np.ndarray
    ay_max: np.ndarray
    frac: np.ndarray
    ax_max: np.ndarray
    ax_min: np.ndarray
    power_limited: np.ndarray   # (nv, nfrac) bool: traction limit set by power rather than grip

    @classmethod
    def of(cls, car: Car, v_max: float | None = None, dv: float = 1.0, n_frac: int = 33) -> "Envelope":
        top = car.top_speed() if v_max is None else v_max
        v = np.arange(2.0, top + 2 * dv, dv)
        t = car.ggv(v, n_frac)
        # is power the binding constraint at the traction limit?
        drag, _ = car.aero(v[:, None])
        fx = car.mass * t["ax_max"] + drag + car.crr * car.mass * G
        power_limited = fx * v[:, None] >= 0.995 * car.power
        return cls(v, t["ay_max"], t["frac"], t["ax_max"], t["ax_min"], power_limited)

    def lookup(self, v: float, ay: float):
        """Bilinear interpolation of (ax_max, ax_min, ay_max, power_limited) at speed v, |ay|."""
        vv = self.v
        i = int(np.clip(np.searchsorted(vv, v) - 1, 0, len(vv) - 2))
        tv = float(np.clip((v - vv[i]) / (vv[i + 1] - vv[i]), 0.0, 1.0))
        aym = self.ay_max[i] * (1 - tv) + self.ay_max[i + 1] * tv
        f = min(abs(ay) / max(aym, 1e-9), 1.0)
        nf = len(self.frac) - 1
        j = min(int(f * nf), nf - 1)
        tf = f * nf - j

        def bil(tab):
            return ((tab[i, j] * (1 - tf) + tab[i, j + 1] * tf) * (1 - tv)
                    + (tab[i + 1, j] * (1 - tf) + tab[i + 1, j + 1] * tf) * tv)

        return bil(self.ax_max), bil(self.ax_min), aym, bool(self.power_limited[i, j] if tv < 0.5 else self.power_limited[i + 1, j])


@dataclass
class LapResult:
    s: np.ndarray
    v: np.ndarray
    v_corner: np.ndarray
    ax: np.ndarray
    ay: np.ndarray
    regime: np.ndarray          # index into REGIMES
    time: np.ndarray            # cumulative time at each point (s)
    lap_time: float

    def to_dict(self, step: int = 1) -> dict:
        sl = slice(None, None, step)
        r = lambda a, d: np.round(np.asarray(a)[sl], d).tolist()
        return {"lap_time_s": round(self.lap_time, 3), "s": r(self.s, 1), "v_kmh": r(self.v * 3.6, 2),
                "ax_g": r(self.ax / G, 3), "ay_g": r(self.ay / G, 3), "regime": np.asarray(self.regime)[sl].tolist(),
                "t": r(self.time, 3)}


def corner_speed(car: Car, kappa: np.ndarray, env: Envelope) -> np.ndarray:
    """Largest v with v²|κ| ≤ a_y,max(v), solved on the tabulated envelope (vectorised)."""
    k = np.abs(kappa)
    # residual r(v) = ay_max(v) - v² k is decreasing in v at the root; scan the table then refine
    v = env.v
    r = env.ay_max[None, :] - (v[None, :] ** 2) * k[:, None]
    ok = r >= 0
    last = np.where(ok.any(axis=1), ok.shape[1] - 1 - np.argmax(ok[:, ::-1], axis=1), 0)
    out = np.empty_like(k)
    for n, i in enumerate(last):
        if i >= len(v) - 1:
            out[n] = v[-1]
            continue
        r0, r1 = r[n, i], r[n, i + 1]
        out[n] = v[i] + (v[i + 1] - v[i]) * r0 / (r0 - r1) if r0 != r1 else v[i]
    return np.minimum(out, v[-1])


def simulate(car: Car, track: Track, env: Envelope | None = None) -> LapResult:
    env = Envelope.of(car) if env is None else env
    n = len(track.s)
    ds = track.ds
    kappa, grade = track.kappa, track.grade
    vc = corner_speed(car, kappa, env)
    g_sin = G * np.sin(grade)

    start = int(np.argmin(vc))
    order = np.r_[np.arange(start, n), np.arange(0, start)]

    fwd = vc.copy()
    pl = np.zeros(n, bool)
    v = vc[start]
    for _ in range(2):                              # two wraps so the start point is consistent
        for idx in range(n):
            i = order[idx]
            j = order[(idx + 1) % n]
            axp, _, _, plim = env.lookup(v, v * v * kappa[i])
            vp = np.sqrt(max(v * v + 2.0 * (axp - g_sin[i]) * ds[i], 0.0))          # Euler predictor
            axq, _, _, _ = env.lookup(vp, vp * vp * kappa[j])
            vn2 = v * v + (axp - g_sin[i] + axq - g_sin[j]) * ds[i]                # Heun corrector
            vn = min(np.sqrt(max(vn2, 0.0)), vc[j])
            if vn < fwd[j]:
                fwd[j] = vn
                pl[j] = plim
            v = vn

    bwd = vc.copy()
    v = vc[start]
    for _ in range(2):
        for idx in range(n, 0, -1):
            j = order[idx % n]
            i = order[idx - 1]
            _, axn, _, _ = env.lookup(v, v * v * kappa[j])
            vq = np.sqrt(max(v * v - 2.0 * (axn - g_sin[j]) * ds[i], 0.0))          # Euler predictor
            _, axm, _, _ = env.lookup(vq, vq * vq * kappa[i])
            vp2 = v * v - (axn - g_sin[j] + axm - g_sin[i]) * ds[i]                # Heun corrector
            vp = min(np.sqrt(max(vp2, 0.0)), vc[i])
            bwd[i] = min(bwd[i], vp)
            v = vp

    speed = np.minimum(fwd, bwd)
    nxt = np.roll(speed, -1)
    dt = 2.0 * ds / np.maximum(speed + nxt, 1e-6)
    t = np.concatenate([[0.0], np.cumsum(dt)[:-1]])
    ax = (nxt ** 2 - speed ** 2) / (2.0 * ds)
    ay = speed ** 2 * kappa
    regime = np.where(speed >= vc - 1e-3, 0, np.where(bwd < fwd - 1e-6, 3, np.where(pl, 1, 2)))
    return LapResult(track.s, speed, vc, ax, ay, regime, t, float(dt.sum()))
