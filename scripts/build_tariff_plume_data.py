"""Build site/data/tariff_plume.json (phase 5b, part 2: #090 tariff dispatch, #069 Gaussian plume).

    python scripts/build_tariff_plume_data.py

Real data: 15-minute load of a steel plant (UCI 851), ANEEL tariffs of EDP SP (REH 3.541/2025) and
hourly INMET weather at Taubaté (A728, 2022–2025). Hypothetical: the plant's connection to EDP SP and
the stack. Deterministic.
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

from energy.data import holidays  # noqa: E402
from thermal import plume as P  # noqa: E402
from thermal import tariff as T  # noqa: E402

OUT = ROOT / "site" / "data" / "tariff_plume.json"
r1 = lambda x: round(float(x), 1)
r2 = lambda x: round(float(x), 2)
r3 = lambda x: round(float(x), 3)


def tariff_block():
    L = T.load_steel()
    h = holidays([2018])
    hol = pd.to_datetime(h.date[h.kind == "feriado"])
    pk = T.peak_mask(L.index, holidays=hol)
    tf = T.tariffs()
    base = {}
    for name, t in tf.items():
        b = T.best_contract(L, pk, t)
        bill = T.bill(L, pk, t, b["Dc_p"], b["Dc_fp"])
        base[name] = {"Dc_p": b["Dc_p"], "Dc_fp": b["Dc_fp"], "annual": r1(b["annual"]),
                      "energy": r1(bill.energy.sum()), "demand": r1(bill.demand.sum()), "over": r1(bill.over.sum()),
                      "monthly": [{"m": r.month, "energy": r1(r.energy), "demand": r1(r.demand + r.over), "Dmax_p": r1(r.Dmax_p), "Dmax_fp": r1(r.Dmax_fp)} for r in bill.itertuples()],
                      "contract_curve": {"Dc": [r1(x) for x in b["grid"]], "annual": [r1(x) for x in b["costs"]]}}
    # alternative peak window (sensitivity of the secondary source)
    pk18 = T.peak_mask(L.index, start="18:00", holidays=hol)
    alt = {name: r1(T.best_contract(L, pk18, t)["annual"]) for name, t in tf.items()}
    # shifting sweep
    sweep = {name: [] for name in tf}
    alphas = [0.0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5]
    shifted_profile = None
    for a in alphas:
        for name, t in tf.items():
            if a == 0:
                sweep[name].append({"alpha": 0.0, "annual": base[name]["annual"], "moved_mwh": 0.0})
                continue
            S, moved = T.shift_year(L, pk, t, a)
            b = T.best_contract(S, pk, t)
            sweep[name].append({"alpha": a, "annual": r1(b["annual"]), "moved_mwh": r2(moved), "Dc_p": b["Dc_p"], "Dc_fp": b["Dc_fp"]})
            if name == "Verde" and a == 0.3:
                shifted_profile = S
    # average working-day profile, before and after (Verde, α = 0.3)
    wd = (L.index.day_of_week < 5) & ~pd.Index(L.index.normalize()).isin(hol)
    tod = (L.index.hour * 60 + L.index.minute)[wd]
    prof = pd.Series(L.to_numpy()[wd]).groupby(tod).mean()
    prof_s = pd.Series(shifted_profile.to_numpy()[wd]).groupby(tod).mean()
    weekly = pd.Series(L.to_numpy()).groupby(L.index.day_of_week).mean()
    # break-even hours of peak use between Verde and Azul (energy-vs-demand trade-off in the peak)
    v, a = tf["Verde"], tf["Azul"]
    be_h = (a.D_p) / ((v.E_p - a.E_p) / 1000)
    peak_h_month = float(pk.sum() * T.DT_H / 12)
    month_peak_use = []
    for m, g in pd.DataFrame({"kW": L.to_numpy(), "pk": pk}, index=L.index).groupby(L.index.to_period("M")):
        Ep = g.kW[g.pk].sum() * T.DT_H
        Dm = g.kW[g.pk].max()
        month_peak_use.append(Ep / Dm)
    fb = T.fiob()
    out = {"tariffs": {n: {"D_p": t.D_p, "D_fp": t.D_fp, "E_p": r2(t.E_p), "E_fp": r2(t.E_fp), "parts": t.parts} for n, t in tf.items()},
           "fiob": {f"{k[0]} {k[1]}": r3(v_) for k, v_ in fb.items()},
           "load": {"n": int(len(L)), "max_kw": r1(L.max()), "mean_kw": r1(L.mean()), "energy_mwh": r1(L.sum() * T.DT_H / 1000),
                    "peak_share": r3(L[pk].sum() / L.sum()), "peak_hours_share": r3(pk.mean()), "load_factor": r3(L.mean() / L.max()),
                    "profile_min": [int(x) for x in prof.index], "profile": [r1(x) for x in prof], "profile_shifted": [r1(x) for x in prof_s],
                    "weekday_mean": [r1(x) for x in weekly]},
           "base": base, "alt_peak_18_21": alt, "sweep": sweep,
           "breakeven": {"hours": r1(be_h), "peak_hours_month": r1(peak_h_month), "plant_hours": [r1(x) for x in month_peak_use]},
           "rules": {"peak": "17:30–20:30, dias úteis", "tolerance": 0.05, "penalty": 2}}
    print("tariff", {n: base[n]["annual"] for n in base}, alt, sweep["Verde"][-1], be_h)
    return out


def plume_block():
    met, head = P.load_taubate()
    lat = float(head["LATITUDE"].replace(",", "."))
    lon = float(head["LONGITUDE"].replace(",", "."))
    m, dropped = P.prepare(met, lat, lon)
    st = P.Stack()
    xs = np.geomspace(100, 10000, 40)
    dirs = np.arange(0, 360, 10.0)
    res = {}
    for night in ("overcast", "clear"):
        cls = P.stability(m.ws, m.rad, m.day, night)
        C, H = P.ground_conc(st, m, cls, xs, dirs)
        ann = C.mean(0)
        day = m.index.floor("D")
        hours_per_day = pd.Series(1, index=m.index).groupby(day).sum()
        full = hours_per_day[hours_per_day >= 18].index           # 24-h means need ≥ 18 valid hours (75 %)
        D = pd.DataFrame(C.reshape(len(m), -1)).groupby(day.to_numpy()).mean()
        D = D.loc[D.index.isin(full)].to_numpy()
        mx24 = D.max(0).reshape(len(dirs), len(xs))
        i = np.unravel_index(ann.argmax(), ann.shape)
        j = np.unravel_index(mx24.argmax(), mx24.shape)
        p98 = np.percentile(D, 98, axis=0).reshape(len(dirs), len(xs))
        res[night] = {"classes": {k: r3(v) for k, v in pd.Series(cls).value_counts(normalize=True).sort_index().items()},
                      "annual_max": r3(ann.max()), "annual_at": [r1(dirs[i[0]]), r1(xs[i[1]])],
                      "max24": r2(mx24.max()), "max24_at": [r1(dirs[j[0]]), r1(xs[j[1]])], "p98_24_max": r2(p98.max()),
                      "annual": [[r3(v) for v in row] for row in ann], "days": int(D.shape[0]),
                      "H_median": r1(np.median(H)), "H_p10": r1(np.percentile(H, 10))}
    # wind rose: 16 sectors × speed bins (from)
    sec = ((m.wd + 11.25) % 360 // 22.5).astype(int)
    bins = [0, 1, 2, 3, 5, 100]
    sp = np.digitize(m.ws, bins[1:-1])
    rose = np.zeros((16, len(bins) - 1))
    for a_, b_ in zip(sec, sp):
        rose[a_, b_] += 1
    rose /= rose.sum()
    cl = {}
    for k in range(6):
        c, Hh, F = P.centerline(st, 2.0, k, 20.0, xs)
        cl["ABCDEF"[k]] = {"c": [r3(v) for v in c], "H": r1(Hh)}
    WHO = {"24h": 45.0, "annual": 15.0}
    q24 = WHO["24h"] / max(res["overcast"]["max24"], res["clear"]["max24"])
    qan = WHO["annual"] / max(res["overcast"]["annual_max"], res["clear"]["annual_max"])
    out = {"station": {"id": "A728", "lat": lat, "lon": lon, "elev": head.get("ALTITUDE")}, "hours": int(len(met)), "valid": int(len(m)),
           "dropped": dropped, "calm_share": r3((m.ws < 1).mean()), "ws_mean": r2(m.ws.mean()), "day_share": r3(m.day.mean()),
           "years": sorted({int(y) for y in m.index.year}),
           "stack": {"h": st.h, "d": st.d, "v": st.v, "Ts": st.Ts, "Q": st.Q},
           "xs": [r1(x) for x in xs], "dirs": dirs.tolist(), "rose": [[r3(v) for v in row] for row in rose], "rose_bins": bins[:-1],
           "centerline": cl, "results": res, "who": WHO, "q_allow": {"by_24h": r2(q24), "by_annual": r2(qan), "governing": r2(min(q24, qan))}}
    print("plume", {k: (v["annual_max"], v["max24"], v["annual_at"], v["max24_at"]) for k, v in res.items()}, out["q_allow"])
    return out


def main():
    out = {"schema": 1, "generated_by": "scripts/build_tariff_plume_data.py",
           "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__, "pandas": pd.__version__},
           "tariff": tariff_block(), "plume": plume_block()}
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":"), allow_nan=False), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
