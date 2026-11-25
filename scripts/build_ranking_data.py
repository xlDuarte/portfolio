"""Build site/motorsport/data/ranking-calibration.json (phase 3, project #111).

    python scripts/build_ranking_data.py

Walk-forward evaluation (2023–2024, each event predicted from every earlier event only) of
race-result probabilities: Plackett–Luce fitted by maximum likelihood, a grid-only Plackett–Luce,
the site's previous approach (ridge score turned into probabilities by a softmax with a fixed
temperature of 5) and the uniform baseline. Proper scores, reliability diagrams with Wilson
intervals, ECE, Spiegelhalter's z and event-bootstrap intervals for the Brier skill score.
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

from race_strategy.ranking import (bootstrap_skill, features, load_events, reliability, scores,  # noqa: E402
                                   walk_forward)

OUT = ROOT / "site" / "motorsport" / "data" / "ranking-calibration.json"
COLS = [0, 1, 2]
NAMES = ["grid", "forma do piloto (5)", "forma da equipe (5)"]
MARKETS = ("win", "podium", "top10")
K_GRID = [3, 5, 10, 20]
r4 = lambda x: round(float(x), 4)


def ridge_softmax(events, first_year=2023, temperature=5.0, alpha=1.0, seed=111, n_samples=20000):
    """Previous site method: ridge regression of finishing position on the three features, then
    P(win) = softmax(−score/T) with T fixed a priori; podium/top-10 by Gumbel sampling of the same
    Plackett–Luce utilities −score/T."""
    rng = np.random.default_rng(seed)
    preds = []
    for i, e in enumerate(events):
        if e["year"] < first_year:
            continue
        X = np.vstack([ev["X"] for ev in events[:i]])
        y = np.concatenate([ev["pos"] for ev in events[:i]]).astype(float)
        mu, sd = X.mean(0), X.std(0)
        Z = (X - mu) / sd
        A = np.column_stack([np.ones(len(Z)), Z])
        P = alpha * np.eye(A.shape[1]); P[0, 0] = 0
        w = np.linalg.solve(A.T @ A + P, A.T @ y)
        score = np.column_stack([np.ones(len(e["X"])), (e["X"] - mu) / sd]) @ w
        s = -score / temperature
        win = np.exp(s - s.max()); win /= win.sum()
        g = rng.gumbel(size=(n_samples, len(s)))
        ranks = np.argsort(np.argsort(-(s[None] + g), axis=1), axis=1)
        preds.append({"id": e["id"], "name": e["name"], "year": e["year"], "codes": e["codes"], "pos": e["pos"].tolist(),
                      "win": win.tolist(), "podium": (ranks < 3).mean(0).tolist(), "top10": (ranks < 10).mean(0).tolist()})
    return preds


def uniform(preds):
    return [{**x, **{m: [k / len(x["pos"])] * len(x["pos"]) for m, k in (("win", 1), ("podium", 3), ("top10", 10))}}
            for x in preds]


def main() -> None:
    events = load_events()
    models = {
        "Plackett–Luce (MLE)": walk_forward(events, COLS),
        "Plackett–Luce, só grid": walk_forward(events, [0]),
        "Ridge + softmax T = 5 (anterior)": ridge_softmax(events),
    }
    models["Uniforme"] = uniform(models["Plackett–Luce (MLE)"])
    ref = "Plackett–Luce (MLE)"
    out = {"schema": 1, "generated_by": "scripts/build_ranking_data.py",
           "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
           "events_total": len(events), "events_scored": len(models[ref]),
           "first_scored": models[ref][0]["name"] + f" {models[ref][0]['year']}", "features": NAMES,
           "drivers_scored": int(sum(len(x["pos"]) for x in models[ref])), "models": {}}
    for name, preds in models.items():
        row = {m: {k: r4(v) for k, v in scores(preds, m).items()} for m in MARKETS}
        if name != ref:
            row["skill_of_pl"] = {m: {k: (r4(v) if not isinstance(v, list) else [r4(x) for x in v])
                                      for k, v in bootstrap_skill(models[ref], preds, m).items()} for m in MARKETS}
        if name != "Uniforme":
            row["reliability"] = {}
            for m in MARKETS:
                rel = reliability(preds, m)
                row["reliability"][m] = {"bins": rel["bins"], "ece": r4(rel["ece"]), "z": round(rel["spiegelhalter_z"], 2), "n": rel["n"]}
        out["models"][name] = row
    # coefficient trajectory of the MLE model (standardised effect of 1 position, utility units)
    out["coef_path"] = [{"event": x["name"], "year": x["year"], "w": [r4(v) for v in x["w"]], "se": [r4(v) for v in x["se"]]}
                        for x in models[ref]]
    # truncation of the likelihood to the first k finishers. A single Plackett–Luce scale cannot fit
    # the fight for the win and the midfield at once, so k is chosen per market on 2023 only and
    # judged on 2024, which played no part in the choice.
    sens, by_k = {}, {}
    for k in K_GRID:
        p = by_k[k] = walk_forward(events, COLS, k=k)
        sens[str(k)] = {}
        for yr in (2023, 2024):
            py = [x for x in p if x["year"] == yr]
            sens[str(k)][str(yr)] = {m: r4(scores(py, m)["brier"]) for m in MARKETS} | {"logloss_winner": r4(scores(py, "win")["logloss_winner"])}
    chosen = {m: min(K_GRID, key=lambda k: sens[str(k)]["2023"][m]) for m in MARKETS}
    test = {}
    for m in MARKETS:
        sel = [x for x in by_k[chosen[m]] if x["year"] == 2024]
        k10 = [x for x in by_k[10] if x["year"] == 2024]
        test[m] = {"k": chosen[m], "brier_chosen": r4(scores(sel, m)["brier"]), "brier_k10": r4(scores(k10, m)["brier"]),
                   "skill_vs_k10": {kk: (r4(v) if not isinstance(v, list) else [r4(x) for x in v])
                                    for kk, v in bootstrap_skill(sel, k10, m).items()},
                   "ece_chosen": r4(reliability(sel, m)["ece"]), "ece_k10": r4(reliability(k10, m)["ece"])}
    out["truncation"] = {"grid": K_GRID, "by_k": sens, "chosen_on_2023": chosen, "test_2024": test}
    # the event shown on the F1-PIP page: 2024 Bahrain, before the race
    bah = next(x for x in models[ref] if x["year"] == 2024 and "Bahrain" in x["name"])
    old = next(x for x in models["Ridge + softmax T = 5 (anterior)"] if x["id"] == bah["id"])
    order = np.argsort(-np.array(bah["win"]))
    out["bahrain_2024"] = [{"driver": bah["codes"][i], "pos": bah["pos"][i], "win": r4(bah["win"][i]),
                            "podium": r4(bah["podium"][i]), "top10": r4(bah["top10"][i]), "win_old": r4(old["win"][i])}
                           for i in order]
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":"), allow_nan=False), encoding="utf-8")
    for name, row in out["models"].items():
        print(name, {m: row[m] for m in MARKETS}, {m: row["reliability"][m]["ece"] for m in MARKETS} if "reliability" in row else "")
        if "skill_of_pl" in row:
            print("   BSS of PL vs", name, row["skill_of_pl"])
    print("truncation", json.dumps(out["truncation"]["test_2024"], indent=1), out["truncation"]["chosen_on_2023"])
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
