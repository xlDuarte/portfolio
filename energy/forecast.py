"""Day-ahead probabilistic forecast of the daily peak load (#064).

Dynamic harmonic regression with a physical temperature term:

    y_t = Σ_d γ_d·1[dow = d] + δ_h·holiday + δ_b·ponto facultativo
          + Σ_k (a_k cos 2πkτ + b_k sin 2πkτ) + θ·t + β_l (T_t − T_b)⁻ + β_r (T_t − T_b)⁺ + u_t
    u_t = φ u_{t−1} + ε_t

τ is the fraction of the year and T_b the change point found by the Guideline 14 model (#008)
on the training years only. The temperature of the forecast day is the observed one; that is an
oracle, so the evaluation also adds Gaussian noise of 1 and 2 °C to imitate a day-ahead
temperature forecast. Coefficients by least squares, then φ from the residuals. The predictive
distribution adds the empirical innovations of the training period to the point forecast, which
keeps their skew and tails; it is scored with the CRPS and interval coverage.

Training: 2019–2022 without 16 Mar–30 Jun 2020 (lockdown, a structural break the model does not
describe). Test: 2023 until the last day with temperature (30 Nov 2023).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .changepoint import fit as cp_fit

COVID = ("2020-03-16", "2020-06-30")


def design(df: pd.DataFrame, Tb: float, temp: np.ndarray | None = None, t0: pd.Timestamp | None = None, K: int = 3):
    T = df["temp"].to_numpy() if temp is None else temp
    t0 = t0 or df.index[0]
    tau = df.index.dayofyear.to_numpy() / 365.25
    cols = [(df["dow"].to_numpy() == d).astype(float) for d in range(7)]
    cols += [df["holiday"].to_numpy(float), df["bridge"].to_numpy(float)]
    for k in range(1, K + 1):
        cols += [np.cos(2 * np.pi * k * tau), np.sin(2 * np.pi * k * tau)]
    cols.append((df.index - t0).days.to_numpy() / 365.25)
    cols += [np.minimum(T - Tb, 0), np.maximum(T - Tb, 0)]
    return np.column_stack(cols)


class PeakModel:
    def __init__(self, target: str = "peak", use_temp: bool = True):
        self.target, self.use_temp = target, use_temp

    def fit(self, train: pd.DataFrame):
        tr = train.dropna(subset=["temp", self.target])
        wk = tr[(tr.dow < 5) & ~tr.holiday & ~tr.bridge]
        years = sorted(wk.index.year.unique())
        Z = np.column_stack([(wk.index.year == y).astype(float) for y in years[1:]])
        self.cp = cp_fit(wk.temp.to_numpy(), wk[self.target].to_numpy(), "4P", Z)
        self.Tb = self.cp.cps[0]
        self.t0 = tr.index[0]
        X = self._X(tr)
        self.beta, *_ = np.linalg.lstsq(X, tr[self.target].to_numpy(), rcond=None)
        r = pd.Series(tr[self.target].to_numpy() - X @ self.beta, index=tr.index)
        lag = r.shift(1, freq="D").reindex(r.index)
        ok = lag.notna()
        self.phi = float(np.dot(r[ok], lag[ok]) / np.dot(lag[ok], lag[ok]))
        self.innov = (r[ok] - self.phi * lag[ok]).to_numpy()
        self.resid = r
        return self

    def _X(self, df, temp=None):
        X = design(df, self.Tb, temp, self.t0)
        return X if self.use_temp else X[:, :-2]

    def predict(self, df: pd.DataFrame, history: pd.Series, temp=None):
        """Point forecasts for each day of df using the observed residual of the previous day."""
        X = self._X(df, temp)
        base = X @ self.beta
        # residual of day t−1 from its observation (known when forecasting day t)
        Xh = self._X(df) if temp is None else self._X(df)          # observed temperature for yesterday
        rh = history.reindex(df.index).to_numpy() - Xh @ self.beta
        prev = pd.Series(rh, index=df.index).shift(1, freq="D").reindex(df.index)
        first = df.index[0] - pd.Timedelta(days=1)
        if first in self.resid.index:
            prev.iloc[0] = self.resid[first]
        prev = prev.fillna(0.0).to_numpy()
        return base + self.phi * prev

    def samples(self, point: np.ndarray, rng, n: int = 2000):
        return point[:, None] + rng.choice(self.innov, size=(len(point), n))

    def samples_uncertain_temp(self, df, history, temp_fcst, sigma: float, rng, n: int = 2000):
        """Ensemble that also propagates the temperature-forecast error: each member draws
        T ~ N(T̂, σ²) and goes through the change-point term, then adds an innovation."""
        p0 = self.predict(df, history, temp_fcst)
        X = self._X(df, temp_fcst)
        hinge0 = X[:, -2:] @ self.beta[-2:]
        Tm = temp_fcst[:, None] + rng.normal(0, sigma, (len(df), n))
        hinge = self.beta[-2] * np.minimum(Tm - self.Tb, 0) + self.beta[-1] * np.maximum(Tm - self.Tb, 0)
        return (p0 - hinge0)[:, None] + hinge + rng.choice(self.innov, size=(len(df), n))


def crps_ensemble(S: np.ndarray, y: np.ndarray) -> np.ndarray:
    """CRPS per row of an ensemble matrix (sorted-sample identity)."""
    S = np.sort(S, axis=1)
    n = S.shape[1]
    w = (2 * np.arange(1, n + 1) - n - 1) / n ** 2
    return np.mean(np.abs(S - y[:, None]), axis=1) - S @ w


def split(df: pd.DataFrame, test_start="2023-01-01"):
    train = df[(df.index < test_start) & ~((df.index >= COVID[0]) & (df.index <= COVID[1]))]
    test = df[(df.index >= test_start) & df.temp.notna()]
    return train, test
