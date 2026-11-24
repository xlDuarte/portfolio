"""Identify car parameters from a measured speed trace: maximum a posteriori (MAP) by nonlinear
least squares with Gaussian priors.

Residual vector (stacked):

    r(θ) = [ (v_sim(s_i; θ) − v_meas,i) / σ_v  ,  (T_sim(θ) − T_meas) / σ_T  ,  (θ_j − μ_j) / τ_j ]

i over the telemetry samples of one lap, j over the parameters θ = (λ_μy, λ_μx, C_L A, C_D A, P).
The official lap time T_meas enters as one more observation (σ_T = 0.25 s, mostly model error):
the speed samples constrain the shape of the profile, the lap time its integral.
Minimising ½‖r‖² is the MAP estimate under v_meas ~ N(v_sim, σ_v²) and θ_j ~ N(μ_j, τ_j²).
The priors encode published orders of magnitude for a 2024 Formula 1 car (wheel power after ERS
deployment limits, drag and downforce areas); they are wide except for power, which a speed trace
cannot separate from drag (top speed fixes only the ratio P / C_D A).

Uncertainty: the Laplace approximation Cov(θ̂) ≈ (JᵀJ)⁻¹ of the stacked residual. Speed residuals
along a lap are autocorrelated, so the data block of JᵀJ is deflated by the AR(1) factor
(1 − ρ)/(1 + ρ) (effective sample size n (1 − ρ)/(1 + ρ)), ρ the lag-1 autocorrelation of the
residuals ordered by distance. σ_v is re-estimated from the residuals and the fit repeated once.

What the fit means: a race lap is not a qualifying lap. λ_μy and λ_μx are the friction *used* on
that lap (tyre management, fuel load, lift-and-coast, traffic), not the tyre's capability, and
the aerodynamic coefficients absorb what the model leaves out (dirty air, ride height, DRS,
energy deployment).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import least_squares

from .openf1 import LapTrace
from .qss import Envelope, simulate
from .track import Track
from .vehicle import Car

PARAMS = ("lambda_muy", "lambda_mux", "cla", "cda", "power")
LABELS = {"lambda_muy": "λ_μy", "lambda_mux": "λ_μx", "cla": "C_L·A", "cda": "C_D·A", "power": "P"}
UNITS = {"lambda_muy": "", "lambda_mux": "", "cla": "m²", "cda": "m²", "power": "W"}
BOUNDS = {"lambda_muy": (0.4, 1.4), "lambda_mux": (0.3, 1.4), "cla": (0.5, 9.0), "cda": (0.4, 2.5), "power": (300e3, 900e3)}
# Prior mean and standard deviation (hypotheses, see module docstring)
PRIOR = {"lambda_muy": (1.0, 0.3), "lambda_mux": (1.0, 0.3), "cla": (4.0, 1.5), "cda": (1.2, 0.4), "power": (620e3, 50e3)}
SCALE = np.array([0.05, 0.05, 0.5, 0.1, 50e3])


def car_from(theta, base: Car) -> Car:
    muy, mux, cla, cda, power = theta
    return base.with_(lambda_muy=muy, lambda_mux=mux, cla=cla, cda=cda, power=power)


def simulated_speed(theta, base: Car, track: Track, s_meas):
    car = car_from(theta, base)
    res = simulate(car, track, Envelope.of(car))
    return np.interp(np.asarray(s_meas) % track.length, res.s, res.v, period=track.length), res


@dataclass
class Fit:
    theta: np.ndarray
    se: np.ndarray
    corr: np.ndarray
    rmse: float                 # m/s
    bias: float                 # m/s, mean(v_sim − v_meas)
    r2: float
    rho: float                  # lag-1 autocorrelation of residuals
    n: int
    n_eff: float
    sigma_v: float
    lap_time_sim: float
    lap_time_meas: float
    nfev: int

    def to_dict(self) -> dict:
        p = {k: {"label": LABELS[k], "value": float(v), "se": float(e), "unit": UNITS[k],
                 "prior_mean": PRIOR[k][0], "prior_sd": PRIOR[k][1]} for k, v, e in zip(PARAMS, self.theta, self.se)}
        return {"params": p, "corr": np.round(self.corr, 3).tolist(), "rmse_kmh": round(self.rmse * 3.6, 2),
                "bias_kmh": round(self.bias * 3.6, 2), "r2": round(self.r2, 4), "residual_lag1": round(self.rho, 3),
                "n": self.n, "n_eff": round(self.n_eff, 1), "sigma_v_kmh": round(self.sigma_v * 3.6, 2),
                "lap_time_sim_s": round(self.lap_time_sim, 3), "lap_time_meas_s": round(self.lap_time_meas, 3),
                "evaluations": self.nfev}


def _lag1(r_sorted):
    r0 = r_sorted - r_sorted.mean()
    return float(np.clip(np.sum(r0[1:] * r0[:-1]) / max(np.sum(r0 * r0), 1e-12), 0.0, 0.95))


def fit_lap(lap: LapTrace, track: Track, base: Car, theta0=None, sigma_v: float = 4.0, sigma_t: float = 0.25) -> Fit:
    theta0 = np.array([PRIOR[k][0] for k in PARAMS] if theta0 is None else theta0, float)
    lo = np.array([BOUNDS[k][0] for k in PARAMS])
    hi = np.array([BOUNDS[k][1] for k in PARAMS])
    mu = np.array([PRIOR[k][0] for k in PARAMS])
    tau = np.array([PRIOR[k][1] for k in PARAMS])
    order = np.argsort(lap.s)
    weight = 1.0
    nfev = 0
    for _ in range(2):                         # second pass with σ_v and ρ re-estimated
        def resid(th, sv=sigma_v, w=weight):
            v, sim = simulated_speed(th, base, track, lap.s)
            dt = [(sim.lap_time - lap.lap_time) / sigma_t] if lap.complete else []
            return np.concatenate([np.sqrt(w) * (v - lap.v) / sv, dt, (th - mu) / tau])
        sol = least_squares(resid, theta0, bounds=(lo, hi), x_scale=SCALE, diff_step=1e-3, xtol=1e-7, ftol=1e-9)
        nfev += sol.nfev
        theta0 = sol.x
        v, res = simulated_speed(sol.x, base, track, lap.s)
        r = v - lap.v
        rho = _lag1(r[order])
        sigma_v = float(np.sqrt(np.mean(r ** 2)))
        weight = (1 - rho) / (1 + rho)
    # Laplace covariance at the final weights
    jac = sol.jac
    cov = np.linalg.inv(jac.T @ jac)
    se = np.sqrt(np.diag(cov))
    corr = cov / np.outer(se, se)
    n = len(r)
    ss_tot = float(np.sum((lap.v - lap.v.mean()) ** 2))
    return Fit(sol.x, se, corr, float(np.sqrt(np.mean(r ** 2))), float(r.mean()), 1 - float(r @ r) / ss_tot, rho, n,
               n * (1 - rho) / (1 + rho), sigma_v, res.lap_time, lap.lap_time, nfev)


def predict_lap(theta, base: Car, track: Track, lap: LapTrace) -> dict:
    """Out-of-sample check: simulate with fixed θ and compare to another lap."""
    v, res = simulated_speed(theta, base, track, lap.s)
    r = v - lap.v
    return {"driver": lap.acronym, "lap": lap.lap, "lap_time_sim_s": round(res.lap_time, 3),
            "lap_time_meas_s": round(lap.lap_time, 3), "rmse_kmh": round(float(np.sqrt(np.mean(r ** 2))) * 3.6, 2),
            "bias_kmh": round(float(r.mean()) * 3.6, 2)}


def sensitivity(car: Car, track: Track, rel: float = 0.01) -> dict:
    """Central-difference lap-time sensitivity: seconds per +1 % of each parameter (and per +10 kg)."""
    base = simulate(car, track).lap_time
    specs = {"massa": "mass", "potência": "power", "C_L·A": "cla", "C_D·A": "cda", "aderência lateral λ_μy": "lambda_muy",
             "aderência longitudinal λ_μx": "lambda_mux", "altura do CG": "h_cg", "balanço aerodinâmico": "aero_balance"}
    out = {}
    for label, name in specs.items():
        cur = getattr(car.tyre, name) if name.startswith("lambda") else getattr(car, name)
        up = simulate(car.with_(**{name: cur * (1 + rel)}), track).lap_time
        dn = simulate(car.with_(**{name: cur * (1 - rel)}), track).lap_time
        out[label] = {"param": name, "s_per_pct": (up - dn) / (2 * rel * 100)}
    out["massa"]["s_per_10kg"] = out["massa"]["s_per_pct"] * 100 * 10 / car.mass
    return {"base_lap_s": base, "items": out}


def monte_carlo(fit: Fit, base: Car, track: Track, n: int = 200, seed: int = 110) -> dict:
    """Propagate the Laplace posterior of θ to the lap time (draws clipped to the bounds)."""
    rng = np.random.default_rng(seed)
    cov = np.outer(fit.se, fit.se) * fit.corr
    lo = np.array([BOUNDS[k][0] for k in PARAMS])
    hi = np.array([BOUNDS[k][1] for k in PARAMS])
    draws = np.clip(rng.multivariate_normal(fit.theta, cov, size=n), lo, hi)
    times = np.array([simulate(car_from(th, base), track).lap_time for th in draws])
    q = np.quantile(times, [0.025, 0.5, 0.975])
    return {"n": n, "mean_s": float(times.mean()), "sd_s": float(times.std(ddof=1)), "q025_s": float(q[0]),
            "q50_s": float(q[1]), "q975_s": float(q[2]), "seed": seed}
