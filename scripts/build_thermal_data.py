"""Build site/data/thermal.json (phase 5b: #029 furnace and machining, #070 bath and replenishment).

    python scripts/build_thermal_data.py

Physics with published material data and correlations; plant, furnace, lathe and bath are
hypothetical and the bath titrations are synthetic. Deterministic (fixed seeds).
"""
from __future__ import annotations

import json
import platform
import sys
from pathlib import Path

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from thermal import bath as B  # noqa: E402
from thermal import furnace as F  # noqa: E402
from thermal import machining as M  # noqa: E402

OUT = ROOT / "site" / "data" / "thermal.json"
KWH = 3.6e6
r1 = lambda x: round(float(x), 1)
r2 = lambda x: round(float(x), 2)
r3 = lambda x: round(float(x), 3)
r4 = lambda x: round(float(x), 4)


def furnace_block():
    f, c = F.Furnace(), F.Charge()
    walls = f.wall_losses()
    faces = [{"name": k, "area": r2(fc.area), "q": r1(v["q"]), "Ts": r1(v["Ts"]), "Q_kw": r3(v["Q"] / 1e3),
              "interfaces": [r1(t) for t in v["interfaces"]]} for (k, v), fc in zip(walls.items(), f.faces())]
    lay = [{"name": l.name, "L_mm": r1(l.L * 1000), "k_hot": r3(l.k(walls["Paredes laterais"]["interfaces"][i])),
            "k_cold": r3(l.k(walls["Paredes laterais"]["interfaces"][i + 1])), "T_hot": r1(walls["Paredes laterais"]["interfaces"][i]),
            "T_limit": r1(l.t_max)} for i, l in enumerate(f.lining)]
    d = f.door()
    run = F.heat_charge(f, c)
    E = {k: r3(v / KWH) for k, v in run["E"].items()}
    step = 6  # 60 s
    cyc = {k: [r1(x) for x in run[k][::step]] for k in ("T_core", "T_surf", "T_chamber")}
    cyc["t_min"] = [r1(x / 60) for x in run["t"][::step]]
    cyc["P_kw"] = [r1(x / 1e3) for x in run["P"][::step]]
    h_theory = c.mass * F.steel_enthalpy(run["T_mean_final"]) / KWH
    Tcp = np.arange(20, 1001, 5)
    mc = F.monte_carlo()
    hist, edges = np.histogram(mc["kwh_t"], bins=24)
    weekends = [{k: (r1(v) if isinstance(v, (float, np.floating)) else v) for k, v in F.weekend(f, D).items()} for D in (12, 24, 48, 64)]
    out = {
        "furnace": {"inner_m": [f.W, f.H, f.D], "T_set": f.T_set, "P_max_kw": f.P_max / 1e3, "door_m": [f.door_w, f.door_h],
                    "door_open_s": f.door_open_s, "wall_mm": r1(f.wall_L * 1000), "area_m2": r2(F.mean_wall_area(f)), "h_in": f.h_in},
        "charge": {"mass": c.mass, "diameter_mm": c.radius * 2000, "bar_length_m": r2(c.mass / (c.rho * np.pi * c.radius**2)),
                   "area_m2": r2(c.area), "eps": c.eps, "exposure": c.exposure, "T_core_target": c.T_core_target, "soak_min": c.soak_s / 60},
        "walls": faces, "layers": lay, "wall_total_kw": r3(f.wall_loss_W() / 1e3),
        "door": {"F12": r4(d["F12"]), "Fbar": r4(d["Fbar"]), "rad_kw": r2(d["rad"] / 1e3), "conv_kw": r2(d["conv"] / 1e3),
                 "conv_unlimited_kw": r1(d["conv_unlimited"] / 1e3), "T_gas": r1(d["T_gas"]), "V_m3s": r3(d["V"]), "purge_kwh": r3(d["purge_J"] / KWH)},
        "cycle": cyc, "energy_kwh": E, "kwh_per_t": r1(run["E"]["total"] / KWH / (c.mass / 1000)),
        "efficiency": r3(run["E"]["charge"] / run["E"]["total"]), "t_core_h": r3(run["t_core"] / 3600), "t_cycle_h": r3(run["t_cycle"] / 3600),
        "power_limited_min": r1(run["power_limited_s"] / 60), "T_mean_final": r1(run["T_mean_final"]),
        "enthalpy_check_kwh": r3(h_theory), "closure_pct": r3(100 * (run["E"]["total"] - sum(run["E"][k] for k in ("charge", "wall", "door_rad", "door_conv"))) / run["E"]["total"]),
        "cp_curve": {"T": Tcp.tolist(), "cp": [r1(x) for x in F.steel_cp(Tcp)]},
        "mc": {"n": len(mc["kwh_t"]), "p5": r1(np.percentile(mc["kwh_t"], 5)), "p50": r1(np.median(mc["kwh_t"])), "p95": r1(np.percentile(mc["kwh_t"], 95)),
               "tc_p5": r2(np.percentile(mc["t_cycle_h"], 5)), "tc_p95": r2(np.percentile(mc["t_cycle_h"], 95)),
               "hist": hist.tolist(), "edges": [r1(e) for e in edges], "srrc": dict(zip(mc["names"], [r3(b) for b in mc["srrc"]])), "r2": r3(mc["r2"])},
        "weekend": weekends,
    }
    print("furnace", out["kwh_per_t"], E, out["mc"]["p5"], out["mc"]["p95"], [(w["stop_h"], w["saving_kwh"]) for w in weekends])
    return out, run


def machining_block(run):
    kc, mc = np.array(M.CK45_ETH_KC), np.array(M.CK45_ETH_MC)
    h = np.round(np.linspace(0.05, 0.5, 46), 3)
    eth = np.array([M.specific_energy(h, a, b) for a, b in zip(kc, mc)])
    cat = M.specific_energy(h, 1500, 0.22)
    pas = M.turning_pass(80, 70, 1000, 200, 0.25)
    sweeps = {lab: M.removal_rate_sweep(a, b) for lab, a, b in (("catalog", 1500, 0.22), ("eth_median", float(np.median(kc)), float(np.median(mc))))}
    f, c = F.Furnace(), F.Charge()
    per_m_furnace = run["E"]["total"] / KWH / (c.mass / (c.rho * np.pi * c.radius**2))
    out = {"vdi3323": [{"name": n, "Rm": rm, "kc1": k, "mc": m} for n, rm, k, m in M.VDI3323],
           "eth": {"kc": M.CK45_ETH_KC, "mc": M.CK45_ETH_MC, "Rm": M.CK45_TENSILE_MPA},
           "u_curve": {"h": h.tolist(), "catalog": [r3(x) for x in cat], "eth_min": [r3(x) for x in eth.min(0)],
                       "eth_med": [r3(x) for x in np.median(eth, 0)], "eth_max": [r3(x) for x in eth.max(0)]},
           "pass": {k: (r3(v) if not isinstance(v, (bool, np.bool_)) else bool(v)) for k, v in pas.items()},
           "lathe": {"P0_kw": M.Lathe().P0 / 1e3, "eta": M.Lathe().eta, "P_max_kw": M.Lathe().P_spindle_max / 1e3},
           "sweep": {lab: {"mrr": [r1(x) for x in s["mrr"]], "e": [r3(x) for x in s["e"]], "idle": [r3(x) for x in s["share_idle"]],
                           "feasible": [bool(x) for x in s["feasible"]]} for lab, s in sweeps.items()},
           "per_m_bar": {"furnace_kwh": r3(per_m_furnace), "turning_kwh": r3(pas["E_J"] / KWH)}}
    print("machining", out["per_m_bar"], out["pass"]["e_J_mm3"])
    return out


def bath_block():
    b = B.Bath()
    truth = np.array([b.k_d, b.q, b.r])
    runs = {}
    for key, bands, wk in (("single", None, True), ("single_noweekend", None, False), ("two_bands", [(30, 26), (22, 18)], True)):
        sim = B.simulate(b, bands=bands)
        t, y = B.titrations(sim, weekend=wk)
        fit = B.fit(t, y, sim["prod"], sim["a"], b.C_set, b.V, sim["adds"])
        runs[key] = {"theta": [round(float(x), 6) for x in fit["theta"]], "se": [round(float(x), 6) for x in fit["se"]], "corr_qr": r3(fit["corr"][1, 2]),
                     "corr": [[r3(v) for v in row] for row in fit["corr"]], "rmse": r3(fit["rmse"]), "n": int(len(t))}
        if key == "single":
            show = {"h": list(range(0, len(sim["C"]))), "C": [r2(x) for x in sim["C"]], "prod": [int(x) for x in sim["prod"]],
                    "t_obs": [int(x) for x in t], "y_obs": [r2(x) for x in y], "adds": len(sim["adds"]),
                    "g_per_add": r1(np.mean([a for _, a in sim["adds"]]))}
            # total daily consumption is well determined even when q and r are not
            rng = np.random.default_rng(5)
            boot = []
            for i in range(200):
                yb = B.predict(fit["theta"], t, sim["prod"], sim["a"], b.C_set, b.V, sim["adds"]) + rng.normal(0, fit["rmse"], len(t))
                th = B.fit(t, yb, sim["prod"], sim["a"], b.C_set, b.V, sim["adds"], x0=fit["theta"])["theta"]
                boot.append((th, B.daily_demand(b, th, 7, np.random.default_rng(0), area_cv=1e-9).sum() / 5))
            th_b = np.array([x[0] for x in boot]); dem_b = np.array([x[1] for x in boot])
            true_week = B.daily_demand(b, truth, 7, np.random.default_rng(0), area_cv=1e-9).sum() / 5
            runs[key]["boot_q_ci"] = [r2(np.percentile(th_b[:, 1], 2.5)), r2(np.percentile(th_b[:, 1], 97.5))]
            runs[key]["boot_r_ci"] = [r3(np.percentile(th_b[:, 2], 2.5)), r3(np.percentile(th_b[:, 2], 97.5))]
            runs[key]["demand_ci"] = [r2(np.percentile(dem_b, 2.5)), r2(np.percentile(dem_b, 97.5))]
            runs[key]["demand_true"] = r2(true_week)
    rng = np.random.default_rng(1)
    dem = B.daily_demand(b, truth, 365 * 20, rng)
    best, tab = B.optimise(dem)
    K, h, p = 350.0, 0.06, 25000.0
    cost = lambda r: K * r["orders_per_year"] + h * 365 * r["mean_inventory"] + p * r["stockout_days_per_year"]
    pol = {}
    for key, lv in (("fixed_lead", False), ("random_lead", True)):
        c = B.classical(dem, lead_variance=lv)
        r = B.simulate_sS(dem, c["s"], c["S"])
        pol[key] = {"s": r1(c["s"]), "S": r1(c["S"]), "sdL": r2(c["sdL"]), **{k: r4(v) for k, v in r.items()}, "cost": r1(cost(r))}
    pol["simulated_optimum"] = {"s": r1(best[0]), "S": r1(best[1]), **{k: r4(v) for k, v in best[3].items()}, "cost": r1(best[2])}
    c = B.classical(dem)
    out = {"bath": {"V": b.V, "k_d": b.k_d, "q": b.q, "r": b.r, "area_rate": b.area_rate, "C_set": b.C_set, "C_min": b.C_min,
                    "concentrate": b.concentrate},
           "show": show, "fits": runs, "truth": truth.tolist(),
           "demand": {"mean": r2(dem.mean()), "sd": r2(dem.std(ddof=1)), "EL": c["EL"], "VL": r2(c["VL"]), "lead": {str(k): v for k, v in B.LEAD.items()}},
           "costs": {"K": K, "h": h, "p_stop": p}, "policies": pol,
           "grid": {"s": sorted({r1(x) for x in tab[:, 0]}), "S": sorted({r1(x) for x in tab[:, 1]}),
                    "rows": [[r1(a), r1(b_), r1(cst), r3(sv)] for a, b_, cst, sv, _ in tab]}}
    print("bath", runs, pol)
    return out


def main():
    fur, run = furnace_block()
    out = {"schema": 1, "generated_by": "scripts/build_thermal_data.py",
           "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
           "furnace": fur, "machining": machining_block(run), "bath": bath_block()}
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":"), allow_nan=False), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
