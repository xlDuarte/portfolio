"""Change-point (degree-day) regression of energy use on temperature, ASHRAE Guideline 14 (#008).

Energy use responds to outdoor temperature only beyond a balance point: below it the load is the
temperature-independent base, above it cooling adds roughly in proportion to the excess. The
classic inverse models are

    2P:  E = β₀ + β₁ T
    3PC: E = β₀ + β_c (T − T_c)⁺                      cooling only
    3PH: E = β₀ + β_h (T_h − T)⁺                      heating only
    4P:  E = β₀ + β_l (T − T_b)⁻ + β_r (T − T_b)⁺     one change point, two slopes
    5P:  E = β₀ + β_h (T_h − T)⁺ + β_c (T − T_c)⁺     dead band between T_h and T_c

with (x)⁺ = max(x, 0) and (x)⁻ = min(x, 0). Change points are found by grid search (profile least
squares); the remaining coefficients are linear. Extra regressors (year, day type) enter
additively, so the temperature response is estimated net of growth and calendar.

Goodness of fit follows Guideline 14: CV(RMSE) = RMSE/ȳ with n − p degrees of freedom and
NMBE = Σ(y − ŷ)/((n − p)·ȳ). Uncertainty of the change point and slopes comes from a moving-block
bootstrap of residuals (blocks of 28 days keep the autocorrelation), and Guideline 14's
autocorrelation correction n′ = n(1 − ρ)/(1 + ρ) is reported.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

GRID = np.arange(14.0, 27.01, 0.1)


def _design(T, kind, cps, Z):
    cols = [np.ones_like(T)]
    if kind == "2P":
        cols.append(T)
    elif kind == "3PC":
        cols.append(np.maximum(T - cps[0], 0))
    elif kind == "3PH":
        cols.append(np.maximum(cps[0] - T, 0))
    elif kind == "4P":
        cols += [np.minimum(T - cps[0], 0), np.maximum(T - cps[0], 0)]
    elif kind == "5P":
        cols += [np.maximum(cps[0] - T, 0), np.maximum(T - cps[1], 0)]
    X = np.column_stack(cols)
    return np.column_stack([X, Z]) if Z is not None and Z.size else X


N_CP = {"2P": 0, "3PC": 1, "3PH": 1, "4P": 1, "5P": 2}


@dataclass
class Fit:
    kind: str
    cps: tuple
    beta: np.ndarray
    sse: float
    n: int
    p: int
    ybar: float
    resid: np.ndarray

    @property
    def cvrmse(self) -> float:
        return float(np.sqrt(self.sse / (self.n - self.p)) / self.ybar)

    @property
    def nmbe(self) -> float:
        return float(self.resid.sum() / ((self.n - self.p) * self.ybar))

    @property
    def bic(self) -> float:
        return float(self.n * np.log(self.sse / self.n) + self.p * np.log(self.n))

    @property
    def rho(self) -> float:
        r = self.resid
        return float(np.corrcoef(r[:-1], r[1:])[0, 1])

    @property
    def n_eff(self) -> float:
        return float(self.n * (1 - self.rho) / (1 + self.rho))

    def predict(self, T, Z=None):
        return _design(np.asarray(T, float), self.kind, self.cps, Z) @ self.beta


def fit(T, y, kind: str, Z=None, grid=GRID) -> Fit:
    T, y = np.asarray(T, float), np.asarray(y, float)
    best = None
    if N_CP[kind] == 0:
        cands = [()]
    elif N_CP[kind] == 1:
        cands = [(c,) for c in grid]
    else:
        cands = [(a, b) for a in grid[::3] for b in grid[::3] if b > a + 0.5]
    for cps in cands:
        X = _design(T, kind, cps, Z)
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        r = y - X @ beta
        sse = float(r @ r)
        if best is None or sse < best[0]:
            best = (sse, cps, beta, r, X.shape[1])
    if N_CP[kind] == 2:          # refine the coarse 5P grid locally
        a0, b0 = best[1]
        for a in np.arange(a0 - 0.3, a0 + 0.31, 0.1):
            for b in np.arange(b0 - 0.3, b0 + 0.31, 0.1):
                if b <= a + 0.5:
                    continue
                X = _design(T, kind, (a, b), Z)
                beta, *_ = np.linalg.lstsq(X, y, rcond=None)
                r = y - X @ beta
                if r @ r < best[0]:
                    best = (float(r @ r), (a, b), beta, r, X.shape[1])
    sse, cps, beta, r, p = best
    return Fit(kind, tuple(float(c) for c in cps), beta, sse, len(y), p + N_CP[kind], float(y.mean()), r)


def block_bootstrap(T, y, f: Fit, Z=None, n_boot: int = 300, block: int = 28, seed: int = 8):
    """Moving-block bootstrap of residuals around the fitted curve; refits the same model."""
    rng = np.random.default_rng(seed)
    yhat = y - f.resid
    n = len(y)
    out = []
    for _ in range(n_boot):
        starts = rng.integers(0, n - block, size=n // block + 1)
        rb = np.concatenate([f.resid[s:s + block] for s in starts])[:n]
        g = fit(T, yhat + rb, f.kind, Z)
        out.append(list(g.cps) + list(g.beta[: 1 + max(N_CP[f.kind], 1) + (1 if f.kind in ("4P", "5P") else 0)]))
    return np.array(out)
