"""Build site/motorsport/data/benchmark-bahrain.json (phase 3, project #014).

    python scripts/build_benchmark_data.py

Real 2024 Bahrain GP laps (OpenF1): per-sector hierarchical Student-t models that separate driver
pace from compound, tyre age and race-lap trend, versus the naive benchmarks (median, best and
ideal lap). Deterministic (fixed seeds).
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

from race_strategy import benchmark as B  # noqa: E402
from race_strategy.data import lap_table, load  # noqa: E402
from race_strategy.pace import FIXED, ess, summary  # noqa: E402

OUT = ROOT / "site" / "motorsport" / "data" / "benchmark-bahrain.json"
r3 = lambda x: round(float(x), 3)


def q(x):
    return {"mean": r3(np.mean(x)), "q05": r3(np.quantile(x, 0.05)), "q95": r3(np.quantile(x, 0.95))}


def main() -> None:
    data = load()
    t = lap_table(data)
    c = t.subset(t.clean)
    S = B.sector_times(data, c)
    tt, SS, posts, lap = B.fit_sectors(c, S)
    D = lap.drivers
    team = {d: tm for d, tm in zip(tt.driver, tt.team)}
    sec = [B.benchmark(p) for p in posts]
    total = sum(sec)
    lapb = B.benchmark(lap)
    rp = B.rank_probabilities(total)
    raw = B.raw_benchmarks(tt, SS, data)
    order = np.argsort(total.mean(0))
    best = order[0]
    rows = []
    for j in order:
        d = D[j]
        gap = [s[:, j] - s[:, best] for s in sec]
        rows.append({"driver": d, "team": str(team[d]), "sectors": [q(s[:, j]) for s in sec], "lap": q(total[:, j]),
                     "lap_model": q(lapb[:, j]), "gap_to_best": [q(g) for g in gap], "gap_total": q(sum(gap)),
                     "p_fastest": r3(rp["p_fastest"][j]), "mean_rank": r3(rp["mean_rank"][j]),
                     "rank90": [int(rp["rank_q05"][j]), int(rp["rank_q95"][j])],
                     "raw": {k: (r3(v) if not isinstance(v, list) else [r3(x) for x in v]) for k, v in raw[d].items()}})
    corrected_rank = np.argsort(np.argsort(total.mean(0)))
    raw_med = np.array([raw[d]["median_lap"] for d in D])
    raw_best = np.array([raw[d]["best_lap"] for d in D])
    raw_ideal = np.array([raw[d]["ideal_lap"] for d in D])
    R = B.residuals(tt, SS, posts)
    w_ok = np.all(np.column_stack([p.lam_mean for p in posts]) > 0.5, axis=1)
    corr = {}
    for a, b in ((0, 1), (1, 2), (0, 2)):
        corr[f"{B.SECTORS[a]}-{B.SECTORS[b]}"] = {"all": {k: (v if isinstance(v, int) else r3(v) if not isinstance(v, list) else [r3(x) for x in v]) for k, v in B.corr_ci(R[:, a], R[:, b]).items()},
                                                    "clean_weights": {k: (v if isinstance(v, int) else r3(v) if not isinstance(v, list) else [r3(x) for x in v]) for k, v in B.corr_ci(R[:, a], R[:, b], w_ok).items()}}
    fixed = {}
    for k, p in enumerate(posts + [lap]):
        sm = summary(p)
        fixed[B.SECTORS[k] if k < 3 else "volta"] = {n: {"mean": r3(sm[n]["mean"]), "q05": r3(sm[n]["q05"]), "q95": r3(sm[n]["q95"])}
                                                  for n in FIXED[1:]} | {"sigma": r3(sm["sigma"]["mean"]), "nu_median": r3(np.median(p.nu))}
    diag = {"rhat_max": r3(max(B.rhat_max(p) for p in posts + [lap])),
            "ess_min_u": r3(min(ess(p.u[:, :, j]) for p in posts + [lap] for j in range(len(D)))),
            "chains": posts[0].meta["chains"], "iters": posts[0].meta["iters"], "burn": posts[0].meta["burn"]}
    m_sum, m_lap = total.mean(0), lapb.mean(0)
    out = {"schema": 1, "generated_by": "scripts/build_benchmark_data.py",
           "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
           "source": {"provider": "OpenF1", "session_key": data["session"]["session_key"] if isinstance(data.get("session"), dict) else None,
                      "laps_clean": int(len(tt)), "drivers": len(D), "a_ref": B.A_REF},
           "drivers": rows,
           "agreement": {"median_vs_corrected": B.rank_agreement(raw_med, m_sum), "best_vs_corrected": B.rank_agreement(raw_best, m_sum),
                         "ideal_vs_corrected": B.rank_agreement(raw_ideal, m_sum),
                         "rank_moves": int(np.sum(np.argsort(np.argsort(raw_med)) != corrected_rank))},
           "consistency": {"slope_sum_on_lap": r3(np.polyfit(m_lap, m_sum, 1)[0]), "corr": r3(np.corrcoef(m_lap, m_sum)[0, 1]),
                           "max_abs_diff_s": r3(np.abs(m_lap - m_sum).max())},
           "residual_corr": corr, "laps_full_weight": int(w_ok.sum()), "fixed": fixed, "diagnostics": diag}
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":"), allow_nan=False,
                              default=lambda o: o.item() if hasattr(o, "item") else str(o)), encoding="utf-8")
    for r in rows[:6]:
        print(r["driver"], r["lap"], r["p_fastest"], r["rank90"], [s["mean"] for s in r["sectors"]], r["raw"]["median_lap"])
    print(json.dumps({k: out[k] for k in ("agreement", "consistency", "residual_corr", "diagnostics")}, indent=1))
    print(json.dumps(fixed, indent=0)[:1500])
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
