"""Hierarchical Bayesian race-pace model with Student-t errors, fitted by Gibbs sampling.

Model for the green-flag lap i of driver d(i):

    t_i = β₀ + β_H·H_i + β_S·a_i(1−H_i) + β_Hd·a_iH_i + γ·(n_i − 1) + u_d + v_d·a_i + ε_i

    H_i   1 if the lap is on the hard compound
    a_i   tyre age in laps;  n_i race lap
    u_d   driver intercept  ~ N(0, τ_u²),   v_d driver degradation slope ~ N(0, τ_v²)
    ε_i   Student-t(ν, 0, σ²), written as ε_i | λ_i ~ N(0, σ²/λ_i), λ_i ~ Gamma(ν/2, ν/2)

A Gaussian variant (λ_i ≡ 1) is fitted with ``nu_grid=[1e6]``; the two are compared on a temporal
hold-out with the CRPS, and the one that forecasts better drives the strategy.

The scale mixture makes every full conditional standard (Gelman et al., *Bayesian Data Analysis*,
3rd ed., ch. 17): normal for the coefficients, inverse-gamma for σ², gamma for λ_i, discrete for ν
on a grid. τ_u and τ_v get half-Cauchy priors through the inverse-gamma auxiliary representation
of Wand et al. (2011). Laps slowed by traffic get small λ_i and therefore little weight, which is
why the t likelihood is used: the OLS residuals of this race have kurtosis ≈ 15 and skew ≈ 2.

γ is the total race-lap trend: fuel burn-off plus track evolution. The data identify only the sum.
The split uses physics: γ_fuel = (∂T/∂m)·ṁ, with ∂T/∂m from the calibrated lap simulation of
phase 1 and ṁ the fuel burn per lap, and γ_track = γ − γ_fuel (see :func:`decompose_trend`).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import lgamma

import numpy as np

from .data import LapTable

FIXED = ("intercept", "hard", "age_soft", "age_hard", "race_lap")
NU_GRID = np.array([2, 2.5, 3, 3.5, 4, 5, 6, 8, 10, 15, 20, 30, 50], float)


@dataclass
class Design:
    X: np.ndarray               # fixed-effects design (n × 5)
    drv_idx: np.ndarray         # driver index per lap
    age: np.ndarray
    drivers: list
    y: np.ndarray
    centre: float               # centring of race lap so the intercept is pace at the reference lap
    ref_lap: int = 30

    @classmethod
    def of(cls, t: LapTable, drivers=None, ref_lap: int = 30) -> "Design":
        drivers = sorted(set(t.driver)) if drivers is None else list(drivers)
        h = (t.compound == "HARD").astype(float)
        a = t.age.astype(float)
        lapc = t.lap.astype(float) - ref_lap
        X = np.column_stack([np.ones(len(t)), h, a * (1 - h), a * h, lapc])
        idx = np.array([drivers.index(d) for d in t.driver])
        return cls(X, idx, a, drivers, t.time.astype(float), float(ref_lap), ref_lap)


@dataclass
class Posterior:
    beta: np.ndarray            # (chains, draws, 5)
    u: np.ndarray               # (chains, draws, D)
    v: np.ndarray               # (chains, draws, D)
    sigma: np.ndarray           # (chains, draws)
    nu: np.ndarray
    tau_u: np.ndarray
    tau_v: np.ndarray
    drivers: list
    lam_mean: np.ndarray        # posterior mean weight per lap
    ref_lap: int
    meta: dict = field(default_factory=dict)

    def flat(self, name):
        a = getattr(self, name)
        return a.reshape(-1, *a.shape[2:])

    def predictive(self, X, drv_idx, age, rng, n_draws: int | None = None):
        """Posterior-predictive draws (draws × laps) of lap times for new rows."""
        b, u, v = self.flat("beta"), self.flat("u"), self.flat("v")
        s, nu = self.flat("sigma"), self.flat("nu")
        k = len(b) if n_draws is None else min(n_draws, len(b))
        pick = rng.choice(len(b), size=k, replace=False)
        mu = b[pick] @ X.T + u[pick][:, drv_idx] + v[pick][:, drv_idx] * age[None, :]
        nu_d = nu[pick][:, None]
        t = np.where(nu_d >= 1e5, rng.standard_normal(mu.shape), rng.standard_t(np.minimum(nu_d, 1e5), size=mu.shape))
        return mu + s[pick][:, None] * t, mu


def _rinvgamma(rng, a, b):
    return b / rng.gamma(a, 1.0, size=np.shape(a) if np.ndim(a) else None)


def gibbs(design: Design, chains: int = 4, iters: int = 3000, burn: int = 1000, seed: int = 2024,
          prior_mean=None, prior_sd=None, A_u: float = 1.0, A_v: float = 0.05, nu_grid=None) -> Posterior:
    """Gibbs sampler. ``nu_grid`` = None samples ν on :data:`NU_GRID` (Student-t); pass [1e6] for
    Gaussian errors (λ_i ≡ 1 in practice)."""
    grid = NU_GRID if nu_grid is None else np.asarray(nu_grid, float)
    gaussian = grid.size == 1 and grid[0] >= 1e5
    X, y, idx, age = design.X, design.y, design.drv_idx, design.age
    n, p = X.shape
    D = len(design.drivers)
    # full design of fixed + random effects
    Zu = np.zeros((n, D)); Zu[np.arange(n), idx] = 1.0
    Zv = Zu * age[:, None]
    M = np.hstack([X, Zu, Zv])
    m0 = np.array([float(np.median(y)), 0.0, 0.0, 0.0, 0.0]) if prior_mean is None else np.asarray(prior_mean, float)
    s0 = np.array([5.0, 1.0, 0.5, 0.5, 0.2]) if prior_sd is None else np.asarray(prior_sd, float)
    keep = iters - burn
    out = {k: np.empty((chains, keep) + shape) for k, shape in
           [("beta", (p,)), ("u", (D,)), ("v", (D,)), ("sigma", ()), ("nu", ()), ("tau_u", ()), ("tau_v", ())]}
    lam_sum = np.zeros(n)
    for c in range(chains):
        rng = np.random.default_rng(seed + 97 * c)
        sigma2 = float(np.var(y)) * rng.uniform(0.5, 1.5)
        tu2, tv2 = 0.3 ** 2, 0.02 ** 2
        au, av = 1.0, 1.0
        nu = float(grid[0]) if gaussian else 4.0
        lam = np.ones(n)
        for it in range(iters):
            # 1. coefficients | rest  (normal; prior precision block-diagonal)
            prec_prior = np.concatenate([1 / s0 ** 2, np.full(D, 1 / tu2), np.full(D, 1 / tv2)])
            mean_prior = np.concatenate([m0, np.zeros(2 * D)])
            Mw = M * (lam / sigma2)[:, None]
            Q = M.T @ Mw + np.diag(prec_prior)
            bvec = Mw.T @ y + prec_prior * mean_prior
            L = np.linalg.cholesky(Q)
            mean = np.linalg.solve(L.T, np.linalg.solve(L, bvec))
            theta = mean + np.linalg.solve(L.T, rng.standard_normal(len(mean)))
            beta, u, v = theta[:p], theta[p:p + D], theta[p + D:]
            r = y - M @ theta
            # 2. σ² | rest  (Jeffreys prior)
            sigma2 = float(_rinvgamma(rng, n / 2.0, 0.5 * np.sum(lam * r * r)))
            # 3. λ_i | rest  and  4. ν | λ on a grid (flat prior over the grid)
            if gaussian:
                nu = float(grid[0])
            else:
                lam = rng.gamma((nu + 1) / 2.0, 1.0, size=n) / ((nu + r * r / sigma2) / 2.0)
                slog, ssum = float(np.sum(np.log(lam))), float(np.sum(lam))
                ll = np.array([n * (0.5 * g * np.log(g / 2.0) - lgamma(g / 2.0)) + (g / 2.0 - 1) * slog - g / 2.0 * ssum
                               for g in grid])
                w = np.exp(ll - ll.max()); w /= w.sum()
                nu = float(rng.choice(grid, p=w))
            # 5. variance components (half-Cauchy via auxiliary inverse-gamma)
            tu2 = float(_rinvgamma(rng, (D + 1) / 2.0, 1.0 / au + 0.5 * np.sum(u * u)))
            au = float(_rinvgamma(rng, 1.0, 1.0 / tu2 + 1.0 / A_u ** 2))
            tv2 = float(_rinvgamma(rng, (D + 1) / 2.0, 1.0 / av + 0.5 * np.sum(v * v)))
            av = float(_rinvgamma(rng, 1.0, 1.0 / tv2 + 1.0 / A_v ** 2))
            if it >= burn:
                k = it - burn
                out["beta"][c, k], out["u"][c, k], out["v"][c, k] = beta, u, v
                out["sigma"][c, k], out["nu"][c, k] = np.sqrt(sigma2), nu
                out["tau_u"][c, k], out["tau_v"][c, k] = np.sqrt(tu2), np.sqrt(tv2)
                lam_sum += lam
    return Posterior(out["beta"], out["u"], out["v"], out["sigma"], out["nu"], out["tau_u"], out["tau_v"],
                     list(design.drivers), lam_sum / (chains * keep), design.ref_lap,
                     {"chains": chains, "iters": iters, "burn": burn, "seed": seed, "n": n,
                      "prior_mean": m0.tolist(), "prior_sd": s0.tolist(), "A_u": A_u, "A_v": A_v,
                      "likelihood": "normal" if gaussian else "student-t"})


# ------------------------------------------------------------------------------------------------
# MCMC diagnostics (Vehtari et al., 2021: rank-normalised split R-hat is the stricter version;
# here the classic split R-hat and an autocorrelation-based ESS, adequate for these well-mixed chains)
# ------------------------------------------------------------------------------------------------
def split_rhat(x: np.ndarray) -> float:
    c, n = x.shape
    h = n // 2
    s = np.concatenate([x[:, :h], x[:, h:2 * h]], axis=0)
    m, n2 = s.shape
    means, vars_ = s.mean(axis=1), s.var(axis=1, ddof=1)
    B = n2 * means.var(ddof=1)
    W = vars_.mean()
    var_hat = (n2 - 1) / n2 * W + B / n2
    return float(np.sqrt(var_hat / W)) if W > 0 else float("nan")


def ess(x: np.ndarray) -> float:
    """Effective sample size from the chain-averaged autocorrelation (Geyer initial positive sequence)."""
    c, n = x.shape
    xc = x - x.mean(axis=1, keepdims=True)
    f = np.fft.rfft(xc, n=2 * n, axis=1)
    acov = np.fft.irfft(f * np.conj(f), axis=1)[:, :n] / n
    rho = acov.mean(axis=0) / acov.mean(axis=0)[0]
    s = 0.0
    for t in range(1, n - 1, 2):
        pair = rho[t] + rho[t + 1]
        if pair < 0:
            break
        s += pair
    tau = max(1.0 + 2 * s, 1.0)
    return float(c * n / tau)


def summary(post: Posterior) -> dict:
    out = {}
    for j, name in enumerate(FIXED):
        x = post.beta[:, :, j]
        out[name] = _stat(x)
    for name in ("sigma", "nu", "tau_u", "tau_v"):
        out[name] = _stat(getattr(post, name))
    return out


def _stat(x: np.ndarray) -> dict:
    flat = x.reshape(-1)
    if np.ptp(flat) == 0:                       # fixed quantity (e.g. ν in the Gaussian model)
        v = float(flat[0])
        return {"mean": v, "sd": 0.0, "q025": v, "q05": v, "median": v, "q95": v, "q975": v, "rhat": 1.0, "ess": float(flat.size)}
    q = np.quantile(flat, [0.025, 0.05, 0.5, 0.95, 0.975])
    return {"mean": float(flat.mean()), "sd": float(flat.std(ddof=1)), "q025": float(q[0]), "q05": float(q[1]),
            "median": float(q[2]), "q95": float(q[3]), "q975": float(q[4]), "rhat": split_rhat(x), "ess": ess(x)}


# ------------------------------------------------------------------------------------------------
# Proper scoring of probabilistic forecasts
# ------------------------------------------------------------------------------------------------
def crps_samples(samples: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Sample CRPS per observation: E|X − y| − ½ E|X − X'| (Gneiting & Raftery, 2007)."""
    s = np.sort(samples, axis=0)
    m = s.shape[0]
    term1 = np.mean(np.abs(s - y[None, :]), axis=0)
    # E|X − X'| for sorted samples = 2/m² Σ (2i − m − 1) x_(i)
    i = np.arange(1, m + 1)[:, None]
    term2 = 2.0 / (m * m) * np.sum((2 * i - m - 1) * s, axis=0)
    return term1 - 0.5 * term2


def decompose_trend(gamma_draws: np.ndarray, ds_dkg: float, ds_dkg_sd: float, burn_kg_lap: float,
                    burn_sd: float, rng) -> dict:
    """Split the race-lap trend γ into fuel burn-off (physics prior) and track evolution (remainder)."""
    k = len(gamma_draws)
    fuel = rng.normal(ds_dkg, ds_dkg_sd, k) * rng.normal(burn_kg_lap, burn_sd, k)    # s/lap gained per lap
    track = gamma_draws + fuel                                                         # γ = −fuel + track
    q = lambda a: [float(x) for x in np.quantile(a, [0.05, 0.5, 0.95])]
    return {"fuel_s_per_lap": {"mean": float(fuel.mean()), "q": q(fuel)},
            "track_s_per_lap": {"mean": float(track.mean()), "q": q(track)},
            "total_s_per_lap": {"mean": float(gamma_draws.mean()), "q": q(gamma_draws)}}
