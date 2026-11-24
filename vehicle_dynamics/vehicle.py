"""Quasi-steady-state vehicle model: aerodynamics, load transfer and the g-g-V envelope.

Model (all SI, x forward, y left, accelerations of the centre of mass):

* Aerodynamics: drag ``D = ½ ρ (C_D A) v²``, downforce ``L = ½ ρ (C_L A) v²`` split front/rear by
  the aero balance ``β_a``.
* Longitudinal load transfer ``ΔF_z,x = m a_x h / ℓ`` (front unloads under acceleration).
* Lateral load transfer per axle ``ΔF_z,y,i = χ_i m a_y h / t_i`` with roll-stiffness share χ_i,
  lumping geometric and elastic transfer (Milliken & Milliken, *Race Car Vehicle Dynamics*, ch. 18).
* Steady yaw balance: axle side forces ``F_y,f = m a_y b/ℓ``, ``F_y,r = m a_y a/ℓ``.
* Rear-wheel drive limited by wheel power ``F_x,r v ≤ P``; braking split by a fixed brake balance.
* Each axle obeys the friction ellipse ``(F_x/F_x,max)² + (F_y/F_y,max)² ≤ 1`` with capacities from
  the Magic Formula peak friction, so load sensitivity makes load transfer cost grip.

Neglected and declared: pitch from drag acting above the ground, ride-height sensitivity of the
aerodynamics, suspension kinematics, camber, tyre temperature, yaw inertia (steady state only).
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace

import numpy as np

from .tyre import MagicFormula, RACE_SLICK

G = 9.80665


def air_density(pressure_hpa: float, temperature_c: float, relative_humidity: float = 0.0) -> float:
    """Moist-air density (kg/m³), ideal-gas mixture with Tetens saturation pressure."""
    t = temperature_c + 273.15
    p_sat = 610.78 * np.exp(17.27 * temperature_c / (temperature_c + 237.3))
    p_v = relative_humidity / 100.0 * p_sat
    p_d = pressure_hpa * 100.0 - p_v
    return float(p_d / (287.058 * t) + p_v / (461.495 * t))


@dataclass(frozen=True)
class Car:
    mass: float = 902.0            # kg: 798 kg minimum with driver + ~104 kg fuel on lap 3 (estimate)
    wheelbase: float = 3.60        # m
    front_weight: float = 0.455    # static front weight fraction = b/ℓ
    h_cg: float = 0.28             # m
    track_f: float = 1.60          # m
    track_r: float = 1.55          # m
    roll_share_f: float = 0.55     # front share of lateral load transfer
    cla: float = 4.0               # m², downforce coefficient × area
    cda: float = 1.05              # m², drag coefficient × area
    aero_balance: float = 0.42     # front share of downforce
    power: float = 700e3           # W at the wheels
    brake_balance: float = 0.56    # front share of braking force
    crr: float = 0.012             # rolling-resistance coefficient
    rho: float = 1.21              # kg/m³
    tyre: MagicFormula = field(default=RACE_SLICK)

    @property
    def a(self) -> float:          # CG to front axle
        return self.wheelbase * (1.0 - self.front_weight)

    @property
    def b(self) -> float:          # CG to rear axle
        return self.wheelbase * self.front_weight

    def with_(self, **kw) -> "Car":
        if "lambda_muy" in kw or "lambda_mux" in kw:
            kw["tyre"] = self.tyre.scaled(kw.pop("lambda_muy", None), kw.pop("lambda_mux", None))
        return replace(self, **kw)

    # ---------------------------------------------------------------------------------------------
    def aero(self, v):
        q = 0.5 * self.rho * np.asarray(v, float) ** 2
        return q * self.cda, q * self.cla          # drag, downforce

    def wheel_loads(self, ax, ay, v):
        """Vertical loads (FL, FR, RL, RR) in N for a turn to the left when ay > 0."""
        ax, ay, v = np.broadcast_arrays(np.asarray(ax, float), np.asarray(ay, float), np.asarray(v, float))
        _, lift = self.aero(v)
        m, l, h = self.mass, self.wheelbase, self.h_cg
        fzf = m * G * self.b / l - m * ax * h / l + lift * self.aero_balance
        fzr = m * G * self.a / l + m * ax * h / l + lift * (1 - self.aero_balance)
        dyf = self.roll_share_f * m * ay * h / self.track_f
        dyr = (1 - self.roll_share_f) * m * ay * h / self.track_r
        return fzf / 2 - dyf, fzf / 2 + dyf, fzr / 2 - dyr, fzr / 2 + dyr

    def utilisation(self, ax, ay, v, grade=0.0):
        """Largest friction-ellipse utilisation of the two axles, and whether power binds.

        Returns (u, power_ok). The state is feasible when u ≤ 1 and power_ok.
        """
        ax, ay, v, grade = np.broadcast_arrays(*(np.asarray(z, float) for z in (ax, ay, v, grade)))
        fl, fr, rl, rr = self.wheel_loads(ax, ay, v)
        if np.any(np.minimum.reduce([fl, fr, rl, rr]) < 0):
            fl, fr, rl, rr = (np.maximum(w, 0.0) for w in (fl, fr, rl, rr))   # wheel lift: inner tyre carries nothing
        cxf = sum(self.tyre.capacity(w)[0] for w in (fl, fr))
        cyf = sum(self.tyre.capacity(w)[1] for w in (fl, fr))
        cxr = sum(self.tyre.capacity(w)[0] for w in (rl, rr))
        cyr = sum(self.tyre.capacity(w)[1] for w in (rl, rr))
        drag, _ = self.aero(v)
        m = self.mass
        resist = drag + self.crr * m * G + m * G * np.sin(grade)
        fx_total = m * ax + resist                       # force the tyres must deliver
        traction = fx_total >= 0
        fxf = np.where(traction, 0.0, self.brake_balance * fx_total)
        fxr = np.where(traction, fx_total, (1 - self.brake_balance) * fx_total)
        fyf = m * ay * self.b / self.wheelbase
        fyr = m * ay * self.a / self.wheelbase
        uf = (fxf / np.maximum(cxf, 1e-9)) ** 2 + (fyf / np.maximum(cyf, 1e-9)) ** 2
        ur = (fxr / np.maximum(cxr, 1e-9)) ** 2 + (fyr / np.maximum(cyr, 1e-9)) ** 2
        power_ok = np.where(traction, fxr * np.maximum(v, 1e-6) <= self.power, True)
        return np.sqrt(np.maximum(uf, ur)), power_ok

    def feasible(self, ax, ay, v, grade=0.0):
        u, p = self.utilisation(ax, ay, v, grade)
        return (u <= 1.0) & p

    # -- envelope -----------------------------------------------------------------------------------
    def coast_ax(self, v, grade=0.0):
        drag, _ = self.aero(v)
        return -(drag + self.crr * self.mass * G) / self.mass - G * np.sin(grade)

    def ay_max(self, v, iters: int = 48):
        """Maximum steady lateral acceleration at speed v holding speed constant (ax = 0)."""
        v = np.asarray(v, float)
        lo, hi = np.zeros_like(v), np.full_like(v, 8.0 * G)
        for _ in range(iters):
            mid = 0.5 * (lo + hi)
            ok = self.feasible(0.0, mid, v)
            lo, hi = np.where(ok, mid, lo), np.where(ok, hi, mid)
        return lo

    def ax_limits(self, v, ay, grade=0.0, iters: int = 48):
        """(ax_max, ax_min) at speed v and lateral acceleration ay. NaN where (v, ay) is infeasible."""
        v, ay, grade = np.broadcast_arrays(*(np.asarray(z, float) for z in (v, ay, grade)))
        coast = self.coast_ax(v, grade)
        ok0 = self.feasible(coast, ay, v, grade)
        # traction: from coast upwards
        lo, hi = coast.copy(), coast + 4.0 * G
        for _ in range(iters):
            mid = 0.5 * (lo + hi)
            ok = self.feasible(mid, ay, v, grade)
            lo, hi = np.where(ok, mid, lo), np.where(ok, hi, mid)
        ax_max = np.where(ok0, lo, np.nan)
        # braking: from coast downwards
        lo, hi = coast - 8.0 * G, coast.copy()
        for _ in range(iters):
            mid = 0.5 * (lo + hi)
            ok = self.feasible(mid, ay, v, grade)
            hi, lo = np.where(ok, mid, hi), np.where(ok, lo, mid)
        ax_min = np.where(ok0, hi, np.nan)
        return ax_max, ax_min

    def top_speed(self) -> float:
        """Speed where wheel power equals drag plus rolling resistance (m/s), by bisection."""
        lo, hi = 1.0, 200.0
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            need = (self.aero(mid)[0] + self.crr * self.mass * G) * mid
            lo, hi = (mid, hi) if need < self.power else (lo, mid)
        return lo

    def ggv(self, speeds, n_ay: int = 41):
        """g-g-V table: for each speed, ay from 0 to ay_max and the ax limits at each ay."""
        speeds = np.asarray(speeds, float)
        aymax = self.ay_max(speeds)
        frac = np.linspace(0.0, 1.0, n_ay)
        ay = aymax[:, None] * frac[None, :]
        vv = np.repeat(speeds[:, None], n_ay, axis=1)
        axp, axn = self.ax_limits(vv, ay)
        # at the very edge the bisection can leave a NaN; fall back to the coast value there
        coast = self.coast_ax(vv)
        axp = np.where(np.isnan(axp), coast, axp)
        axn = np.where(np.isnan(axn), coast, axn)
        return {"v": speeds, "ay_max": aymax, "frac": frac, "ay": ay, "ax_max": axp, "ax_min": axn}
