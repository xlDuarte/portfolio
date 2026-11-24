"""Build site/motorsport/data/strategy-bayes.json (phase 2: pace, tyre physics, strategy).

    python scripts/build_strategy_data.py

Deterministic (fixed seeds). Steps: Bayesian pace model on every green-flag lap of the 2024
Bahrain GP, temporal hold-out validation against two baselines, physics split of the race-lap
trend, measured pit loss, Bayesian decision analysis of static plans, stochastic dynamic
programme with safety cars, tyre sliding energy and a two-node thermal model from the
calibrated lap simulation of phase 1. Also refreshes strategy-real.json for the existing tool.
"""
from __future__ import annotations

import json
import platform
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from race_strategy.data import RACE_LAPS, lap_table, load, pit_losses  # noqa: E402
from race_strategy.pace import FIXED, Design, crps_samples, decompose_trend, gibbs, summary  # noqa: E402
from race_strategy.strategy import (H, S, SHORT, Pace, equivalence_key, plan_matrix, plans, sdp,  # noqa: E402
                                    simulate_policy, static_under_sc)
from vehicle_dynamics import Car, MagicFormula, Track, simulate  # noqa: E402
from vehicle_dynamics.tyre_energy import ThermalParams, calibrate_convection, lap_energy, thermal_stint  # noqa: E402

DATA = ROOT / "site" / "motorsport" / "data"
OUT = DATA / "strategy-bayes.json"
TRAIN_LAST = 42                     # temporal hold-out: fit on laps ≤ 42, forecast laps 43–57
SC_RATES = (0.0, 0.01, 0.02, 0.035)  # probability per green lap that a safety car starts
SC_LAPS = 4
PIT_SC_RATIO = 0.5                   # hypothesis: pitting under SC costs half the green loss
FOCUS = "VER"
r3 = lambda x: round(float(x), 3)


def stat(a):
    a = np.asarray(a).reshape(-1)
    q = np.quantile(a, [0.05, 0.5, 0.95])
    return {"mean": r3(a.mean()), "q05": r3(q[0]), "q50": r3(q[1]), "q95": r3(q[2])}


def calibrated_car_and_track():
    d = json.loads((DATA / "lapsim-bahrain.json").read_text(encoding="utf-8"))
    spec = dict(d["car"])
    tyre = MagicFormula(**spec.pop("tyre"))
    car = Car(**spec, tyre=tyre)
    t = d["track"]
    tr = Track(*(np.array(t[k]) for k in ("s", "x", "y", "z", "kappa", "grade")), t["length_m"], {})
    return d, car, tr


def main() -> None:
    data = load()
    table = lap_table(data)
    clean = table.subset(table.clean)
    design = Design.of(clean)
    drivers = sorted(str(d) for d in set(clean.driver))
    rng = np.random.default_rng(57)
    LIKELIHOODS = {"normal": [1e6], "student-t": None}

    # ---------------------------------------------------------------- hold-out validation (both likelihoods)
    train = clean.subset(clean.lap <= TRAIN_LAST)
    test = clean.subset(clean.lap > TRAIN_LAST)
    dtr = Design.of(train, drivers)
    dte = Design.of(test, drivers)
    holdout = {}
    for name, grid in LIKELIHOODS.items():
        pt = gibbs(dtr, chains=2, iters=2500, burn=800, seed=7, nu_grid=grid)
        pred, _ = pt.predictive(dte.X, dte.drv_idx, dte.age, rng, n_draws=1600)
        lo50, hi50 = np.quantile(pred, [0.25, 0.75], axis=0)
        lo90, hi90 = np.quantile(pred, [0.05, 0.95], axis=0)
        med = np.median(pred, axis=0)
        holdout[name] = {"crps_s": r3(crps_samples(pred, dte.y).mean()), "cover50": r3(np.mean((dte.y >= lo50) & (dte.y <= hi50))),
                         "cover90": r3(np.mean((dte.y >= lo90) & (dte.y <= hi90))), "mae_s": r3(np.mean(np.abs(med - dte.y))),
                         "bias_s": r3(np.mean(dte.y - med))}
    chosen = min(holdout, key=lambda k_: holdout[k_]["crps_s"])

    # ---------------------------------------------------------------- full fits
    fits = {name: gibbs(design, chains=4, iters=3000, burn=1000, seed=2024, nu_grid=grid) for name, grid in LIKELIHOODS.items()}
    post = fits[chosen]
    summ = summary(post)
    B, U, V = post.flat("beta"), post.flat("u"), post.flat("v")
    # baseline 1: OLS with driver fixed effects, Gaussian predictive
    Zd = np.eye(len(drivers))[dtr.drv_idx]
    Xo = np.hstack([dtr.X, Zd[:, 1:]])
    bo, *_ = np.linalg.lstsq(Xo, dtr.y, rcond=None)
    so = float(np.std(dtr.y - Xo @ bo, ddof=Xo.shape[1]))
    Xo_te = np.hstack([dte.X, np.eye(len(drivers))[dte.drv_idx][:, 1:]])
    mo = Xo_te @ bo
    zs = rng.standard_normal((1600, len(mo)))
    crps_ols = crps_samples(mo[None, :] + so * zs, dte.y)
    cov_ols90 = float(np.mean(np.abs(dte.y - mo) <= 1.645 * so))
    # baseline 2: persistence — driver's median of the last 5 clean training laps
    last = {}
    for d in drivers:
        m = train.driver == d
        last[d] = float(np.median(train.time[m][np.argsort(train.lap[m])][-5:])) if m.any() else float(np.median(train.time))
    mp = np.array([last[d] for d in test.driver])
    sp = float(np.std(np.concatenate([train.time[train.driver == d] - last[d] for d in drivers])))
    crps_pers = crps_samples(mp[None, :] + sp * rng.standard_normal((1600, len(mp))), dte.y)
    validation = {
        "train_laps": int(len(train)), "test_laps": int(len(test)), "split_lap": TRAIN_LAST, "chosen": chosen,
        "bayes_normal": holdout["normal"], "bayes_t": holdout["student-t"],
        "ols": {"crps_s": r3(crps_ols.mean()), "cover90": r3(cov_ols90), "mae_s": r3(np.mean(np.abs(mo - dte.y))),
                "bias_s": r3(np.mean(dte.y - mo))},
        "persistence": {"crps_s": r3(crps_pers.mean()), "mae_s": r3(np.mean(np.abs(mp - dte.y)))},
    }
    robust = {name: {k_: {kk: r3(vv) for kk, vv in v_.items()} for k_, v_ in summary(f).items()} for name, f in fits.items()}

    # ---------------------------------------------------------------- physics split of the trend
    lapsim, car, track = calibrated_car_and_track()
    ds_dkg = lapsim["sensitivity"]["items"]["massa"]["s_per_10kg"] / 10.0
    trend = decompose_trend(B[:, 4], ds_dkg, 0.15 * ds_dkg, 1.84, 0.10, rng)
    trend["physics"] = {"s_per_kg": r3(ds_dkg), "s_per_kg_sd": r3(0.15 * ds_dkg), "burn_kg_per_lap": 1.84,
                        "burn_sd": 0.10}

    # ---------------------------------------------------------------- driver effects and degradation curves
    order = np.argsort(U.mean(axis=0))
    driver_rows = [{"driver": drivers[k], "u": stat(U[:, k]), "v": stat(V[:, k]),
                    "team": str(table.team[table.driver == drivers[k]][0])} for k in order]
    ages = np.arange(0, 36)
    curves = {}
    for name, c in (("SOFT", S), ("HARD", H)):
        delta = B[:, 1] if c == H else 0.0
        beta = B[:, 3] if c == H else B[:, 2]
        draws = (np.asarray(delta)[:, None] if c == H else 0.0) + beta[:, None] * ages[None, :]
        q = np.quantile(draws, [0.05, 0.5, 0.95], axis=0)
        curves[name] = {"age": ages.tolist(), "q05": np.round(q[0], 3).tolist(), "q50": np.round(q[1], 3).tolist(),
                        "q95": np.round(q[2], 3).tolist()}

    # ---------------------------------------------------------------- pit loss (measured)
    bm, um, vm = B.mean(axis=0), U.mean(axis=0), V.mean(axis=0)

    def mean_pace(d, n, comp, age):
        k = drivers.index(str(d))
        h = comp == "HARD"
        return bm[0] + bm[1] * h + (bm[3] if h else bm[2]) * age + bm[4] * (n - post.ref_lap) + um[k] + vm[k] * age

    stops = pit_losses(table, mean_pace)
    losses = np.array([s["loss_s"] for s in stops])
    normal = losses[losses < 40.0]
    boot = np.array([np.median(rng.choice(normal, normal.size)) for _ in range(4000)])
    pit = {"n": int(losses.size), "n_used": int(normal.size), "median_s": r3(np.median(normal)),
           "ci95_s": [r3(x) for x in np.quantile(boot, [0.025, 0.975])],
           "iqr_s": [r3(x) for x in np.quantile(normal, [0.25, 0.75])],
           "excluded": [s for s in stops if s["loss_s"] >= 40.0],
           "lane_median_s": r3(np.median([p["lane_duration"] for p in data["pit"] if p["lane_duration"]])),
           "losses_s": np.round(np.sort(losses), 2).tolist()}

    # ---------------------------------------------------------------- static plans: Bayesian decision analysis
    every = plans(RACE_LAPS, max_stops=3, min_stint=6)
    # Main analysis: start on the used soft set (age 3), as every front-runner did. The model excludes
    # lap 1, so it cannot see the launch and first-lap track position that motivate that choice; the
    # hard-start alternative is reported separately as a sensitivity, not as advice.
    allp = [pl for pl in every if pl.compounds[0] == S]
    hardp = [pl for pl in every if pl.compounds[0] == H]
    A, k = plan_matrix(allp, RACE_LAPS, start_age=3)
    kf = drivers.index(FOCUS)
    nd = 1200
    pick = rng.choice(len(B), size=nd, replace=False)
    theta = np.column_stack([B[pick, 1], B[pick, 2], B[pick, 3], V[pick, kf]])
    Ld = rng.choice(boot, size=nd)
    best = np.full(nd, np.inf)
    arg = np.zeros(nd, int)
    exp_cost = np.zeros(len(allp))
    for a0 in range(0, len(allp), 15000):
        cost = A[a0:a0 + 15000] @ theta.T + np.outer(k[a0:a0 + 15000], Ld)       # plans × draws
        exp_cost[a0:a0 + 15000] = cost.mean(axis=1)
        m = cost.min(axis=0)
        better = m < best
        arg[better] = cost.argmin(axis=0)[better] + a0
        best = np.minimum(best, m)
    order_ = np.argsort(exp_cost)
    top, seen = [], set()
    for j in order_:
        key_ = equivalence_key(allp[j], RACE_LAPS)
        if key_ in seen:
            continue
        seen.add(key_)
        top.append(j)
        if len(top) == 10:
            break
    top = np.array(top)
    # optimality is credited to the equivalence class (identical cost)
    cls = np.array([hash(equivalence_key(allp[j], RACE_LAPS)) for j in arg])
    rel = (A[top] @ theta.T + np.outer(k[top], Ld)) - best[None, :]                   # regret vs per-draw optimum
    fam = {}
    for j in arg:
        key = "–".join(SHORT[c] for c in allp[j].compounds)
        fam[key] = fam.get(key, 0) + 1
    stops2 = [allp[j].stops for j in arg if len(allp[j].stops) == 2]
    plan_rows = [{"label": allp[j].label, "compounds": "–".join(SHORT[c] for c in allp[j].compounds),
                  "stops": list(allp[j].stops), "expected_vs_best_s": r3(exp_cost[j] - exp_cost[top[0]]),
                  "regret": stat(rel[i]), "p_optimal": r3(np.mean(cls == hash(equivalence_key(allp[j], RACE_LAPS))))}
                 for i, j in enumerate(top)]

    # actual strategies of every finisher vs the optimum for that driver
    actual = []
    cache = {}
    st_by = {}
    for s in data["stints"]:
        st_by.setdefault(s["driver_number"], []).append(s)
    acr = {d["driver_number"]: d["name_acronym"] for d in data["drivers"]}
    for num, sts in st_by.items():
        sts = sorted(sts, key=lambda s: s["stint_number"])
        if sts[-1]["lap_end"] < RACE_LAPS - 2 or acr[num] not in drivers:
            continue
        comps = tuple(S if s["compound"] == "SOFT" else H for s in sts)
        stops_ = tuple(s["lap_end"] for s in sts[:-1])
        kd = drivers.index(acr[num])
        th = np.column_stack([B[pick, 1], B[pick, 2], B[pick, 3], V[pick, kd]])
        n_laps, a_start = sts[-1]["lap_end"], sts[0].get("tyre_age_at_start", 0)
        Aa, ka = plan_matrix([type(allp[0])(comps, stops_)], n_laps, start_age=a_start)
        own = (Aa @ th.T + np.outer(ka, Ld))[0]
        key_ = (n_laps, a_start)
        if key_ not in cache:
            pl_ = allp if n_laps == RACE_LAPS else [x for x in plans(n_laps, max_stops=3, min_stint=6) if x.compounds[0] == S]
            cache[key_] = plan_matrix(pl_, n_laps, start_age=a_start)
        Ab, kb = cache[key_]
        bestd = np.full(nd, np.inf)
        for a0 in range(0, len(Ab), 15000):
            bestd = np.minimum(bestd, (Ab[a0:a0 + 15000] @ th.T + np.outer(kb[a0:a0 + 15000], Ld)).min(axis=0))
        actual.append({"driver": acr[num], "plan": "–".join(SHORT[c] for c in comps) + " · " + "/".join(map(str, stops_)),
                       "regret": stat(own - bestd)})
    actual.sort(key=lambda r: r["regret"]["mean"])

    Ah, kh = plan_matrix(hardp, RACE_LAPS, start_age=3)
    hard_best = np.full(nd, np.inf)
    for a0 in range(0, len(hardp), 15000):
        hard_best = np.minimum(hard_best, (Ah[a0:a0 + 15000] @ theta.T + np.outer(kh[a0:a0 + 15000], Ld)).min(axis=0))
    decision_hard_start = stat(hard_best - best)            # negative = a new-hard start would be faster in the model
    decision = {"driver": FOCUS, "draws": nd, "plans_evaluated": len(allp), "top": plan_rows,
                "hard_start_vs_soft_start_s": decision_hard_start,
                "family_share": {k_: r3(v / nd) for k_, v in sorted(fam.items(), key=lambda kv: -kv[1])},
                "first_stop_two_stop": np.bincount([s[0] for s in stops2], minlength=RACE_LAPS).tolist() if stops2 else [],
                "second_stop_two_stop": np.bincount([s[1] for s in stops2], minlength=RACE_LAPS).tolist() if stops2 else [],
                "actual": actual,
                "draw_params": {"delta_h": np.round(theta[:400, 0], 4).tolist(), "beta_s": np.round(theta[:400, 1], 4).tolist(),
                                "beta_h": np.round(theta[:400, 2], 4).tolist(), "v": np.round(theta[:400, 3], 4).tolist(),
                                "pit_loss": np.round(Ld[:400], 3).tolist()}}

    # ---------------------------------------------------------------- stochastic DP with safety cars
    pm = Pace(float(bm[1]), float(bm[2]), float(bm[3]), float(vm[kf]))
    Lg = float(np.median(normal))
    Lsc = PIT_SC_RATIO * Lg
    best_static = allp[top[0]]
    sdp_rows = []
    policy_maps = {}
    for p_sc in SC_RATES:
        r_s = sdp(pm, Lg, Lsc, p_sc, SC_LAPS, RACE_LAPS, S, 3)
        r_h = sdp(pm, Lg, Lsc, p_sc, SC_LAPS, RACE_LAPS, H, 0)
        res, start_c, start_a = r_s, S, 3                         # same start rule as the static analysis
        mc = simulate_policy(pm, res.policy, Lg, Lsc, p_sc, np.random.default_rng(11), 3000, SC_LAPS, RACE_LAPS,
                             start_compound=start_c, start_age=start_a)
        st = static_under_sc(pm, best_static, Lg, Lsc, p_sc, np.random.default_rng(11), 3000, SC_LAPS, RACE_LAPS)
        sdp_rows.append({"p_sc": p_sc, "expected_sc_per_race": r3(p_sc * (RACE_LAPS - 1)), "sdp_expected_s": r3(res.expected),
                         "sdp_start": "D" if start_c == H else "M", "sdp_expected_start_soft_s": r3(r_s.expected),
                         "sdp_expected_start_hard_s": r3(r_h.expected),
                         "sdp_mc_mean_s": r3(mc.mean()), "sdp_mc_q": [r3(x) for x in np.quantile(mc, [0.05, 0.5, 0.95])],
                         "static_mc_mean_s": r3(st.mean()), "static_mc_q": [r3(x) for x in np.quantile(st, [0.05, 0.5, 0.95])],
                         "value_of_flexibility_s": r3(st.mean() - mc.mean())})
        if p_sc in (0.0, 0.02):
            # decisions on hard tyres with both compounds already used, and on the starting softs
            policy_maps[str(p_sc)] = {
                "hard_both_green": res.policy[1:, 0, H, :41, 3].T.tolist(),
                "hard_both_sc": res.policy[1:, SC_LAPS, H, :41, 3].T.tolist(),
                "soft_only_green": res.policy[1:, 0, S, :41, 1].T.tolist(),
                "soft_only_sc": res.policy[1:, SC_LAPS, S, :41, 1].T.tolist(),
            }

    # ---------------------------------------------------------------- tyre physics (#110 link)
    sim = simulate(car, track)
    en = lap_energy(car, sim, track.ds)
    w = data["weather"][0]
    tw = {"air": w["air_temperature"], "track": w["track_temperature"]}
    h1 = calibrate_convection(en["power_W"], en["fz"], sim.v, en["dt"], tw["air"], tw["track"])
    tp = replace(ThermalParams(), h1=h1)
    ts, tb, lm = thermal_stint(en["power_W"], en["fz"], sim.v, en["dt"], tw["air"], tw["track"], 25, tp)
    sens = lapsim["sensitivity"]["items"]
    dT_dlam = -(sens["aderência lateral λ_μy"]["s_per_pct"] + sens["aderência longitudinal λ_μx"]["s_per_pct"]) * 100
    e_total = float(en["slide_J"].sum())
    wear = {}
    for name, j in (("SOFT", 2), ("HARD", 3)):
        rate = B[:, j] / dT_dlam                                   # grip lost per lap (fraction)
        wear[name] = {"grip_loss_pct_per_lap": stat(rate * 100), "grip_loss_pct_per_MJ": stat(rate * 100 / (e_total / 1e6))}
    step = 4
    tyre_phys = {
        "slide_MJ": np.round(en["slide_J"] / 1e6, 3).tolist(), "roll_MJ": np.round(en["roll_J"] / 1e6, 3).tolist(),
        "rear_share": r3(en["slide_J"][2:].sum() / en["slide_J"].sum()),
        "max_slip_deg": np.round(np.degrees(en["alpha"].max(axis=1)), 2).tolist(),
        "max_kappa": np.round(en["kappa"].max(axis=1), 3).tolist(),
        "s": np.round(sim.s[::step], 1).tolist(),
        "power_kw_axle": [np.round((en["power_W"][0] + en["power_W"][1])[::step] / 1e3, 2).tolist(),
                          np.round((en["power_W"][2] + en["power_W"][3])[::step] / 1e3, 2).tolist()],
        "surface_last_lap": [np.round(ts[i, ::step], 1).tolist() for i in range(4)],
        "lap_means": [{"surface": np.round(x["surface"], 1).tolist(), "bulk": np.round(x["bulk"], 1).tolist()} for x in lm],
        "thermal_params": {k_: getattr(tp, k_) for k_ in tp.__dataclass_fields__},
        "h1_calibrated": r3(h1), "target_rear_bulk_c": 105.0, "weather_c": tw,
        "dT_dlambda_s": r3(dT_dlam), "wear": wear,
    }

    # ---------------------------------------------------------------- write
    out = {
        "schema": 1, "generated_by": "scripts/build_strategy_data.py",
        "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
        "source": {"provider": "OpenF1", "session_key": data["session"]["session_key"], "event": "GP do Bahrein 2024, corrida",
                   "race_laps": RACE_LAPS, "laps_total": int(len(table)), "laps_clean": int(len(clean)),
                   "filter": "sem volta 1, voltas de entrada e saída de box e voltas acima de 110 s"},
        "model": {"fixed": list(FIXED), "summary": {k_: {kk: r3(vv) for kk, vv in v_.items()} for k_, v_ in summ.items()},
                  "meta": post.meta, "ref_lap": post.ref_lap,
                  "likelihood": chosen, "both": robust,
                  "t_outlier_weights": {"share_below_0_5": r3(np.mean(fits["student-t"].lam_mean < 0.5))}},
        "validation": validation, "trend": trend, "drivers": driver_rows, "curves": curves, "pit": pit,
        "decision": decision, "sdp": {"rows": sdp_rows, "sc_laps": SC_LAPS, "pit_sc_ratio": PIT_SC_RATIO, "pit_green_s": r3(Lg),
                                      "best_static": best_static.label, "maps": policy_maps, "start": "macio usado (3 voltas)",
                                      "pace": {"delta_h": float(pm.delta_h), "beta_s": float(pm.beta_s), "beta_h": float(pm.beta_h),
                                               "v": float(pm.v_driver)},
                                      "static_plan": {"compounds": list(best_static.compounds), "stops": list(best_static.stops)}},
        "tyre": tyre_phys,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":"), default=lambda o: o.item()), encoding="utf-8")

    # refresh the coefficients of the existing deterministic tool with the posterior means
    sr = json.loads((DATA / "strategy-real.json").read_text(encoding="utf-8"))
    sr["coefficients"] = {"intercept": float(bm[0] - bm[4] * post.ref_lap), "hard_offset": float(bm[1]),
                          "soft_age": float(bm[2]), "hard_age": float(bm[3]), "lap_trend": float(bm[4])}
    sr["observed_laps_used"] = int(len(clean))
    sr["method"] = "Médias a posteriori do modelo bayesiano hierárquico (race_strategy/pace.py); ver strategy-bayes.json"
    sr["pit_loss_measured_s"] = r3(Lg)
    (DATA / "strategy-real.json").write_text(json.dumps(sr, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1024:.0f} KB)")
    print(json.dumps({"chosen": chosen, "validation": validation, "pit": {k_: pit[k_] for k_ in ("median_s", "ci95_s", "n_used")},
                      "top": plan_rows[:5], "family": decision["family_share"], "sdp": sdp_rows, "trend": trend,
                      "wear": wear, "rear_share": tyre_phys["rear_share"]}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
