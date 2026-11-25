"""Plant climate at Taubaté (INMET A728) and the thermal response of a warehouse to it (#063).

1. **Climatology.** Annual mean temperature, cooling and heating degree-days (base 18 °C on the
   daily mean) and hot days (Tmax ≥ 32 °C), for years with at least 330 valid days. Trend by the
   Mann–Kendall test with Sen's slope (Sen, 1968; Kendall, 1975).
2. **Hourly forcing from daily data.** Hourly temperature reconstructed from Tmin and Tmax with a
   two-piece cosine (minimum at 06 h, maximum at 15 h), a standard approximation when only daily
   extremes exist. Global radiation by Hargreaves–Samani, Rs = k_Rs·√(Tmax − Tmin)·Ra, with
   k_Rs = 0.16 for interior locations and Ra from FAO-56 (eq. 21), spread over daylight hours with
   a sine. Both are estimates: the station's measured hourly series is not in this dataset.
3. **Warehouse model (1R1C).** One thermal node (air, contents and floor slab, capacitance C):

       C dT_i/dt = U_r A (T_sa − T_i) + (U_w A_w + ρ c_p V̇)(T_o − T_i) + Q_int − Q_cool
       T_sa = T_o + α G / h_o            (sol-air temperature of the roof, ASHRAE)

   integrated hourly (implicit Euler, unconditionally stable). Q_cool keeps T_i ≤ T_set when
   cooling is on (ideal controller); its electric energy is Q_cool/COP. Envelope values are
   order-of-magnitude hypotheses, stated in ``Warehouse``; the point is to compare roof options
   and years under real weather, not to predict a specific building.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
import pandas as pd

from .data import inmet_daily

STATION = "A728"
LAT = -23.04166666          # from the INMET file
MIN_DAYS = 330


# ------------------------------------------------------------------------------------------------
# climatology
# ------------------------------------------------------------------------------------------------
def annual(w: pd.DataFrame, base: float = 18.0) -> pd.DataFrame:
    g = w.groupby(w.index.year)
    out = pd.DataFrame({"days": g.tmean.count(), "tmean": g.tmean.mean(), "tmax_mean": g.tmax.mean(),
                        "cdd": g.tmean.apply(lambda s: np.maximum(s - base, 0).sum()),
                        "hdd": g.tmean.apply(lambda s: np.maximum(base - s, 0).sum()),
                        "hot_days": g.tmax.apply(lambda s: int((s >= 32).sum()))})
    # degree-days scaled to a full year so years with a few missing days stay comparable
    out["cdd"] *= 365.25 / out["days"]
    out["hdd"] *= 365.25 / out["days"]
    out["hot_days"] = out["hot_days"] * 365.25 / out["days"]
    return out[out.days >= MIN_DAYS]


def mann_kendall(y: np.ndarray, x: np.ndarray | None = None):
    """Mann–Kendall S, normal-approximation z and two-sided p (tie-corrected variance), and Sen's
    slope with its 95 % interval (Gilbert, 1987)."""
    from scipy.stats import norm
    y = np.asarray(y, float)
    x = np.arange(len(y), dtype=float) if x is None else np.asarray(x, float)
    n = len(y)
    s = sum(np.sign(y[j] - y[i]) for i in range(n - 1) for j in range(i + 1, n))
    _, counts = np.unique(y, return_counts=True)
    var = (n * (n - 1) * (2 * n + 5) - np.sum(counts * (counts - 1) * (2 * counts + 5))) / 18
    z = (s - np.sign(s)) / np.sqrt(var) if s != 0 else 0.0
    p = 2 * (1 - norm.cdf(abs(z)))
    slopes = np.sort([(y[j] - y[i]) / (x[j] - x[i]) for i in range(n - 1) for j in range(i + 1, n)])
    N = len(slopes)
    ca = 1.96 * np.sqrt(var)
    lo, hi = int(np.floor((N - ca) / 2)), int(np.ceil((N + ca) / 2))
    return {"S": float(s), "z": float(z), "p": float(p), "sen": float(np.median(slopes)),
            "sen_ci95": [float(slopes[max(lo, 0)]), float(slopes[min(hi, N - 1)])], "n": n}


# ------------------------------------------------------------------------------------------------
# hourly forcing
# ------------------------------------------------------------------------------------------------
def extraterrestrial(doy: np.ndarray, lat_deg: float = LAT) -> np.ndarray:
    """Daily extraterrestrial radiation Ra (MJ m⁻² day⁻¹), FAO-56 eq. 21."""
    phi = np.radians(lat_deg)
    dr = 1 + 0.033 * np.cos(2 * np.pi * doy / 365)
    dec = 0.409 * np.sin(2 * np.pi * doy / 365 - 1.39)
    ws = np.arccos(np.clip(-np.tan(phi) * np.tan(dec), -1, 1))
    return 24 * 60 / np.pi * 0.0820 * dr * (ws * np.sin(phi) * np.sin(dec) + np.cos(phi) * np.cos(dec) * np.sin(ws))


def daylength(doy: np.ndarray, lat_deg: float = LAT) -> np.ndarray:
    phi = np.radians(lat_deg)
    dec = 0.409 * np.sin(2 * np.pi * doy / 365 - 1.39)
    return 24 / np.pi * np.arccos(np.clip(-np.tan(phi) * np.tan(dec), -1, 1))


def fill_daily(w: pd.DataFrame) -> pd.DataFrame:
    """Continuous daily series: gaps filled with the smoothed day-of-year climatology (flagged)."""
    w = w.asfreq("D")
    clim = {}
    for c in ("tmin", "tmax"):
        m = w[c].groupby(w.index.dayofyear).mean().reindex(range(1, 367)).interpolate(limit_direction="both")
        sm = np.convolve(np.r_[m.to_numpy()[-15:], m.to_numpy(), m.to_numpy()[:15]], np.ones(31) / 31, mode="valid")
        clim[c] = pd.Series(sm, index=range(1, 367))
    filled = w[["tmin", "tmax"]].isna().any(axis=1)
    for c in ("tmin", "tmax"):
        w[c] = w[c].fillna(pd.Series(clim[c].reindex(w.index.dayofyear).to_numpy(), index=w.index))
    w["filled"] = filled
    return w


def hourly_forcing(w: pd.DataFrame, k_rs: float = 0.16):
    """Hourly outdoor temperature (°C) and global horizontal irradiance (W/m²)."""
    tmin, tmax = w.tmin.to_numpy(), w.tmax.to_numpy()
    tmin_next = np.r_[tmin[1:], tmin[-1]]
    h = np.arange(24)
    T = np.empty((len(w), 24))
    for i in range(len(w)):
        rise = (h >= 6) & (h <= 15)
        T[i, rise] = tmin[i] + (tmax[i] - tmin[i]) * (1 - np.cos(np.pi * (h[rise] - 6) / 9)) / 2
        after = h > 15
        T[i, after] = tmin_next[i] + (tmax[i] - tmin_next[i]) * (1 + np.cos(np.pi * (h[after] - 15) / 15)) / 2
        before = h < 6
        prev_max = tmax[i - 1] if i else tmax[i]
        T[i, before] = tmin[i] + (prev_max - tmin[i]) * (1 + np.cos(np.pi * (h[before] + 9) / 15)) / 2
    doy = w.index.dayofyear.to_numpy()
    Rs = k_rs * np.sqrt(np.maximum(tmax - tmin, 0)) * extraterrestrial(doy)       # MJ/m²/day
    N = daylength(doy)
    G = np.zeros((len(w), 24))
    for i in range(len(w)):
        sr, ss = 12 - N[i] / 2, 12 + N[i] / 2
        hh = h + 0.5
        shape = np.where((hh > sr) & (hh < ss), np.sin(np.pi * (hh - sr) / N[i]), 0.0)
        if shape.sum() > 0:
            G[i] = Rs[i] * 1e6 / 3600 * shape / shape.sum()                  # W/m² hourly mean
    return T.ravel(), G.ravel(), Rs


# ------------------------------------------------------------------------------------------------
# warehouse
# ------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Warehouse:
    area: float = 2000.0              # m², floor = roof
    wall_area: float = 1440.0         # m², 4 walls 8 m high around 45 × 45 m
    U_roof: float = 5.0               # W/m²K, single metal sheet (hypothesis); 0.5 with 50 mm PU sandwich
    U_wall: float = 2.5               # W/m²K, block wall
    alpha: float = 0.8                # roof solar absorptance (weathered metal); 0.3 for a white roof
    h_out: float = 17.0               # W/m²K, outdoor surface coefficient (ASHRAE)
    ach: float = 0.5                  # air changes per hour
    height: float = 8.0
    C_per_m2: float = 100e3           # J/m²K effective (slab, racks, goods)
    q_int: float = 5.0                # W/m² internal gains in working hours (lighting, people, forklifts)
    t_set: float = 26.0               # °C cooling set point
    cop: float = 3.0

    def label(self) -> str:
        return f"U={self.U_roof:g}, α={self.alpha:g}"


SCENARIOS = {
    "Telha metálica escura": Warehouse(),
    "Telha metálica branca": Warehouse(alpha=0.3),
    "Telha sanduíche escura": Warehouse(U_roof=0.5),
    "Telha sanduíche branca": Warehouse(U_roof=0.5, alpha=0.3),
}


def simulate(b: Warehouse, T_out: np.ndarray, G: np.ndarray, hours_index: pd.DatetimeIndex, cooling: bool):
    """Hourly indoor temperature and cooling power (W, thermal) by implicit Euler with dt = 1 h."""
    dt = 3600.0
    C = b.C_per_m2 * b.area
    vent = 1.2 * 1005 * b.ach * b.area * b.height / 3600
    K_roof, K_out = b.U_roof * b.area, b.U_wall * b.wall_area + vent
    work = (hours_index.hour >= 7) & (hours_index.hour < 17) & (hours_index.day_of_week < 6)
    q = np.where(work, b.q_int * b.area, 0.0)
    Tsa = T_out + b.alpha * G / b.h_out
    Ti = np.empty_like(T_out)
    Qc = np.zeros_like(T_out)
    x = T_out[0]
    denom = C / dt + K_roof + K_out
    for k in range(len(T_out)):
        xn = (C / dt * x + K_roof * Tsa[k] + K_out * T_out[k] + q[k]) / denom
        if cooling and xn > b.t_set:
            Qc[k] = (C / dt * x + K_roof * Tsa[k] + K_out * T_out[k] + q[k]) - denom * b.t_set
            xn = b.t_set
        Ti[k] = x = xn
    return Ti, Qc


def run_years(w: pd.DataFrame, scenarios=SCENARIOS):
    """Per scenario and complete year: hours above 30 °C free-running, cooling electricity (MWh)
    and peak cooling power (kW electric), plus the annual CDD of the same (filled) series."""
    wf = fill_daily(w)
    T, G, _ = hourly_forcing(wf)
    idx = pd.date_range(wf.index[0], periods=len(T), freq="h")
    valid = w.groupby(w.index.year).tmean.count()
    years = [y for y in sorted(set(idx.year)) if valid.get(y, 0) >= MIN_DAYS]
    res = {}
    for name, b in scenarios.items():
        Ti_free, _ = simulate(b, T, G, idx, cooling=False)
        _, Qc = simulate(b, T, G, idx, cooling=True)
        rows = {}
        for y in years:
            m = idx.year == y
            rows[y] = {"hours_above_30": int((Ti_free[m] > 30).sum()), "ti_max": float(Ti_free[m].max()),
                       "cooling_mwh": float(Qc[m].sum() / b.cop / 1e6), "peak_kw": float(Qc[m].max() / b.cop / 1e3)}
        res[name] = rows
    cdd = {y: float(np.maximum(T[idx.year == y].reshape(-1, 24).mean(1) - 18, 0).sum()) for y in years}
    return res, years, cdd, (T, G, idx)
