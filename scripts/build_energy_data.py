"""Build site/data/energy.json (phase 5a: projects #008, #064, #063).

    python scripts/build_energy_data.py

Real data, committed: ONS hourly load (SE/CO subsystem, 2019–2025) and INMET daily weather of
São Paulo, Rio de Janeiro, Belo Horizonte and Taubaté. Deterministic (fixed seeds).
"""
from __future__ import annotations

import json
import platform
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import scipy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from energy import changepoint as CP  # noqa: E402
from energy import climate as K  # noqa: E402
from energy import data as E  # noqa: E402
from energy import forecast as F  # noqa: E402

OUT = ROOT / "site" / "data" / "energy.json"
r3 = lambda x: round(float(x), 3)
r1 = lambda x: round(float(x), 1)


def weekday_panel(df):
    return df[(df.dow < 5) & ~df.holiday & ~df.bridge & df.temp.notna()]


def year_dummies(idx, years):
    return np.column_stack([(idx.year == y).astype(float) for y in years[1:]])


def changepoint_block(df):
    wk = weekday_panel(df)
    wk = wk[~((wk.index >= F.COVID[0]) & (wk.index <= F.COVID[1]))]
    years = sorted(wk.index.year.unique())
    Z = year_dummies(wk.index, years)
    T, y = wk.temp.to_numpy(), wk.load.to_numpy()
    fits = {k: CP.fit(T, y, k, Z) for k in ("2P", "3PC", "3PH", "4P", "5P")}
    best = min(fits, key=lambda k: fits[k].bic)
    f = fits[best]
    boot = CP.block_bootstrap(T, y, f, Z)
    q = lambda a: [r3(np.quantile(a, 0.025)), r3(np.quantile(a, 0.975))]
    table = {k: {"cps": [r1(c) for c in g.cps], "slopes": [r1(b) for b in g.beta[1:1 + {"2P": 1, "3PC": 1, "3PH": 1, "4P": 2, "5P": 2}[k]]],
                 "cvrmse": r3(g.cvrmse), "nmbe": round(g.nmbe, 6), "bic": r1(g.bic), "rho": r3(g.rho), "n_eff": r1(g.n_eff)} for k, g in fits.items()}
    # year-adjusted scatter: remove the year effects so all years share the 2019 level
    adj = y - (Z @ f.beta[-Z.shape[1]:])
    tg = np.linspace(T.min(), T.max(), 120)
    curve = f.predict(tg, np.zeros((len(tg), Z.shape[1])))
    by_year = {}
    for yr in years:
        m = wk.index.year == yr
        g = CP.fit(T[m], y[m], "4P")
        by_year[str(yr)] = {"cp": r1(g.cps[0]), "slope_cool": r1(g.beta[2]), "base": r1(g.predict([g.cps[0]])[0]), "n": int(m.sum()), "cvrmse": r3(g.cvrmse)}
    we = df[(df.dow >= 5) & df.temp.notna() & ~((df.index >= F.COVID[0]) & (df.index <= F.COVID[1]))]
    gw = CP.fit(we.temp.to_numpy(), we.load.to_numpy(), "4P", year_dummies(we.index, sorted(we.index.year.unique())))
    out = {"n": int(len(wk)), "years": years, "best": best, "models": table,
           "best_ci": {"cp": q(boot[:, 0]), "slope_below": q(boot[:, 2]), "slope_above": q(boot[:, 3])},
           "scatter": {"T": np.round(T, 2).tolist(), "y": np.round(adj, 0).tolist()}, "curve": {"T": np.round(tg, 2).tolist(), "y": np.round(curve, 0).tolist()},
           "by_year": by_year, "weekend": {"cp": r1(gw.cps[0]), "slope_above": r1(gw.beta[2]), "cvrmse": r3(gw.cvrmse)},
           "year_effects": {str(yr): r1(v) for yr, v in zip(years[1:], f.beta[-Z.shape[1]:])}}
    print("changepoint", best, table[best], out["best_ci"])
    return out


def forecast_block(df):
    train, test = F.split(df)
    rng = np.random.default_rng(64)
    y = test.peak.to_numpy()
    mods = {"temp": F.PeakModel("peak", True).fit(train), "notemp": F.PeakModel("peak", False).fit(train)}
    rows, series = {}, {}

    def score(name, S, point):
        lo, hi = np.quantile(S, [0.05, 0.95], axis=1)
        rows[name] = {"mape": r3(100 * np.mean(np.abs(point - y) / y)), "rmse": r1(np.sqrt(np.mean((point - y) ** 2))),
                      "crps": r1(F.crps_ensemble(S, y).mean()), "cover90": r3(np.mean((y >= lo) & (y <= hi)))}
        return lo, hi

    p = mods["temp"].predict(test, df.peak)
    S = mods["temp"].samples(p, rng)
    lo, hi = score("Temperatura observada (oráculo)", S, p)
    series["oracle"] = {"p": np.round(p).tolist(), "lo": np.round(lo).tolist(), "hi": np.round(hi).tolist()}
    p = mods["notemp"].predict(test, df.peak)
    score("Sem temperatura", mods["notemp"].samples(p, rng), p)
    for sig in (1.0, 2.0):
        tf = test.temp.to_numpy() + np.random.default_rng(int(sig * 10)).normal(0, sig, len(test))
        p = mods["temp"].predict(test, df.peak, tf)
        score(f"Previsão de temperatura com erro de {sig:g} °C, valor direto", mods["temp"].samples(p, rng), p)
        S = mods["temp"].samples_uncertain_temp(test, df.peak, tf, sig, rng)
        lo, hi = score(f"Previsão de temperatura com erro de {sig:g} °C, incerteza propagada", S, S.mean(1))
        if sig == 1.0:
            series["prop1"] = {"p": np.round(S.mean(1)).tolist(), "lo": np.round(lo).tolist(), "hi": np.round(hi).tolist()}
    naive = df.peak.shift(7, freq="D").reindex(test.index).to_numpy()
    rows["Mesmo dia da semana anterior"] = {"mape": r3(100 * np.mean(np.abs(naive - y) / y)), "rmse": r1(np.sqrt(np.mean((naive - y) ** 2))), "crps": None, "cover90": None}
    m = mods["temp"]
    # when does the daily peak happen? month × hour frequency over 2019–2025
    hm = pd.crosstab(df.index.month, df.peak_hour)
    hm = hm.reindex(columns=range(24), fill_value=0)
    share_afternoon = {str(yr): r3(np.mean((g.peak_hour >= 12) & (g.peak_hour <= 16))) for yr, g in df.groupby(df.index.year)}
    out = {"train": [str(train.index[0].date()), str(train.index[-1].date())], "test": [str(test.index[0].date()), str(test.index[-1].date())],
           "n_train": int(len(train)), "n_test": int(len(test)), "Tb": r1(m.Tb), "slopes": [r1(m.beta[-2]), r1(m.beta[-1])], "phi": r3(m.phi),
           "metrics": rows, "dates": [str(d.date()) for d in test.index], "actual": np.round(y).tolist(), "temp": np.round(test.temp.to_numpy(), 1).tolist(),
           "series": series, "peak_hour_heatmap": hm.to_numpy().tolist(), "afternoon_share": share_afternoon,
           "peak_record": {"mw": r1(df.peak.max()), "date": str(df.peak.idxmax().date())}}
    print("forecast", rows)
    return out


def climate_block():
    w = E.inmet_daily(K.STATION)
    a = K.annual(w)
    trends = {c: K.mann_kendall(a[c].to_numpy(), a.index.to_numpy()) for c in ("tmean", "cdd", "hot_days")}
    wsp = E.inmet_daily("A701")
    asp = K.annual(wsp)
    trends_sp = {c: K.mann_kendall(asp[c].to_numpy(), asp.index.to_numpy()) for c in ("tmean", "cdd", "hot_days")}
    res, years, cdd, (T, G, idx) = K.run_years(w)
    # hottest week of the simulated complete years, for the chart
    Td = pd.Series(T, index=idx).resample("D").mean()
    Td = Td[Td.index.year.isin(years)]
    c = Td.rolling(7).mean().idxmax()
    sl = (idx > c - pd.Timedelta(days=7)) & (idx <= c)
    week = {"t": [str(t) for t in idx[sl][::2]], "T_out": np.round(T[sl][::2], 2).tolist(), "G": np.round(G[sl][::2], 1).tolist(), "Ti": {}}
    for name, b in K.SCENARIOS.items():
        Ti, _ = K.simulate(b, T, G, idx, cooling=False)
        week["Ti"][name] = np.round(Ti[sl][::2], 2).tolist()
    fit_r2 = {}
    for name, r in res.items():
        x = np.array([cdd[y] for y in years]); yv = np.array([r[y]["cooling_mwh"] for y in years])
        fit_r2[name] = r3(np.corrcoef(x, yv)[0, 1] ** 2)
    tab = lambda df_: {str(y): {k: r1(v) for k, v in row.items()} for y, row in df_.iterrows()}
    out = {"station": {"id": K.STATION, **E.manifest("inmet")["stations"][K.STATION]}, "flagged_rows": int(w.attrs["flagged"]),
           "coverage": {str(y): int(n) for y, n in w.groupby(w.index.year).tmean.count().items()},
           "annual": tab(a), "trends": {k: {kk: (r3(vv) if not isinstance(vv, list) else [r3(z) for z in vv]) for kk, vv in v.items()} for k, v in trends.items()},
           "annual_sp": tab(asp), "trends_sp": {k: {kk: (r3(vv) if not isinstance(vv, list) else [r3(z) for z in vv]) for kk, vv in v.items()} for k, v in trends_sp.items()},
           "sim_years": years, "scenarios": {n: {"label": b.label(), **{k: (r3(v) if isinstance(v, float) else v) for k, v in vars(b).items()}} for n, b in K.SCENARIOS.items()},
           "results": {n: {str(y): {k: r1(v) for k, v in vv.items()} for y, vv in r.items()} for n, r in res.items()},
           "cdd_sim": {str(y): r1(v) for y, v in cdd.items()}, "r2_cooling_cdd": fit_r2, "week": week}
    print("climate", out["trends"], {n: np.mean([v["cooling_mwh"] for v in r.values()]) for n, r in res.items()})
    return out


def main() -> None:
    df = E.daily_panel()
    h = E.ons_hourly("SE")
    out = {"schema": 1, "generated_by": "scripts/build_energy_data.py",
           "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__, "pandas": pd.__version__},
           "data": {"ons_hours": int(len(h)), "ons_span": [str(h.index[0]), str(h.index[-1])], "ons_gaps": int((h.index.to_series().diff() != pd.Timedelta(hours=1)).sum() - 1),
                    "temp_days": int(df.temp.notna().sum()), "temp_span": [str(df.temp.dropna().index[0].date()), str(df.temp.dropna().index[-1].date())],
                    "flagged": {s: int(E.inmet_daily(s).attrs["flagged"]) for s in ("A701", "A652", "A521", "A728")}},
           "changepoint": changepoint_block(df), "forecast": forecast_block(df), "climate": climate_block()}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":"), allow_nan=False), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
