"""Remaining useful life of turbofan engines (NASA C-MAPSS) with a Bayesian degradation model (#097).

Data: Saxena, Goebel, Simon and Eklund, "Damage propagation modeling for aircraft engine run-to-
failure simulation", PHM 2008; NASA Prognostics Center of Excellence data repository (public
domain). FD001 (one operating condition, HPC degradation) and FD003 (one condition, HPC and fan
degradation), committed gzip-compressed under data/cmapss with their SHA-256 in the manifest.

Model, in three steps:

1. **Health indicator.** A linear combination S = w·z of the standardised informative sensors,
   fitted on the training engines only so that S ≈ 0 in the first 10 % of life and S ≈ 1 in the
   last 10 % (Wang, Yu, Siegel and Lee, PHM 2008).
2. **Random-coefficient degradation path.** For engine i,
       S_i(t) = a_i + b_i · g(t) + ε,   g(t) = (e^{γt} − 1)/γ,   ε ~ N(0, σ²),
   with (a_i, log b_i) ~ N(μ₀, Σ₀) across the fleet: the rate b is log-normal, so every engine
   degrades and the spread of lifetimes (128 to 362 cycles in FD001) maps to a spread of rates.
   γ (common acceleration), μ₀, Σ₀ and σ come from the training engines (empirical Bayes). The
   posterior of a test engine given its cycles so far is computed by importance sampling with a
   Laplace proposal (in the spirit of Gebraeel, Lawley, Li and Ryan, IIE Trans.
   37, 2005, whose conjugate version needs a Gaussian rate).
3. **Failure threshold and RUL.** Failure happens when S crosses D, D ~ N(m_D, s_D²) estimated from
   the fitted paths at the training failure times. Sampling (a, b, D) from the posterior gives
   the predictive distribution of the crossing time, hence of the RUL, and its median is the
   point forecast.

γ is chosen by cross-validation on the training engines, truncated at random cycles to imitate
the test set, scoring the CRPS of the RUL predictive distribution. The test RUL values are used
only for the final evaluation.
"""
from __future__ import annotations

import gzip
from dataclasses import dataclass
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parents[1] / "data" / "cmapss"
SENSORS = (2, 3, 4, 7, 8, 9, 11, 12, 13, 14, 15, 17, 20, 21)    # vary with degradation in FD001/FD003


def _read(name: str) -> np.ndarray:
    with gzip.open(DATA / f"{name}.txt.gz", "rt") as f:
        return np.loadtxt(f)


@dataclass
class Fleet:
    unit: np.ndarray
    cycle: np.ndarray
    X: np.ndarray                     # informative sensors

    @property
    def units(self):
        return np.unique(self.unit)

    def of(self, k):
        m = self.unit == k
        return self.cycle[m], self.X[m]


def load(fd: str = "FD001"):
    """(train Fleet, test Fleet, true test RUL)."""
    cols = [4 + s for s in SENSORS]
    tr, te, rul = _read(f"train_{fd}"), _read(f"test_{fd}"), _read(f"RUL_{fd}")
    f = lambda a: Fleet(a[:, 0].astype(int), a[:, 1], a[:, cols])
    return f(tr), f(te), rul


# ------------------------------------------------------------------------------------------------
# 1. health indicator
# ------------------------------------------------------------------------------------------------
@dataclass
class HealthIndicator:
    mu: np.ndarray
    sd: np.ndarray
    w: np.ndarray

    @classmethod
    def fit(cls, fleet: Fleet, edge: float = 0.1):
        life = {k: fleet.cycle[fleet.unit == k].max() for k in fleet.units}
        frac = fleet.cycle / np.array([life[k] for k in fleet.unit])
        mu, sd = fleet.X.mean(0), fleet.X.std(0)
        sd[sd == 0] = 1.0
        Z = (fleet.X - mu) / sd
        sel = (frac <= edge) | (frac >= 1 - edge)
        A = np.column_stack([np.ones(sel.sum()), Z[sel]])
        y = (frac[sel] >= 1 - edge).astype(float)
        w = np.linalg.lstsq(A, y, rcond=None)[0]
        return cls(mu, sd, w)

    def __call__(self, X):
        return np.column_stack([np.ones(len(X)), (X - self.mu) / self.sd]) @ self.w


# ------------------------------------------------------------------------------------------------
# 2–3. degradation model
# ------------------------------------------------------------------------------------------------
def basis(t, gamma):
    t = np.asarray(t, float)
    g = t if abs(gamma) < 1e-9 else np.expm1(gamma * t) / gamma
    return np.column_stack([np.ones_like(t), g])


GAMMA_GRID = np.linspace(0.002, 0.08, 157)


def fit_path(t, s, gamma=None):
    """Least squares of s = a + b·g_γ(t): (a, b) in closed form, γ by grid search when not given."""
    best = None
    for g in ([gamma] if gamma is not None else GAMMA_GRID):
        B = basis(t, g)
        c, *_ = np.linalg.lstsq(B, s, rcond=None)
        r = s - B @ c
        sse = r @ r
        if best is None or sse < best[0]:
            best = (sse, c, g, r)
    return best[1], best[2], best[3]


@dataclass
class DegradationModel:
    """Random-coefficient path. ``random_gamma=False``: θ = (a, log b), γ shared by the fleet.
    ``random_gamma=True``: θ = (a, log b, log γ), each engine with its own acceleration."""
    gamma: float
    random_gamma: bool
    mu0: np.ndarray
    S0: np.ndarray
    sigma: float
    rho: float                        # lag-1 autocorrelation of the residuals
    mD: float
    sD: float
    hi: HealthIndicator

    @classmethod
    def fit(cls, fleet: Fleet, gamma: float | None = None, hi: HealthIndicator | None = None):
        hi = hi or HealthIndicator.fit(fleet)
        random_gamma = gamma is None
        est, res, ends, rho = [], [], [], []
        for k in fleet.units:
            t, X = fleet.of(k)
            s = hi(X)
            c, g, r = fit_path(t, s, gamma)
            res.append(r)
            rho.append(np.corrcoef(r[:-1], r[1:])[0, 1])
            ends.append((basis([t.max()], g) @ c)[0])
            th = [c[0], np.log(max(c[1], 1e-12))]
            est.append(th + [np.log(g)] if random_gamma else th)
        est = np.array(est)
        sigma = float(np.sqrt(np.mean(np.concatenate(res) ** 2)))
        g0 = float(np.exp(est[:, 2].mean())) if random_gamma else float(gamma)
        return cls(g0, random_gamma, est.mean(0), np.cov(est.T), sigma, float(np.mean(rho)),
                   float(np.mean(ends)), float(np.std(ends, ddof=1)), hi)

    @property
    def sigma_eff(self) -> float:
        """Noise inflated for AR(1) residuals: the information of n correlated points equals that
        of n(1−ρ)/(1+ρ) independent ones."""
        return self.sigma * np.sqrt((1 + self.rho) / (1 - self.rho))

    def _unpack(self, th):
        a, b = th[..., 0], np.exp(th[..., 1])
        g = np.exp(th[..., 2]) if self.random_gamma else np.full_like(a, self.gamma)
        return a, b, g

    def posterior_draws(self, t, X, n: int = 4000, rng=None, n_prop: int = 8000):
        """Posterior over θ by importance sampling with a Laplace proposal: the posterior mode and
        numerical Hessian give a Gaussian (covariance ×2) whose draws are weighted by
        prior × likelihood / proposal. Returns the resampled draws and the effective sample size."""
        from scipy.optimize import minimize
        rng = rng or np.random.default_rng(0)
        s = self.hi(X)
        P0 = np.linalg.inv(self.S0)
        se = self.sigma_eff
        d = len(self.mu0)

        def resid(th):
            a, b, g = self._unpack(np.atleast_2d(th))
            G = np.expm1(g[:, None] * t[None]) / g[:, None]
            return s[None] - a[:, None] - b[:, None] * G

        def nlp(th):
            r = resid(th)[0]
            dd = th - self.mu0
            return 0.5 * r @ r / se ** 2 + 0.5 * dd @ P0 @ dd

        mode = minimize(nlp, self.mu0, method="Nelder-Mead",
                        options={"xatol": 1e-7, "fatol": 1e-9, "maxiter": 4000, "maxfev": 8000}).x
        h = 1e-3
        H = np.empty((d, d))
        E = np.eye(d) * h
        for i in range(d):
            for j in range(d):
                H[i, j] = (nlp(mode + E[i] + E[j]) - nlp(mode + E[i] - E[j]) - nlp(mode - E[i] + E[j]) + nlp(mode - E[i] - E[j])) / (4 * h * h)
        try:
            Sprop = 2.0 * np.linalg.inv(0.5 * (H + H.T))
            np.linalg.cholesky(Sprop)
        except np.linalg.LinAlgError:
            Sprop = self.S0
        th = rng.multivariate_normal(mode, Sprop, size=n_prop)
        r = resid(th)
        lw = -0.5 * np.sum(r ** 2, axis=1) / se ** 2 + _mvn_logpdf(th, self.mu0, self.S0) - _mvn_logpdf(th, mode, Sprop)
        w = np.exp(lw - lw.max()); w /= w.sum()
        return th[rng.choice(n_prop, size=n, p=w)], float(1 / np.sum(w ** 2))

    def rul_samples(self, t, X, n: int = 4000, rng=None, horizon: float = 600.0, return_ess: bool = False):
        rng = rng or np.random.default_rng(0)
        th, ess = self.posterior_draws(t, X, n, rng)
        D = rng.normal(self.mD, self.sD, size=n)
        a, b, g = self._unpack(th)
        with np.errstate(invalid="ignore", divide="ignore", over="ignore"):
            tf = np.log1p(g * (D - a) / b) / g
        tf = np.where(np.isfinite(tf), tf, horizon)
        r = np.clip(tf - t[-1], 0, horizon)
        return (r, ess) if return_ess else r


def _mvn_logpdf(x, m, S):
    d = x - m
    P = np.linalg.inv(S)
    return -0.5 * np.einsum("ij,jk,ik->i", d, P, d) - 0.5 * np.log(np.linalg.det(2 * np.pi * S))


# ------------------------------------------------------------------------------------------------
# scores
# ------------------------------------------------------------------------------------------------
def crps_samples(x: np.ndarray, y: float) -> float:
    """CRPS of an ensemble: E|X − y| − ½E|X − X'| (sorted-sample identity)."""
    x = np.sort(x)
    n = len(x)
    return float(np.mean(np.abs(x - y)) - np.sum((2 * np.arange(1, n + 1) - n - 1) * x) / n ** 2)


def nasa_score(pred, true) -> float:
    """PHM 2008 asymmetric score: late predictions (d > 0) cost more than early ones."""
    d = np.asarray(pred) - np.asarray(true)
    return float(np.sum(np.where(d < 0, np.exp(-d / 13) - 1, np.exp(d / 10) - 1)))


def truncations(fleet: Fleet, rng, per_unit: int = 3, min_cycles: int = 31):
    """Random cut points imitating the test set: (unit, cut cycle, true RUL)."""
    out = []
    for k in fleet.units:
        T = int(fleet.cycle[fleet.unit == k].max())
        for c in rng.integers(min_cycles, T, size=per_unit):
            out.append((k, int(c), T - int(c)))
    return out


def cv_gamma(fleet: Fleet, gammas, folds: int = 5, seed: int = 97):
    """Unit-wise K-fold CV of the mean CRPS for each candidate (a fixed γ, or None for a random γ
    per engine); the health indicator and the prior are refitted inside each fold."""
    rng = np.random.default_rng(seed)
    units = rng.permutation(fleet.units)
    parts = np.array_split(units, folds)
    out = {}
    for g in gammas:
        scores = []
        for p in parts:
            trm = ~np.isin(fleet.unit, p)
            tr = Fleet(fleet.unit[trm], fleet.cycle[trm], fleet.X[trm])
            te = Fleet(fleet.unit[~trm], fleet.cycle[~trm], fleet.X[~trm])
            m = DegradationModel.fit(tr, g)
            for k, c, r in truncations(te, rng):
                t, X = te.of(k)
                keep = t <= c
                scores.append(crps_samples(m.rul_samples(t[keep], X[keep], n=1500, rng=rng), r))
        out["aleatório" if g is None else g] = float(np.mean(scores))
    return out


# ------------------------------------------------------------------------------------------------
# baselines
# ------------------------------------------------------------------------------------------------
def window_features(t, X, hi: HealthIndicator, w: int = 20):
    """Last-window mean and slope of the health indicator and of each standardised sensor."""
    s = hi(X)
    Z = (X - hi.mu) / hi.sd
    k = min(w, len(t))
    tt = t[-k:] - t[-k:].mean()
    slope = lambda v: float(np.dot(tt, v[-k:] - v[-k:].mean()) / max(np.dot(tt, tt), 1e-9))
    return np.r_[s[-k:].mean(), slope(s), Z[-k:].mean(0), [slope(z) for z in Z.T], t[-1]]


def ridge_rul(train: Fleet, cap: float = 125.0, l2: float = 1.0, seed: int = 97):
    """Ridge regression on window features with the piecewise-linear target min(cap, RUL),
    the usual C-MAPSS baseline (Heimes, PHM 2008). Returns a predict(t, X) function."""
    hi = HealthIndicator.fit(train)
    rng = np.random.default_rng(seed)
    F, y = [], []
    for k, c, r in truncations(train, rng, per_unit=20, min_cycles=15):
        t, X = train.of(k)
        keep = t <= c
        F.append(window_features(t[keep], X[keep], hi)); y.append(min(cap, r))
    F, y = np.array(F), np.array(y)
    mu, sd = F.mean(0), F.std(0) + 1e-12
    A = np.column_stack([np.ones(len(F)), (F - mu) / sd])
    P = l2 * np.eye(A.shape[1]); P[0, 0] = 0
    w = np.linalg.solve(A.T @ A + P, A.T @ y)
    return lambda t, X: float(np.clip(np.r_[1, (window_features(t, X, hi) - mu) / sd] @ w, 0, None))


# ------------------------------------------------------------------------------------------------
# lifetime distribution
# ------------------------------------------------------------------------------------------------
def weibull_mle(x: np.ndarray):
    """Two-parameter Weibull MLE (shape k, scale λ) with a 95 % Wald interval from the observed
    information, for complete (uncensored) lifetimes."""
    from scipy.optimize import brentq
    lx = np.log(x)

    def eq(k):
        xk = x ** k
        return np.sum(xk * lx) / np.sum(xk) - 1 / k - lx.mean()
    k = brentq(eq, 0.05, 50)
    lam = np.mean(x ** k) ** (1 / k)
    n = len(x)
    # observed information for (k, λ)
    z = x / lam
    lz = np.log(z)
    zk = z ** k
    I11 = n / k ** 2 + np.sum(zk * lz ** 2)
    I12 = (np.sum(zk) + k * np.sum(zk * lz) - n) / lam
    I22 = k * (k + 1) * np.sum(zk) / lam ** 2 - n * k / lam ** 2
    cov = np.linalg.inv(np.array([[I11, I12], [I12, I22]]))
    se = np.sqrt(np.diag(cov))
    return {"shape": float(k), "scale": float(lam), "shape_ci95": [float(k - 1.96 * se[0]), float(k + 1.96 * se[0])],
            "scale_ci95": [float(lam - 1.96 * se[1]), float(lam + 1.96 * se[1])]}
