"""Gaussian plume from a hypothetical stack driven by real hourly weather at Taubaté (#069).

Weather: INMET automatic station A728 (Taubaté, SP), hourly wind speed and direction at 10 m,
global radiation and air temperature, from the INMET yearly archives (BDMEP).

Model (steady-state Gaussian plume, as in EPA's ISC3 short-term model, rural):

    C(x, y, 0) = Q / (π u σ_y σ_z) · exp(−y²/2σ_y²) · exp(−H²/2σ_z²)

* **Stability class** (Pasquill–Gifford, Turner 1964). Daytime from wind speed and incoming solar
  radiation (strong > 600, moderate 300–600, slight < 300 W/m²). At night the method needs cloud
  cover, which the station does not report: two bounding assumptions are run, overcast (≥ 4/8,
  classes D–E) and clear (≤ 3/8, classes E–F). Intermediate classes (A–B, …) are averaged in σ.
* **Dispersion** σ_y, σ_z: Briggs (1973) open-country formulas.
* **Wind at stack height**: power law with the ISC rural exponents (A–F: 0.07, 0.07, 0.10, 0.15,
  0.35, 0.55); wind below 1 m/s is set to 1 m/s (calm-hour convention).
* **Plume rise**: Briggs buoyant rise. F_b = g v_s d² (T_s − T_a)/(4 T_s); neutral/unstable final
  rise 21.425 F^(3/4)/u (F < 55) or 38.71 F^(3/5)/u; stable 2.6 (F/(u s))^(1/3) with
  s = (g/T_a)·∂θ/∂z, ∂θ/∂z = 0.020 (E) and 0.035 K/m (F).
* No mixing-height cap, no terrain, no building downwash: screening-level estimates.
"""
from __future__ import annotations

import io
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

G = 9.80665
CLASSES = "ABCDEF"
P_EXP = np.array([0.07, 0.07, 0.10, 0.15, 0.35, 0.55])
DTHETA = {4: 0.020, 5: 0.035}  # K/m for E (index 4) and F (index 5)


ROOT = Path(__file__).resolve().parents[1]


def read_inmet_hourly(zip_path, station="A728"):
    """Hourly INMET file for one station out of a yearly archive (latin-1, ';', decimal comma)."""
    with zipfile.ZipFile(zip_path) as z:
        name = next(n for n in z.namelist() if f"_{station}_" in n)
        raw = z.read(name)
    m, head = parse_inmet_hourly(raw)
    return m, head, name


def load_taubate(years=(2022, 2023, 2024, 2025)):
    """Committed hourly files of station A728 (data/inmet_hourly), concatenated."""
    import gzip
    frames, head = [], None
    for y in years:
        m, head = parse_inmet_hourly(gzip.decompress((ROOT / "data" / "inmet_hourly" / f"A728_{y}.csv.gz").read_bytes()))
        frames.append(m)
    return pd.concat(frames).sort_index(), head


def parse_inmet_hourly(raw: bytes):
    text = raw.decode("latin-1")
    lines = text.splitlines()
    head = {l.split(":;")[0]: l.split(":;")[1] for l in lines[:8] if ":;" in l}
    df = pd.read_csv(io.StringIO("\n".join(lines[8:])), sep=";", decimal=",", na_values=["", "-9999"])
    find = lambda pat: next(c for c in df.columns if re.search(pat, c, re.I))
    date_col = df.columns[0]
    hour_col = df.columns[1]
    hh = df[hour_col].astype(str).str.extract(r"(\d{2})(\d{2})")[0].astype(int)
    t = pd.to_datetime(df[date_col].astype(str).str.replace("-", "/"), format="%Y/%m/%d") + pd.to_timedelta(hh, unit="h")
    out = pd.DataFrame({
        "T": df[find(r"BULBO SECO")].to_numpy(float),
        "rad_kj": df[find(r"RADIACAO GLOBAL")].to_numpy(float),
        "wd": df[find(r"DIRE..O HORARIA")].to_numpy(float),
        "ws": df[find(r"VELOCIDADE HORARIA")].to_numpy(float),
    }, index=pd.DatetimeIndex(t))
    out.index.name = "utc"
    return out, head


@dataclass(frozen=True)
class Stack:
    h: float = 40.0     # m
    d: float = 1.5      # m
    v: float = 12.0     # m/s
    Ts: float = 420.0   # K
    Q: float = 1.0      # g/s (results scale linearly)


def stability(ws, rad_wm2, is_day, night="overcast"):
    """Pasquill–Gifford class as a float index (A = 0 … F = 5); halves for intermediate classes."""
    ws = np.asarray(ws, float)
    r = np.asarray(rad_wm2, float)
    wbin = np.digitize(ws, [2, 3, 5, 6])            # 0:<2, 1:2–3, 2:3–5, 3:5–6, 4:>6
    # day table [wind bin][insolation strong, moderate, slight]
    day = np.array([[0, 0.5, 1], [0.5, 1, 2], [1, 1.5, 2], [2, 2.5, 3], [2, 3, 3]])
    ins = np.where(r > 600, 0, np.where(r >= 300, 1, 2))
    # night: overcast (≥ 4/8) and clear (≤ 3/8); Turner uses E/F for winds < 3 m/s
    n_over = np.array([4, 4, 3, 3, 3])
    n_clear = np.array([5, 5, 4, 3, 3])
    nt = n_over if night == "overcast" else n_clear
    return np.where(is_day, day[wbin, ins], nt[wbin])


def _briggs(cls_idx, x):
    """σ_y, σ_z (m) for integer class index and downwind distance x (m), Briggs rural."""
    x = np.asarray(x, float)
    sy = np.array([0.22, 0.16, 0.11, 0.08, 0.06, 0.04])[cls_idx] * x / np.sqrt(1 + 1e-4 * x)
    sz = np.select([cls_idx == 0, cls_idx == 1, cls_idx == 2, cls_idx == 3, cls_idx == 4],
                   [0.20 * x, 0.12 * x, 0.08 * x / np.sqrt(1 + 2e-4 * x), 0.06 * x / np.sqrt(1 + 1.5e-3 * x),
                    0.03 * x / (1 + 3e-4 * x)], 0.016 * x / (1 + 3e-4 * x))
    return sy, sz


def sigmas(cls, x):
    """Allow half classes: geometric mean of the two neighbours."""
    lo = np.floor(cls).astype(int)
    hi = np.ceil(cls).astype(int)
    sy1, sz1 = _briggs(lo, x)
    sy2, sz2 = _briggs(hi, x)
    return np.sqrt(sy1 * sy2), np.sqrt(sz1 * sz2)


def wind_at(ws10, cls, h):
    p = np.sqrt(P_EXP[np.floor(cls).astype(int)] * P_EXP[np.ceil(cls).astype(int)])
    return np.maximum(ws10, 1.0) * (h / 10.0) ** p


def plume_rise(stack: Stack, u, Ta_K, cls):
    F = G * stack.v * stack.d**2 * (stack.Ts - Ta_K) / (4 * stack.Ts)
    F = np.maximum(F, 0.0)
    neutral = np.where(F < 55, 21.425 * F**0.75, 38.71 * F**0.6) / u
    k = np.ceil(cls).astype(int)
    dth = np.where(k == 5, DTHETA[5], DTHETA[4])
    s = G / Ta_K * dth
    stable = 2.6 * (F / (u * s)) ** (1 / 3)
    return np.where(k >= 4, stable, neutral), F


def ground_conc(stack: Stack, met: pd.DataFrame, cls, xs, dirs_deg):
    """Hourly ground-level concentration (µg/m³) on a polar receptor grid.

    met: columns ws, wd (direction the wind blows FROM, degrees), T (°C). Receptors at distances
    xs (m) along directions dirs_deg (degrees, where the receptor lies FROM the stack). Returns an
    array [hours, len(dirs), len(xs)].
    """
    u = wind_at(met.ws.to_numpy(), cls, stack.h)
    dh, _ = plume_rise(stack, u, met["T"].to_numpy() + 273.15, cls)
    H = stack.h + dh
    to = (met.wd.to_numpy() + 180.0) % 360.0                     # direction the plume travels to
    rel = np.radians((dirs_deg[None, :] - to[:, None] + 540.0) % 360.0 - 180.0)   # [h, d]
    out = np.zeros((len(met), len(dirs_deg), len(xs)), np.float32)
    for j, R in enumerate(xs):
        xd = R * np.cos(rel)                                     # downwind distance
        yd = R * np.sin(rel)                                     # crosswind
        ok = xd > 1.0
        sy, sz = sigmas(np.repeat(cls[:, None], len(dirs_deg), 1), np.where(ok, xd, 1.0))
        c = stack.Q * 1e6 / (np.pi * u[:, None] * sy * sz) * np.exp(-yd**2 / (2 * sy**2)) * np.exp(-H[:, None] ** 2 / (2 * sz**2))
        out[:, :, j] = np.where(ok, c, 0.0)
    return out, H


def centerline(stack: Stack, u10, cls, Ta_C, xs):
    """Ground-level centerline concentration for one fixed condition (µg/m³ per g/s)."""
    cls = np.full(1, cls, float)
    u = wind_at(np.array([u10]), cls, stack.h)
    dh, F = plume_rise(stack, u, np.array([Ta_C + 273.15]), cls)
    H = stack.h + dh[0]
    sy, sz = sigmas(np.full(len(xs), cls[0]), np.asarray(xs, float))
    return stack.Q * 1e6 / (np.pi * u[0] * sy * sz) * np.exp(-H**2 / (2 * sz**2)), H, float(F[0])


def solar_elevation(utc: pd.DatetimeIndex, lat_deg: float, lon_deg: float):
    """Solar elevation angle (degrees), NOAA low-precision formulas (declination, equation of time)."""
    doy = utc.dayofyear.to_numpy()
    hour = utc.hour.to_numpy() + utc.minute.to_numpy() / 60.0 - 0.5      # middle of the hour that ends at the stamp
    g = 2 * np.pi / 365 * (doy - 1 + (hour - 12) / 24)
    eqt = 229.18 * (0.000075 + 0.001868 * np.cos(g) - 0.032077 * np.sin(g) - 0.014615 * np.cos(2 * g) - 0.040849 * np.sin(2 * g))
    decl = (0.006918 - 0.399912 * np.cos(g) + 0.070257 * np.sin(g) - 0.006758 * np.cos(2 * g) + 0.000907 * np.sin(2 * g)
            - 0.002697 * np.cos(3 * g) + 0.00148 * np.sin(3 * g))
    tst = hour * 60 + eqt + 4 * lon_deg
    ha = np.radians(tst / 4 - 180)
    lat = np.radians(lat_deg)
    cosz = np.sin(lat) * np.sin(decl) + np.cos(lat) * np.cos(decl) * np.cos(ha)
    return np.degrees(np.arcsin(np.clip(cosz, -1, 1)))


def prepare(met: pd.DataFrame, lat: float, lon: float):
    """Day flag from the sun, radiation in W/m² (night blanks → 0), drop hours missing what the model needs."""
    m = met.copy()
    elev = solar_elevation(m.index, lat, lon)
    m["day"] = elev > 0
    m["rad"] = m["rad_kj"] / 3.6
    m.loc[~m["day"] & m["rad"].isna(), "rad"] = 0.0
    m.loc[~m["day"], "rad"] = 0.0
    ok = m[["T", "ws", "wd", "rad"]].notna().all(axis=1) & (m.ws >= 0)
    return m[ok], int((~ok).sum())
