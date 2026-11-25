"""Sector-level lap benchmark of the 2024 Bahrain GP corrected for tyre, compound and fuel (project #014).

Raw lap rankings confound driver pace with conditions: a driver who ran more laps on fresh softs
or late in the race (less fuel, rubbered-in track) looks faster than one who did not. Here each of
the three official sectors gets the hierarchical model of :mod:`race_strategy.pace`

    t_ik = β₀ᵏ + β_Hᵏ H_i + β_Sᵏ a_i(1−H_i) + β_Hdᵏ a_i H_i + γᵏ(n_i − 30) + u_dᵏ + v_dᵏ a_i + ε_ik

with Student-t errors, so traffic-affected laps are down-weighted rather than deleted. The
benchmark of driver d in sector k is the posterior of the conditional pace at a common reference
(hard tyre, age a_ref, race lap 30), relative to the field: Δ_dᵏ = u_dᵏ + v_dᵏ a_ref − mean_d(·).
The lap benchmark is Σ_k Δ_dᵏ. Sectors are fitted separately; the posterior of the sum treats
the three posteriors as independent, which the residual correlation below shows is approximately
but not exactly true (positive correlation → the sum's interval is slightly too narrow).
"""
from __future__ import annotations

from dataclasses import replace

import numpy as np
from scipy import stats

from .data import LapTable
from .pace import Design, gibbs, split_rhat

SECTORS = ("S1", "S2", "S3")
A_REF = 10                                    # reference tyre age, laps (hard compound)


def sector_times(data: dict, t: LapTable) -> np.ndarray:
    """(n, 3) sector times aligned with the rows of ``t``; NaN where OpenF1 has no sector."""
    acr = {d["driver_number"]: d["name_acronym"] for d in data["drivers"]}
    key = {(acr[l["driver_number"]], l["lap_number"]): l for l in data["laps"]}
    out = np.full((len(t), 3), np.nan)
    for i, (d, n) in enumerate(zip(t.driver, t.lap)):
        lap = key.get((d, int(n)))
        if lap:
            out[i] = [lap.get(f"duration_sector_{k}") or np.nan for k in (1, 2, 3)]
    return out


def fit_sectors(t: LapTable, S: np.ndarray, chains: int = 4, iters: int = 3000, burn: int = 1000, seed: int = 14):
    """One Student-t hierarchical model per sector (rows with all three sectors only)."""
    ok = np.all(np.isfinite(S), axis=1)
    t, S = t.subset(ok), S[ok]
    base = Design.of(t)
    posts = []
    for k in range(3):
        y = S[:, k]
        d = replace(base, y=y)
        posts.append(gibbs(d, chains, iters, burn, seed + 11 * k,
                           prior_mean=[float(np.median(y)), 0.0, 0.0, 0.0, 0.0],
                           prior_sd=[3.0, 0.5, 0.2, 0.2, 0.1], A_u=0.5, A_v=0.02))
    lap = gibbs(base, chains, iters, burn, seed + 101)          # whole-lap model, for consistency
    return t, S, posts, lap


def benchmark(post, a_ref: int = A_REF) -> np.ndarray:
    """Draws (chains·draws, D) of each driver's pace relative to the field mean at the reference."""
    u, v = post.flat("u"), post.flat("v")
    x = u + v * a_ref
    return x - x.mean(axis=1, keepdims=True)


def residuals(t: LapTable, S: np.ndarray, posts) -> np.ndarray:
    """Posterior-mean residuals (n, 3) of each sector model."""
    X = Design.of(t).X
    idx = Design.of(t).drv_idx
    R = np.empty_like(S)
    for k, p in enumerate(posts):
        b, u, v = p.flat("beta").mean(0), p.flat("u").mean(0), p.flat("v").mean(0)
        R[:, k] = S[:, k] - (X @ b + u[idx] + v[idx] * t.age)
    return R


def corr_ci(x, y, robust_w=None):
    """Pearson correlation with a Fisher-z 95 % interval; ``robust_w`` restricts to weighted laps."""
    if robust_w is not None:
        m = robust_w
        x, y = x[m], y[m]
    r = float(np.corrcoef(x, y)[0, 1])
    z, se = np.arctanh(r), 1 / np.sqrt(len(x) - 3)
    return {"r": r, "ci95": [float(np.tanh(z - 1.96 * se)), float(np.tanh(z + 1.96 * se))], "n": int(len(x))}


def rank_probabilities(total: np.ndarray):
    """P(rank = 1), expected rank and 90 % rank interval per driver from benchmark draws."""
    ranks = np.argsort(np.argsort(total, axis=1), axis=1) + 1         # 1 = fastest (most negative)
    return {"p_fastest": (ranks == 1).mean(0), "mean_rank": ranks.mean(0),
            "rank_q05": np.quantile(ranks, 0.05, axis=0), "rank_q95": np.quantile(ranks, 0.95, axis=0)}


def raw_benchmarks(t: LapTable, S: np.ndarray, data: dict) -> dict:
    """Naive per-driver numbers: median clean lap, best lap, ideal lap (sum of best sectors)."""
    acr = {d["driver_number"]: d["name_acronym"] for d in data["drivers"]}
    allsec = {}
    for l in data["laps"]:
        s = [l.get(f"duration_sector_{k}") for k in (1, 2, 3)]
        if all(s) and not l.get("is_pit_out_lap") and l["lap_number"] > 1:
            allsec.setdefault(acr[l["driver_number"]], []).append(s)
    out = {}
    for d in sorted(set(t.driver)):
        m = t.driver == d
        sec = np.array(allsec.get(d, [[np.nan] * 3]))
        out[d] = {"median_lap": float(np.median(t.time[m])), "best_lap": float(t.time[m].min()),
                  "ideal_lap": float(np.nansum(np.nanmin(sec, axis=0))), "best_sectors": np.nanmin(sec, axis=0).tolist(),
                  "laps": int(m.sum()), "soft_share": float(np.mean(t.compound[m] == "SOFT")), "mean_age": float(t.age[m].mean())}
    return out


def rank_agreement(a, b) -> dict:
    tau = stats.kendalltau(a, b)
    rho = stats.spearmanr(a, b)
    return {"kendall_tau": float(tau.statistic), "kendall_p": float(tau.pvalue), "spearman_rho": float(rho.statistic)}


def rhat_max(post) -> float:
    return float(max(split_rhat(post.u[:, :, j]) for j in range(post.u.shape[2])))
