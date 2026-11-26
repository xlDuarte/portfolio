"""Chemical bath depletion and concentrate replenishment (#070). Hypothetical plant, synthetic data.

**Mass balance of the active chemical** in a bath of volume V (L), concentration C (g/L):

    V dC/dt = −k_d V C − q C − r a(t) + ṁ_add(t)

* k_d C: spontaneous decomposition, first order (1/h);
* q C: drag-out, the solution carried away on the parts (L/h), first order in C;
* r a(t): consumption by reaction per treated area (g/m²), zero order in C, a(t) in m²/h;
* ṁ_add: additions of concentrate when the titration falls below C_min, back to C_set.

With a constant a the solution between additions is C(t) = C* + (C₀ − C*) e^(−λt), with
λ = k_d + q/V and C* = −r a/(V λ). Production stops (a = q = 0) leave only k_d, which is what makes
k_d separable from drag-out: titrations taken on a weekend identify k_d on their own.

**Estimation.** Titrations with Gaussian error; the three rates are fitted by nonlinear least
squares on the exact piecewise solution, with standard errors from the Jacobian and a parametric
bootstrap. Fitting without weekend titrations shows the confounding.

**Replenishment.** Daily concentrate demand follows from the fitted rates and a random daily
production (gamma); an (s, S) policy with a fixed lead time is simulated over many years and
optimised on a grid for cost with a cycle-service constraint, then compared with the classical
normal approximation (s = μ_L + zσ_L, S = s + EOQ).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import least_squares
from scipy.stats import norm


@dataclass(frozen=True)
class Bath:
    V: float = 2000.0       # L
    k_d: float = 0.004      # 1/h
    q: float = 6.0          # L/h drag-out while producing
    r: float = 1.2          # g per m² treated
    area_rate: float = 60.0  # m²/h while producing
    C_set: float = 30.0     # g/L after an addition
    C_min: float = 26.0     # g/L, titration action limit
    concentrate: float = 400.0  # g of active per kg of concentrate


def schedule(hours, start_monday=True):
    """1 while producing (two shifts, 06–22 h, Monday–Friday), else 0."""
    t = np.arange(hours)
    dow = (t // 24) % 7
    hod = t % 24
    return ((dow < 5) & (hod >= 6) & (hod < 22)).astype(float)


def simulate(b: Bath, hours=24 * 28, seed=70, area_cv=0.15, bands=None):
    """Hour-step exact simulation with additions; returns hourly truth and the dosing log.

    ``bands`` optionally gives (C_set, C_min) per week, to run the bath at different concentrations.
    """
    rng = np.random.default_rng(seed)
    prod = schedule(hours)
    a = prod * b.area_rate * rng.gamma(1 / area_cv**2, area_cv**2, hours)  # m²/h, hour-to-hour noise
    C = b.C_set
    out, adds = np.empty(hours), []
    for h in range(hours):
        lam = b.k_d + prod[h] * b.q / b.V
        Cs = -b.r * a[h] / (b.V * lam)
        C = Cs + (C - Cs) * np.exp(-lam * 1.0)
        c_set, c_min = (b.C_set, b.C_min) if bands is None else bands[(h // 168) % len(bands)]
        if C < c_min:
            adds.append((h, (c_set - C) * b.V))   # g of active added
            C = c_set
        out[h] = C
    return {"C": out, "prod": prod, "a": a, "adds": adds}


def predict(theta, t_obs, prod, a, C0, V, adds):
    """Model concentration at observation hours for parameters (k_d, q, r)."""
    k_d, q, r = theta
    C, j, res = C0, 0, {}
    adds = dict(adds)
    targets = set(int(x) for x in t_obs)
    for h in range(int(max(t_obs)) + 1):
        lam = k_d + prod[h] * q / V
        Cs = -r * a[h] / (V * lam)
        C = Cs + (C - Cs) * np.exp(-lam)
        if h in adds:
            C = C + adds[h] / V
        if h in targets:
            res[h] = C
    return np.array([res[int(x)] for x in t_obs])


def fit(t_obs, y, prod, a, C0, V, adds, x0=(0.002, 3.0, 1.0)):
    f = lambda th: predict(th, t_obs, prod, a, C0, V, adds) - y
    sol = least_squares(f, x0, bounds=([0, 0, 0], [0.05, 50, 10]), x_scale=[0.001, 1, 0.1])
    J = sol.jac
    dof = max(len(y) - 3, 1)
    s2 = float(np.sum(sol.fun**2) / dof)
    try:
        cov = np.linalg.inv(J.T @ J) * s2
        se = np.sqrt(np.diag(cov))
        corr = cov / np.outer(se, se)
    except np.linalg.LinAlgError:
        se, corr = np.full(3, np.inf), np.full((3, 3), np.nan)
    return {"theta": sol.x, "se": se, "corr": corr, "rmse": float(np.sqrt(s2))}


def titrations(sim, every_h=4, weekend=True, sd=0.25, seed=71):
    rng = np.random.default_rng(seed)
    t = np.arange(every_h, len(sim["C"]), every_h)
    if not weekend:
        t = t[sim["prod"][t] > 0]
    return t, sim["C"][t] + rng.normal(0, sd, len(t))


# ------------------------------------------------------------------------------------------------
# replenishment of the concentrate
# ------------------------------------------------------------------------------------------------
def daily_demand(b: Bath, theta, days, rng, area_cv=0.25):
    """kg of concentrate per day: decomposition + drag-out + reaction at the average concentration."""
    k_d, q, r = theta
    Cbar = 0.5 * (b.C_set + b.C_min)
    dow = np.arange(days) % 7
    work = dow < 5
    m2 = np.where(work, b.area_rate * 16 * rng.gamma(1 / area_cv**2, area_cv**2, days), 0.0)
    g = k_d * b.V * Cbar * 24 + q * Cbar * 16 * work + r * m2
    return g / b.concentrate


LEAD = {4: 0.5, 5: 0.2, 7: 0.2, 10: 0.1}   # supplier lead time in days (hypothetical distribution)


def simulate_sS(demand, s, S, lead=LEAD, seed=7):
    """Daily review (s, S) with random lead times; returns service measures and cost drivers."""
    rng = np.random.default_rng(seed)
    days, probs = np.array(list(lead)), np.array(list(lead.values()))
    inv = S
    pipeline = {}
    orders = stockout_days = 0
    short = held = 0.0
    cycles = cycles_ok = 0
    cycle_short = False
    for d, D in enumerate(demand):
        inv += pipeline.pop(d, 0.0)
        if inv >= D:
            inv -= D
        else:
            short += D - inv
            inv = 0.0
            stockout_days += 1
            cycle_short = True
        held += inv
        pos = inv + sum(pipeline.values())
        if pos <= s:
            L = int(rng.choice(days, p=probs))
            pipeline[d + L] = pipeline.get(d + L, 0.0) + (S - pos)
            orders += 1
            cycles += 1
            cycles_ok += 0 if cycle_short else 1
            cycle_short = False
    n = len(demand)
    return {"orders_per_year": orders / n * 365, "mean_inventory": held / n, "fill_rate": 1 - short / np.sum(demand),
            "stockout_days_per_year": stockout_days / n * 365, "cycle_service": cycles_ok / max(cycles, 1)}


def optimise(demand, lead=LEAD, K=350.0, h=0.06, p_stop=25000.0, service=0.99, grid=None):
    """Cost per year = K·orders + h·365·mean inventory + p_stop·stockout days; subject to cycle service."""
    mu = demand.mean()
    grid = grid or (np.arange(0, 30 * mu, mu * 0.5), np.arange(mu * 2, 60 * mu, mu))
    best, table = None, []
    for s in grid[0]:
        for S in grid[1]:
            if S <= s:
                continue
            r = simulate_sS(demand, s, S, lead)
            cost = K * r["orders_per_year"] + h * 365 * r["mean_inventory"] + p_stop * r["stockout_days_per_year"]
            table.append((s, S, cost, r["cycle_service"], r["fill_rate"]))
            if r["cycle_service"] >= service and (best is None or cost < best[2]):
                best = (s, S, cost, r)
    return best, np.array(table)


def classical(demand, lead=LEAD, K=350.0, h=0.06, service=0.99, lead_variance=True):
    """Normal approximation of lead-time demand + EOQ.

    σ_L² = E[L]·σ_d² + μ_d²·Var[L] (random lead time, iid days); with lead_variance=False the
    second term is dropped, the common shortcut that treats the lead time as fixed.
    """
    mu, sd = demand.mean(), demand.std(ddof=1)
    days, probs = np.array(list(lead)), np.array(list(lead.values()))
    EL = float(days @ probs)
    VL = float((days - EL) ** 2 @ probs)
    muL = mu * EL
    sdL = np.sqrt(EL * sd**2 + (mu**2 * VL if lead_variance else 0.0))
    s = muL + norm.ppf(service) * sdL
    Q = np.sqrt(2 * K * mu * 365 / (h * 365))
    return {"s": s, "S": s + Q, "Q": Q, "muL": muL, "sdL": sdL, "EL": EL, "VL": VL}
