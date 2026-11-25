"""Plackett–Luce race-result model fitted by maximum likelihood, with walk-forward probabilities.

For an event with drivers i = 1..n and utilities s_i = w·x_i, the probability of a finishing
order π truncated at the first k places is

    P(π₁..π_k) = Π_{j=1..k} exp(s_{π_j}) / Σ_{l ∉ {π₁..π_{j−1}}} exp(s_l)

(Plackett, 1975; Luce, 1959). The log-likelihood is concave in w, so the maximum is unique; it is
found by L-BFGS with the analytic gradient and a small L2 penalty. Win probabilities are the
softmax of s; podium and top-10 probabilities come from exact sampling of the model by the
Gumbel-max trick (sort s_i + G_i, G_i ~ Gumbel(0, 1)).

Features per driver and event (as published by the site's F1-PIP dataset, all known before the
race): grid position, mean of the driver's last five results, mean of the constructor's last five.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

DATA = Path(__file__).resolve().parents[1] / "site" / "motorsport" / "data" / "results-real.json"


def load_events(path: Path = DATA):
    events = json.loads(Path(path).read_text(encoding="utf-8"))["events"]
    out = []
    for e in events:
        rows = [r for r in e["rows"] if r.get("position") is not None]
        X = np.array([r["x"] for r in rows], float)
        pos = np.array([r["position"] for r in rows], int)
        out.append({"id": e["id"], "name": e["name"], "year": e["year"], "date": e["date"],
                    "codes": [r["driver_code"] for r in rows], "X": X, "pos": pos})
    out.sort(key=lambda e: e["date"])
    return out


def features(X, cols):
    """Transform raw features: lower grid/finish numbers are better, so use their negatives."""
    return -X[:, cols]


def neg_loglik(w, events, cols, k, l2):
    nll = 0.0
    grad = np.zeros_like(w)
    for e in events:
        F = features(e["X"], cols)
        s = F @ w
        order = np.argsort(e["pos"])
        remaining = np.ones(len(s), bool)
        for j in range(min(k, len(order))):
            i = order[j]
            ss = s[remaining]
            m = ss.max()
            p = np.exp(ss - m)
            z = p.sum()
            nll -= s[i] - (m + np.log(z))
            grad -= F[i] - (p / z) @ F[remaining]
            remaining[i] = False
    nll += l2 * w @ w
    grad += 2 * l2 * w
    return nll, grad


def fit(events, cols, k: int = 10, l2: float = 1e-3):
    w0 = np.zeros(len(cols))
    res = minimize(neg_loglik, w0, args=(events, cols, k, l2), jac=True, method="L-BFGS-B")
    # observed information for standard errors (numerical Hessian of the analytic gradient)
    h = 1e-5
    H = np.zeros((len(cols), len(cols)))
    for j in range(len(cols)):
        e = np.zeros(len(cols)); e[j] = h
        H[:, j] = (neg_loglik(res.x + e, events, cols, k, l2)[1] - neg_loglik(res.x - e, events, cols, k, l2)[1]) / (2 * h)
    cov = np.linalg.inv(0.5 * (H + H.T))
    return res.x, np.sqrt(np.diag(cov)), float(res.fun)


def probabilities(w, event, cols, rng, n_samples: int = 20000):
    """P(win), P(podium), P(top 10) for every driver of the event (exact win, sampled others)."""
    s = features(event["X"], cols) @ w
    win = np.exp(s - s.max()); win /= win.sum()
    g = rng.gumbel(size=(n_samples, len(s)))
    ranks = np.argsort(np.argsort(-(s[None, :] + g), axis=1), axis=1)       # 0 = winner
    return {"win": win, "podium": (ranks < 3).mean(axis=0), "top10": (ranks < 10).mean(axis=0)}


def walk_forward(events, cols, first_year: int = 2023, k: int = 10, seed: int = 111):
    """Fit on every earlier event, predict the next one. Returns per-event predictions and outcomes."""
    rng = np.random.default_rng(seed)
    preds = []
    for i, e in enumerate(events):
        if e["year"] < first_year:
            continue
        w, se, _ = fit(events[:i], cols, k)
        p = probabilities(w, e, cols, rng)
        preds.append({"id": e["id"], "name": e["name"], "year": e["year"], "w": w.tolist(), "se": se.tolist(),
                      "codes": e["codes"], "pos": e["pos"].tolist(), **{m: v.tolist() for m, v in p.items()}})
    return preds


# ------------------------------------------------------------------------------------------------
# Scoring and calibration
# ------------------------------------------------------------------------------------------------
def outcomes(pred, market):
    pos = np.array(pred["pos"])
    return {"win": pos == 1, "podium": pos <= 3, "top10": pos <= 10}[market].astype(float)


def scores(preds, market):
    """Brier score (mean over drivers and events), winner log-loss (win market only)."""
    p = np.concatenate([np.array(x[market]) for x in preds])
    y = np.concatenate([outcomes(x, market) for x in preds])
    out = {"brier": float(np.mean((p - y) ** 2))}
    if market == "win":
        out["logloss_winner"] = float(np.mean([-np.log(max(np.array(x["win"])[np.array(x["pos"]) == 1][0], 1e-12))
                                               for x in preds if (np.array(x["pos"]) == 1).any()]))
    return out


def reliability(preds, market, bins: int = 10):
    """Reliability diagram: mean forecast vs observed frequency per bin, Wilson 95 % interval, ECE."""
    p = np.concatenate([np.array(x[market]) for x in preds])
    y = np.concatenate([outcomes(x, market) for x in preds])
    edges = np.linspace(0, 1, bins + 1)
    idx = np.clip(np.digitize(p, edges) - 1, 0, bins - 1)
    rows, ece = [], 0.0
    for b in range(bins):
        m = idx == b
        n = int(m.sum())
        if n == 0:
            continue
        f, o = float(p[m].mean()), float(y[m].mean())
        z = 1.96
        centre = (o + z * z / (2 * n)) / (1 + z * z / n)
        half = z * np.sqrt(o * (1 - o) / n + z * z / (4 * n * n)) / (1 + z * z / n)
        rows.append({"bin": b, "n": n, "forecast": round(f, 4), "observed": round(o, 4),
                     "lo": round(max(centre - half, 0.0), 4), "hi": round(min(centre + half, 1.0), 4)})
        ece += n / len(p) * abs(f - o)
    # Spiegelhalter (1986) z-test of calibration
    num = np.sum((y - p) * (1 - 2 * p))
    den = np.sqrt(np.sum((1 - 2 * p) ** 2 * p * (1 - p)))
    return {"bins": rows, "ece": float(ece), "spiegelhalter_z": float(num / den) if den > 0 else float("nan"), "n": int(len(p))}


def bootstrap_skill(preds_model, preds_ref, market, n_boot: int = 4000, seed: int = 7):
    """Brier skill score 1 − BS_model/BS_ref with a bootstrap over events (events resampled)."""
    rng = np.random.default_rng(seed)

    def per_event(preds):
        return np.array([np.sum((np.array(x[market]) - outcomes(x, market)) ** 2) for x in preds])

    a, b = per_event(preds_model), per_event(preds_ref)
    bss = 1 - a.sum() / b.sum()
    idx = rng.integers(0, len(a), (n_boot, len(a)))
    boots = 1 - a[idx].sum(axis=1) / b[idx].sum(axis=1)
    return {"bss": float(bss), "ci95": [float(x) for x in np.quantile(boots, [0.025, 0.975])]}
