"""Time-of-use tariff of a Group A consumer and load shifting by linear programming (#090).

Data:
* **Load** — the real 15-minute electricity use of a steel plant (DAEWOO Steel, Gwangyang, Korea,
  2018; UCI dataset 851, CC BY 4.0), applied to the Brazilian tariff as if the plant were connected
  at 13.8 kV (subgroup A4) in the EDP São Paulo concession.
* **Tariff** — ANEEL's homologated tariffs for EDP SP, REH nº 3.541 of 14 Oct 2025 (in force from
  23 Oct 2025 to 22 Oct 2026), "Tarifa de Aplicação", A4, Verde and Azul. Taxes (ICMS, PIS/COFINS)
  and the tariff flags (bandeiras) are left out: they scale the bill but not the comparisons.

Rules (ANEEL REN 1.000/2021): peak (ponta) is three consecutive hours on working days set by the
distributor — 17:30–20:30 for EDP SP (secondary source; a sensitivity at 18:00–21:00 is run);
billing demand is the larger of contracted and measured 15-minute maximum; measured demand above
105 % of the contract pays the excess at twice the tariff (ultrapassagem).

Shifting LP (per month, HiGHS): a fraction α of each peak interval's load may be moved to the
off-peak intervals of the same day; the objective is energy cost plus the demand charges of the
month's maxima. Energy is conserved day by day; the contract is then re-optimised on the new curve.
"""
from __future__ import annotations

import gzip
import io
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

ROOT = Path(__file__).resolve().parents[1]
DT_H = 0.25


def load_steel() -> pd.Series:
    """kW averaged over each 15-minute interval, indexed by interval start."""
    raw = gzip.decompress((ROOT / "data" / "steel" / "Steel_industry_data.csv.gz").read_bytes()).decode("utf-8-sig")
    d = pd.read_csv(io.StringIO(raw))
    end = pd.to_datetime(d["date"], format="%d/%m/%Y %H:%M")
    # the interval ending at midnight is stamped with the day it closes (NSM = 0): move it to the next day
    end = end + pd.to_timedelta((d["NSM"] == 0).astype(int), unit="D")
    s = pd.Series(d["Usage_kWh"].to_numpy() / DT_H, index=end - pd.Timedelta(minutes=15), name="kW")
    return s.sort_index()


@dataclass(frozen=True)
class Tariff:
    name: str
    D_p: float      # R$/kW peak demand (Azul) or single demand (Verde)
    D_fp: float     # R$/kW off-peak demand (Azul); 0 for Verde
    E_p: float      # R$/MWh TUSD + TE peak
    E_fp: float     # R$/MWh TUSD + TE off-peak
    parts: dict


def tariffs(start="2026-01-01") -> dict:
    """A4 'Tarifa de Aplicação' of EDP SP from the committed ANEEL subset (values ×1/100, see manifest)."""
    d = pd.read_csv(ROOT / "data" / "aneel" / "tarifas_edp_sp.csv", sep=";", dtype=str)
    d = d[(d.subgrupo == "A4") & (d.detalhe == "Não se aplica") & (d.acessante == "Não se aplica") & (d.vigencia_inicio == start)]
    num = lambda x: 0.0 if pd.isna(x) or x == "" else float(x) / 100.0

    def get(mod, posto, unit, col):
        r = d[(d.modalidade == mod) & (d.posto == posto) & (d.unidade == unit)]
        if len(r) != 1:
            raise ValueError(f"{mod}/{posto}/{unit}: {len(r)} rows")
        return num(r.iloc[0][col])

    out = {}
    v = dict(D=get("Verde", "Não se aplica", "R$/kW", "vlr_tusd"),
             tusd_p=get("Verde", "Ponta", "R$/MWh", "vlr_tusd"), te_p=get("Verde", "Ponta", "R$/MWh", "vlr_te"),
             tusd_fp=get("Verde", "Fora ponta", "R$/MWh", "vlr_tusd"), te_fp=get("Verde", "Fora ponta", "R$/MWh", "vlr_te"))
    out["Verde"] = Tariff("Verde", v["D"], 0.0, v["tusd_p"] + v["te_p"], v["tusd_fp"] + v["te_fp"], v)
    a = dict(D_p=get("Azul", "Ponta", "R$/kW", "vlr_tusd"), D_fp=get("Azul", "Fora ponta", "R$/kW", "vlr_tusd"),
             tusd_p=get("Azul", "Ponta", "R$/MWh", "vlr_tusd"), te_p=get("Azul", "Ponta", "R$/MWh", "vlr_te"),
             tusd_fp=get("Azul", "Fora ponta", "R$/MWh", "vlr_tusd"), te_fp=get("Azul", "Fora ponta", "R$/MWh", "vlr_te"))
    out["Azul"] = Tariff("Azul", a["D_p"], a["D_fp"], a["tusd_p"] + a["te_p"], a["tusd_fp"] + a["te_fp"], a)
    return out


def fiob(start="2026-01-01") -> dict:
    """Fio B component (second, independent mirror) for the scale check: must stay below TUSD."""
    f = pd.read_csv(ROOT / "data" / "aneel" / "fiob_edp_sp.csv", dtype=str)
    f = f[(f.subgrupo == "A4") & (f.inicio == start) & (f.acessante == "Não se aplica") & (f.detalhe == "Não se aplica")
          & (f.unidade == "R$/kW") & (f.base == "Tarifa de Aplicação")]
    return {(r.modalidade, r.posto): float(r.fiob) for r in f.itertuples()}


def peak_mask(idx: pd.DatetimeIndex, start="17:30", hours=3, holidays=()):
    t0 = pd.Timedelta(start + ":00")
    tod = idx - idx.normalize()
    working = (idx.day_of_week < 5) & ~pd.Index(idx.normalize()).isin(pd.DatetimeIndex(holidays))
    return np.asarray(working & (tod >= t0) & (tod < t0 + pd.Timedelta(hours=hours)))


def bill(load: pd.Series, peak: np.ndarray, t: Tariff, Dc_p: float, Dc_fp: float = 0.0, tolerance=0.05):
    """Monthly bill components (R$) for a 15-minute kW series."""
    df = pd.DataFrame({"kW": load.to_numpy(), "peak": peak}, index=load.index)
    rows = []
    for m, g in df.groupby(df.index.to_period("M")):
        Ep = g.kW[g.peak].sum() * DT_H / 1000
        Efp = g.kW[~g.peak].sum() * DT_H / 1000
        energy = t.E_p * Ep + t.E_fp * Efp
        if t.name == "Verde":
            Dm = g.kW.max()
            dem = t.D_p * max(Dc_p, Dm)
            over = 2 * t.D_p * (Dm - Dc_p) if Dm > (1 + tolerance) * Dc_p else 0.0
            Dm_p, Dm_fp = g.kW[g.peak].max() if g.peak.any() else 0.0, Dm
        else:
            Dm_p = g.kW[g.peak].max() if g.peak.any() else 0.0
            Dm_fp = g.kW[~g.peak].max()
            dem = t.D_p * max(Dc_p, Dm_p) + t.D_fp * max(Dc_fp, Dm_fp)
            over = (2 * t.D_p * (Dm_p - Dc_p) if Dm_p > (1 + tolerance) * Dc_p else 0.0) \
                + (2 * t.D_fp * (Dm_fp - Dc_fp) if Dm_fp > (1 + tolerance) * Dc_fp else 0.0)
        rows.append({"month": str(m), "E_p_MWh": Ep, "E_fp_MWh": Efp, "energy": energy, "demand": dem, "over": over,
                     "Dmax_p": Dm_p, "Dmax_fp": Dm_fp, "total": energy + dem + over})
    return pd.DataFrame(rows)


def best_contract(load, peak, t: Tariff, step=5.0):
    """Annual-cost-minimising contracted demand(s) by grid search (the cost is not convex: tolerance)."""
    mx = float(load.max())
    grid = np.arange(30.0, mx * 1.1 + step, step)
    if t.name == "Verde":
        costs = [bill(load, peak, t, d)["total"].sum() for d in grid]
        i = int(np.argmin(costs))
        return {"Dc_p": float(grid[i]), "Dc_fp": 0.0, "annual": float(costs[i]), "grid": grid, "costs": np.array(costs)}
    mp = float(load[peak].max())
    gp = np.arange(30.0, mp * 1.1 + step, step)
    best = None
    # the two demands are billed separately, so the minimisation separates
    cp = [bill(load, peak, t, d, mx)["total"].sum() for d in gp]
    dp = float(gp[int(np.argmin(cp))])
    cf = [bill(load, peak, t, dp, d)["total"].sum() for d in grid]
    df_ = float(grid[int(np.argmin(cf))])
    best = {"Dc_p": dp, "Dc_fp": df_, "annual": float(bill(load, peak, t, dp, df_)["total"].sum()), "grid": grid, "costs": np.array(cf)}
    return best


def shift_month(kw: np.ndarray, peak: np.ndarray, day: np.ndarray, t: Tariff, alpha: float):
    """LP for one month. Variables: s_i (peak reduction), u_j (off-peak increase), D_p, D_fp.

    min Σ c_p s_i·(−Δt) + Σ c_fp u_j·Δt + T_p D_p + T_fp D_fp
    s.t. 0 ≤ s_i ≤ α L_i;  Σ_day u = Σ_day s;  L_i − s_i ≤ D_p (peak);  L_j + u_j ≤ D_fp (off-peak);
         Verde: one demand, D_p = D_fp (both rows bound the same variable).
    """
    P = np.flatnonzero(peak)
    F = np.flatnonzero(~peak)
    nP, nF = len(P), len(F)
    nv = nP + nF + 2
    iDp, iDf = nP + nF, nP + nF + 1
    cp, cf = t.E_p / 1000 * DT_H, t.E_fp / 1000 * DT_H
    c = np.zeros(nv)
    c[:nP] = -cp
    c[nP:nP + nF] = cf
    if t.name == "Verde":
        c[iDp] = t.D_p
        dem_fp = iDp
    else:
        c[iDp], c[iDf] = t.D_p, t.D_fp
        dem_fp = iDf
    # inequalities
    r, cidx, v, b = [], [], [], []
    row = 0
    for k, i in enumerate(P):            # L_i − s_i ≤ D_p
        r += [row, row]; cidx += [k, iDp]; v += [-1.0, -1.0]; b.append(-kw[i]); row += 1
    for k, j in enumerate(F):            # L_j + u_j ≤ D_fp
        r += [row, row]; cidx += [nP + k, dem_fp]; v += [1.0, -1.0]; b.append(-kw[j]); row += 1
    A_ub = coo_matrix((v, (r, cidx)), shape=(row, nv)).tocsr()
    # equalities: per day Σu − Σs = 0
    days = np.unique(day)
    r, cidx, v = [], [], []
    for q, dd in enumerate(days):
        for k in np.flatnonzero(day[P] == dd):
            r.append(q); cidx.append(k); v.append(-1.0)
        for k in np.flatnonzero(day[F] == dd):
            r.append(q); cidx.append(nP + k); v.append(1.0)
    A_eq = coo_matrix((v, (r, cidx)), shape=(len(days), nv)).tocsr()
    bounds = [(0, alpha * kw[i]) for i in P] + [(0, None)] * nF + [(0, None), (0, None)]
    res = linprog(c, A_ub=A_ub, b_ub=np.array(b), A_eq=A_eq, b_eq=np.zeros(len(days)), bounds=bounds, method="highs")
    if res.status != 0:
        raise RuntimeError(res.message)
    new = kw.astype(float).copy()
    new[P] -= res.x[:nP]
    new[F] += res.x[nP:nP + nF]
    duals = {"day_energy": res.eqlin.marginals}
    return new, res, duals


def shift_year(load: pd.Series, peak: np.ndarray, t: Tariff, alpha: float):
    out = load.copy()
    kw = load.to_numpy()
    day = pd.factorize(load.index.normalize())[0]          # calendar day id, independent of the index resolution
    months = load.index.to_period("M")
    moved = 0.0
    for m in months.unique():
        sel = np.asarray(months == m)
        new, res, _ = shift_month(kw[sel], peak[sel], day[sel], t, alpha)
        moved += float(np.sum(np.maximum(kw[sel] - new, 0)) * DT_H)
        out.iloc[np.flatnonzero(sel)] = new
    return out, moved / 1000.0
