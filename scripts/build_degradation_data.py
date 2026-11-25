"""Build site/data/degradation.json (phase 4b: projects #097, #036, #037).

    python scripts/fetch_hydraulic.py      # once: verified cache of the hydraulic-rig data
    python scripts/build_degradation_data.py

* #097 NASA C-MAPSS FD001 and FD003 (committed): health indicator, random-coefficient degradation
  model with importance-sampling posterior, RUL predictive distributions on the official test
  sets, ridge baseline, maintenance decision under a cost ratio, Weibull lifetimes.
* #036 / #037 ZeMA hydraulic rig: plateau flow, viscosity compensation, extrapolation to hot oil,
  pump-leakage classification under random and leave-one-temperature-regime-out validation,
  Arrhenius ageing from measured temperature.
Deterministic (fixed seeds).
"""
from __future__ import annotations

import json
import platform
import sys
from pathlib import Path

import numpy as np
import scipy
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bearings.learn import Softmax, balanced_accuracy  # noqa: E402
from degradation import cmapss as C  # noqa: E402
from degradation import hydraulics as H  # noqa: E402

OUT = ROOT / "site" / "data" / "degradation.json"
r3 = lambda x: round(float(x), 3)
CANDIDATES = [0.01, 0.02, 0.03, None]
HORIZON, COST_RATIO = 30, 10.0


def cmapss_block(fd: str) -> dict:
    tr, te, rul = C.load(fd)
    cv = C.cv_gamma(tr, CANDIDATES)
    best = min(cv, key=cv.get)
    m = C.DegradationModel.fit(tr, None if best == "aleatório" else best)
    ridge = C.ridge_rul(tr)
    rng = np.random.default_rng(97)
    rows, ess = [], []
    for i, k in enumerate(te.units):
        t, X = te.of(k)
        s, e = m.rul_samples(t, X, rng=rng, return_ess=True)
        ess.append(e)
        q = np.quantile(s, [0.05, 0.25, 0.5, 0.75, 0.95])
        rows.append({"unit": int(k), "cycles": int(t[-1]), "true": float(rul[i]), "q": [r3(v) for v in q],
                     "p_fail_h": r3(np.mean(s <= HORIZON)), "crps": r3(C.crps_samples(s, rul[i])), "ridge": r3(ridge(t, X))})
    true = np.array([r["true"] for r in rows]); med = np.array([r["q"][2] for r in rows]); rp = np.array([r["ridge"] for r in rows])
    q05 = np.array([r["q"][0] for r in rows]); q95 = np.array([r["q"][4] for r in rows])
    q25 = np.array([r["q"][1] for r in rows]); q75 = np.array([r["q"][3] for r in rows])
    rmse = lambda a, b: r3(np.sqrt(np.mean((a - b) ** 2)))
    bins = {}
    for lo, hi in ((0, 60), (60, 120), (120, 1000)):
        sel = (true >= lo) & (true < hi)
        bins[f"{lo}-{hi if hi < 1000 else '+'}"] = {"n": int(sel.sum()), "rmse_bayes": rmse(med[sel], true[sel]), "rmse_ridge": rmse(rp[sel], true[sel]),
                                                    "cover90": r3(np.mean((true[sel] >= q05[sel]) & (true[sel] <= q95[sel])))}
    # maintenance decision: intervene within the next HORIZON cycles if P(RUL ≤ H) ≥ c_p/c_f
    pf = np.array([r["p_fail_h"] for r in rows])
    fails = true <= HORIZON

    def cost(act):
        return {"interventions": int(act.sum()), "failures": int(np.sum(fails & ~act)),
                "cost": r3(act.sum() * 1.0 + np.sum(fails & ~act) * COST_RATIO)}
    decision = {"horizon": HORIZON, "cost_ratio": COST_RATIO, "threshold": r3(1 / COST_RATIO),
                "bayes": cost(pf >= 1 / COST_RATIO), "ridge": cost(rp <= HORIZON), "perfect": cost(fails),
                "never": cost(np.zeros_like(fails))}
    # training paths for the chart and three test engines with their posterior bands
    paths = []
    for k in tr.units[:25]:
        t, X = tr.of(k)
        paths.append({"t": t[::3].tolist(), "s": np.round(m.hi(X)[::3], 3).tolist()})
    examples = []
    for k in (te.units[np.argmin(true)], te.units[np.argsort(true)[len(true) // 2]], te.units[np.argmax(true)]):
        t, X = te.of(k)
        th, _ = m.posterior_draws(t, X, n=2000, rng=np.random.default_rng(int(k)))
        a, b, g = m._unpack(th)
        tg = np.arange(1, t[-1] + 260, 3.0)
        paths_post = a[:, None] + b[:, None] * np.expm1(g[:, None] * tg[None]) / g[:, None]
        examples.append({"unit": int(k), "true_rul": float(rul[list(te.units).index(k)]), "t_obs": t.tolist(), "s_obs": np.round(m.hi(X), 3).tolist(),
                         "t_grid": tg.tolist(), "band": [np.round(np.quantile(paths_post, qq, axis=0), 3).tolist() for qq in (0.05, 0.5, 0.95)]})
    life = np.array([tr.cycle[tr.unit == k].max() for k in tr.units])
    wb = C.weibull_mle(life)
    ks = stats.kstest(life, "weibull_min", args=(wb["shape"], 0, wb["scale"]))
    x = np.sort(life)
    wb_out = {k: (r3(v) if not isinstance(v, list) else [r3(z) for z in v]) for k, v in wb.items()}
    wb_out |= {"B10": r3(wb["scale"] * (-np.log(0.9)) ** (1 / wb["shape"])), "ks_p": r3(ks.pvalue), "n": int(len(life)),
               "lives": x.tolist(), "ecdf": [r3((i + 0.5) / len(x)) for i in range(len(x))]}
    out = {"cv_crps": {str(k): r3(v) for k, v in cv.items()}, "chosen": str(best),
           "model": {"mu0": [r3(v) for v in m.mu0], "sd0": [r3(v) for v in np.sqrt(np.diag(m.S0))], "sigma": r3(m.sigma),
                     "rho": r3(m.rho), "mD": r3(m.mD), "sD": r3(m.sD), "hi_sensors": list(C.SENSORS)},
           "metrics": {"rmse_bayes": rmse(med, true), "rmse_ridge": rmse(rp, true), "score_bayes": r3(C.nasa_score(med, true)),
                       "score_ridge": r3(C.nasa_score(rp, true)), "crps_bayes": r3(np.mean([r["crps"] for r in rows])),
                       "cover90": r3(np.mean((true >= q05) & (true <= q95))), "cover50": r3(np.mean((true >= q25) & (true <= q75))),
                       "width90": r3(np.mean(q95 - q05)), "ess_min": r3(min(ess)), "ess_median": r3(np.median(ess))},
           "bins": bins, "decision": decision, "units": rows, "train_paths": paths, "examples": examples, "weibull": wb_out,
           "n_train": int(len(tr.units)), "n_test": int(len(te.units))}
    print(fd, out["cv_crps"], out["metrics"], bins, decision)
    return out


def hydraulic_block() -> dict:
    D = H.load()
    prof = D["profile"]
    F, T = D["plateau"], D["TS1_mean"]
    y = prof[:, 2].astype(str)
    n = len(y)
    st = prof[:, 4] == 0
    # physics test: fit the healthy-pump model on the two cooler blocks with cooler oil, predict the hottest
    tr = st & (prof[:, 2] == 0) & (prof[:, 0] != 3)
    te = st & (prof[:, 2] == 0) & (prof[:, 0] == 3)
    comp = H.Compensation().fit(F[tr, 0], T[tr])
    lin = np.polyfit(T[tr], F[tr, 0], 1)
    extrap = {"T_train": [r3(T[tr].min()), r3(T[tr].max())], "T_test_mean": r3(T[te].mean()),
              "observed_mean": r3(F[te, 0].mean()), "observed_median": r3(np.median(F[te, 0])),
              "viscosity_model": r3(comp.expected(T[te]).mean()), "linear_in_T": r3(np.polyval(lin, T[te]).mean()),
              "Qth": r3(comp.Qth), "K": r3(comp.K)}
    # leakage paths are not purely turbulent: the fitted K grows with leakage
    k_by_leak = {}
    for leak in (0, 1, 2):
        s = st & (prof[:, 2] == leak) & (prof[:, 0] != 3)
        c = H.Compensation().fit(F[s, 0], T[s])
        k_by_leak[str(leak)] = r3(c.K)
    # scatter: flow at p_ref vs temperature, by leakage
    scatter = {str(k): {"T": np.round(T[st & (prof[:, 2] == k)][::3], 2).tolist(), "q": np.round(F[st & (prof[:, 2] == k), 0][::3], 3).tolist()} for k in (0, 1, 2)}
    tg = np.linspace(34, 58, 49)
    curve = {"T": tg.tolist(), "q": np.round(comp.expected(tg), 4).tolist()}
    # classification
    protocols = {}
    for proto in ("aleatório", "regime térmico novo"):
        if proto == "aleatório":
            te_mask = np.random.default_rng(36).random(n) < 0.3
            folds = [(~te_mask, te_mask)]
        else:
            folds = [(prof[:, 0] != c, prof[:, 0] == c) for c in (3, 20, 100)]
        res = {}
        for name in ("estatísticos", "físicos sem compensação", "físicos com compensação"):
            yt, yp, per_fold = [], [], []
            for trm, tem in folds:
                fs, _ = H.feature_sets(D, trm)
                X = H.impute(fs[name], trm)
                p = Softmax(1e-2).fit(X[trm], y[trm]).predict(X[tem])
                yp.append(p); yt.append(y[tem]); per_fold.append(r3(balanced_accuracy(y[tem], p)))
            res[name] = {"balanced": r3(balanced_accuracy(np.concatenate(yt), np.concatenate(yp))), "folds": per_fold}
        protocols[proto] = res
    fs, comp_all = H.feature_sets(D, np.ones(n, bool))
    de = fs["físicos com compensação"][:, 0]
    by_state = {str(c): {"T": r3(T[prof[:, 0] == c].mean()), "nu": r3(H.walther(T[prof[:, 0] == c].mean())),
                         "deficit": [r3(np.median(de[(prof[:, 0] == c) & (prof[:, 2] == k) & st])) for k in (0, 1, 2)],
                         "eta": [r3(np.median(F[(prof[:, 0] == c) & (prof[:, 2] == k), 2])) for k in (0, 1, 2)]} for c in (3, 20, 100)}
    # #037: oil ageing from measured temperature
    ea0 = H.ea_for_doubling()
    ageing = {}
    for c in (3, 20, 100):
        Tc = D["TS1"][prof[:, 0] == c].ravel()
        ageing[str(c)] = {"T_mean": r3(Tc.mean()), "T_p95": r3(np.percentile(Tc, 95)), "nu_mean": r3(H.walther(Tc).mean()),
                          **{f"factor_{round(ea / 1000)}": r3(H.arrhenius_factor(Tc, Ea=ea).mean()) for ea in (50e3, ea0, 80e3)}}
    tv = np.linspace(20, 90, 71)
    out = {"cycles": int(n), "labels": {lab: {str(v): int(c) for v, c in zip(*np.unique(prof[:, j], return_counts=True))} for j, lab in enumerate(H.LABELS)},
           "extrapolation": extrap, "K_by_leak": k_by_leak, "scatter": scatter, "curve": curve, "protocols": protocols, "by_cooler": by_state,
           "compensation_all": {"Qth": r3(comp_all.Qth), "K": r3(comp_all.K), "resid_sd": r3(comp_all.resid_sd)},
           "ageing": ageing, "ea_doubling_kj": r3(ea0 / 1000), "viscosity_curve": {"T": tv.tolist(), "nu": np.round(H.walther(tv), 3).tolist()},
           "oil": {"nu40": H.NU40, "nu100": H.NU100}}
    print("hydraulic", extrap, k_by_leak, protocols, by_state, ageing)
    return out


def main() -> None:
    out = {"schema": 1, "generated_by": "scripts/build_degradation_data.py",
           "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
           "cmapss": {fd: cmapss_block(fd) for fd in ("FD001", "FD003")}, "hydraulic": hydraulic_block()}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":"), allow_nan=False), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
