"""Pit-stop strategy: static plans under parameter uncertainty and a stochastic dynamic programme
with safety-car risk.

Lap-time model used here (all terms that differ between strategies):

    lap cost = δ_c + (β_c + v_d)·a          on green-flag laps (δ_S = 0, δ_H = β_H)
    pit cost = L_g on green, L_sc under safety car (both from data or hypothesis, see below)

The intercept, driver offset and race-lap trend are identical for every plan of the same driver,
so they cancel when plans are compared and are left out. Under the safety car every car laps at
the same slow pace, so tyre age does not change the lap cost on those laps.

Rules: a dry race must use at least two different compounds (FIA Sporting Regulations, art. 30.5).
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

import numpy as np

S, H = 0, 1
NAMES = {S: "SOFT", H: "HARD"}
SHORT = {S: "M", H: "D"}            # Macio / Duro, as shown on the site


@dataclass(frozen=True)
class Pace:
    delta_h: float                  # s, hard minus soft at equal age
    beta_s: float                   # s/lap, soft degradation
    beta_h: float                   # s/lap, hard degradation
    v_driver: float = 0.0           # s/lap, driver-specific extra degradation

    def lap(self, compound, age):
        b = np.where(compound == H, self.beta_h, self.beta_s) + self.v_driver
        return np.where(compound == H, self.delta_h, 0.0) + b * age


def stint_cost(p: Pace, compound: int, start_age: int, n: int) -> float:
    """Σ over n laps of δ_c + β·a with a = start_age … start_age + n − 1 (closed form)."""
    b = (p.beta_h if compound == H else p.beta_s) + p.v_driver
    d = p.delta_h if compound == H else 0.0
    return n * d + b * (n * start_age + n * (n - 1) / 2.0)


@dataclass(frozen=True)
class Plan:
    compounds: tuple
    stops: tuple                    # laps at the end of which the car pits

    @property
    def label(self) -> str:
        return "–".join(SHORT[c] for c in self.compounds) + " · " + ("/".join(str(s) for s in self.stops) or "sem parada")


def equivalence_key(plan: Plan, race_laps: int = 57):
    """Plans with the same first stint and the same multiset of later stints cost the same in this model."""
    bounds = (0,) + plan.stops + (race_laps,)
    stints = [(c, bounds[i + 1] - bounds[i]) for i, c in enumerate(plan.compounds)]
    return (stints[0], tuple(sorted(stints[1:])))


def plans(race_laps: int = 57, max_stops: int = 3, min_stint: int = 5):
    """All legal plans (≥ 2 compounds) with stints of at least ``min_stint`` laps."""
    out = []
    for k in range(1, max_stops + 1):
        for seq in np.ndindex(*([2] * (k + 1))):
            if len(set(seq)) < 2:
                continue
            for stops in combinations(range(min_stint, race_laps - min_stint + 1), k):
                lens = np.diff((0,) + stops + (race_laps,))
                if lens.min() < min_stint:
                    continue
                out.append(Plan(tuple(seq), stops))
    return out


def plan_cost(p: Pace, plan: Plan, pit_loss: float, race_laps: int = 57, start_age: int = 3) -> float:
    """``start_age`` is the age of the soft set used in qualifying; a car starting on hards uses a new set."""
    bounds = (0,) + plan.stops + (race_laps,)
    total = 0.0
    for i, c in enumerate(plan.compounds):
        n = bounds[i + 1] - bounds[i]
        total += stint_cost(p, c, start_age if (i == 0 and c == S) else 0, n)
    return total + pit_loss * len(plan.stops)


def plan_matrix(plans_, race_laps: int = 57, start_age: int = 3):
    """Sufficient statistics per plan so that cost = A·[δ_H, β_S, β_H, v] + k·L (vectorised over draws).

    ``start_age`` applies to a soft starting set (the qualifying tyre); a hard start is a new set."""
    A = np.zeros((len(plans_), 4))
    k = np.zeros(len(plans_))
    for j, pl in enumerate(plans_):
        bounds = (0,) + pl.stops + (race_laps,)
        for i, c in enumerate(pl.compounds):
            n = bounds[i + 1] - bounds[i]
            a0 = start_age if (i == 0 and c == S) else 0
            ages = n * a0 + n * (n - 1) / 2.0
            if c == H:
                A[j, 0] += n
                A[j, 2] += ages
            else:
                A[j, 1] += ages
            A[j, 3] += ages
        k[j] = len(pl.stops)
    return A, k


# ------------------------------------------------------------------------------------------------
# Stochastic dynamic programme with safety cars
# ------------------------------------------------------------------------------------------------
@dataclass
class SDPResult:
    expected: float                 # expected strategy-dependent time (s) from the start
    policy: np.ndarray              # [lap, sc laps remaining, compound, age, mask] → −1 stay, 0 pit soft, 1 pit hard
    value: np.ndarray

    @property
    def policy_green(self):
        return self.policy[:, 0]


def sdp(p: Pace, pit_green: float, pit_sc: float, p_sc: float, sc_laps: int = 4, race_laps: int = 57,
        start_compound: int = S, start_age: int = 3, max_age: int = 60) -> SDPResult:
    """Bellman recursion over (lap, compound, age, compounds-used mask, safety-car laps remaining).

    At the end of each lap the team may pit for either compound. A safety car starts on the next lap
    with probability p_sc per green lap and lasts ``sc_laps`` laps. Finishing without two compounds
    used is infeasible (infinite cost). Expected cost is minimised (risk-neutral).
    """
    A = max_age + 1
    INF = 1e9
    # V[s_rem, compound, age, mask] at the start of lap n (iterate backwards)
    V = np.full((sc_laps + 1, 2, A, 4), INF)
    V[:, :, :, 3] = 0.0                                 # after the last lap: fine only if both used
    pol = np.full((race_laps + 1, sc_laps + 1, 2, A, 4), -1, np.int8)
    ages = np.arange(A)
    for n in range(race_laps, 0, -1):
        Vn = np.full_like(V, INF)
        for c in (S, H):
            lap_green = p.lap(np.full(A, c), ages)          # cost of driving lap n at age a (green)
            for m in range(4):
                if not (m >> c) & 1:
                    continue                                 # mask must include current compound
                for s_rem in range(sc_laps + 1):
                    under_sc = s_rem > 0
                    lap_cost = np.zeros(A) if under_sc else lap_green
                    # next-lap SC state distribution
                    if under_sc:
                        nxt = [(s_rem - 1, 1.0)]
                    else:
                        nxt = [(0, 1.0 - p_sc), (sc_laps, p_sc)] if n < race_laps else [(0, 1.0)]
                    a_next = np.minimum(ages + 1, max_age)
                    stay = sum(w * V[s2, c, a_next, m] for s2, w in nxt)
                    best = stay.copy()
                    act = np.full(A, -1, np.int8)
                    if n < race_laps:
                        loss = pit_sc if under_sc else pit_green
                        for c2 in (S, H):
                            m2 = m | (1 << c2)
                            go = loss + sum(w * V[s2, c2, 0, m2] for s2, w in nxt)
                            better = go < best
                            best = np.where(better, go, best)
                            act = np.where(better, c2, act)
                    Vn[s_rem, c, :, m] = lap_cost + best
                    pol[n, s_rem, c, :, m] = act
        V = Vn
    m0 = 1 << start_compound
    return SDPResult(float(V[0, start_compound, start_age, m0]), pol, V)


def simulate_policy(p: Pace, policy, pit_green, pit_sc, p_sc, rng, n_races=4000, sc_laps=4,
                    race_laps=57, start_compound=S, start_age=3):
    """Monte Carlo of a policy (from :func:`sdp`) under random safety cars; returns costs per race."""
    costs = np.zeros(n_races)
    for r in range(n_races):
        c, a, m, s_rem, cost = start_compound, start_age, 1 << start_compound, 0, 0.0
        for n in range(1, race_laps + 1):
            under = s_rem > 0
            if not under:
                cost += float(p.lap(np.array(c), np.array(a)))
            act = policy[n, s_rem, c, min(a, policy.shape[3] - 1), m]
            if n < race_laps and act >= 0:
                cost += pit_sc if under else pit_green
                c, a, m = int(act), 0, m | (1 << int(act))
            else:
                a += 1
            if under:
                s_rem -= 1
            elif n < race_laps and rng.random() < p_sc:
                s_rem = sc_laps
        costs[r] = cost if m == 3 else np.inf
    return costs


def static_under_sc(p: Pace, plan: Plan, pit_green, pit_sc, p_sc, rng, n_races=4000, sc_laps=4, race_laps=57,
                    start_age=3):
    """A fixed plan that does not react to safety cars (it may still pit under one by chance)."""
    pits = set(plan.stops)
    costs = np.zeros(n_races)
    bounds = (0,) + plan.stops + (race_laps,)
    comp_of = np.zeros(race_laps + 1, int)
    for i, c in enumerate(plan.compounds):
        comp_of[bounds[i] + 1: bounds[i + 1] + 1] = c
    first_age = start_age if plan.compounds[0] == S else 0
    for r in range(n_races):
        a, s_rem, cost = first_age, 0, 0.0
        for n in range(1, race_laps + 1):
            under = s_rem > 0
            c = comp_of[n]
            if not under:
                cost += float(p.lap(np.array(c), np.array(a)))
            if n in pits:
                cost += pit_sc if under else pit_green
                a = 0
            else:
                a += 1
            if under:
                s_rem -= 1
            elif n < race_laps and rng.random() < p_sc:
                s_rem = sc_laps
        costs[r] = cost
    return costs
