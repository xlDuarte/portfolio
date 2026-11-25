"""Anomaly detection and supervised classification on CWRU, with honest validation (#104, #052).

CWRU has one damaged bearing per fault type and size, recorded at four loads, and a single healthy
bearing. Windows cut from the same recording are near-copies of each other, so a random split of
windows puts the same bearing in training and test and measures memory, not generalisation
(Hendriks, Dumond and Knox, MSSP 169, 2022). Three protocols are compared:

* ``windows``: random 70/30 split of windows (the common, leaky protocol);
* ``load``:    leave one load out (same bearings, new operating condition);
* ``size``:    leave one fault size out, i.e. a physically different damaged bearing in test.
               The healthy bearing is the same in all folds (there is only one), split by load.
"""
from __future__ import annotations

import numpy as np
from scipy.signal import welch

from . import dsp
from .data import FS, Record, windows
from .diagnosis import WIN, indicators
from .learn import Novelty, Softmax, auc, balanced_accuracy

PHYS = ["log RMS", "log curtose", "log fator de crista", "assimetria", "H pista externa", "H pista interna", "H esfera",
        "log SK máxima"]
N_BANDS = 32


def window_features(rec: Record):
    """Physics-informed (8) and spectral (32 log-PSD bands, 0–6 kHz) features for each 1 s window."""
    W = windows(rec.x, WIN)
    H, _ = indicators(rec, "cpw")
    phys, spec = [], []
    edges = np.linspace(0, FS / 2, N_BANDS + 1)
    for w, h in zip(W, H):
        t = dsp.features(w)
        _, _, k = dsp.sk_band(w, FS)
        phys.append([np.log(t["rms"]), np.log(t["kurtosis"]), np.log(t["crest"]), t["skew"], *h, np.log(max(k, 0) + 1)])
        f, P = welch(w, fs=FS, nperseg=1024)
        idx = np.digitize(f, edges[1:-1])
        spec.append(np.log(np.bincount(idx, weights=P, minlength=N_BANDS) / np.bincount(idx, minlength=N_BANDS)))
    return np.array(phys), np.array(spec)


def table(records: list[Record]):
    rows = []
    for r in records:
        P, S = window_features(r)
        for i in range(len(P)):
            rows.append((r.id, r.cls, r.size_mils, r.load_hp, P[i], S[i]))
    ids = np.array([x[0] for x in rows]); cls = np.array([x[1] for x in rows])
    size = np.array([x[2] for x in rows]); load = np.array([x[3] for x in rows])
    return {"id": ids, "cls": cls, "size": size, "load": load, "phys": np.array([x[4] for x in rows]), "spec": np.array([x[5] for x in rows])}


def detection(T: dict, feat: str):
    """Leave-one-load-out novelty detection: train on healthy windows of three loads, score the
    healthy windows of the fourth and every fault window recorded at that load."""
    s = np.full(len(T["cls"]), np.nan)
    thr = {}
    for L in range(4):
        tr = (T["cls"] == "N") & (T["load"] != L)
        m = Novelty().fit(T[feat][tr])
        te = T["load"] == L
        s[te] = m.score(T[feat][te])
        thr[L] = float(np.quantile(m.score(T[feat][tr]), 0.99))
    return s, thr


def detection_summary(T: dict, s: np.ndarray, n_boot: int = 2000, seed: int = 104):
    """AUC per fault type (healthy vs that type), with a bootstrap over records (cluster bootstrap)."""
    rng = np.random.default_rng(seed)
    out = {}
    neg_ids = np.unique(T["id"][T["cls"] == "N"])
    for c in ("IR", "B", "OR"):
        pos_ids = np.unique(T["id"][T["cls"] == c])
        a = auc(s[T["cls"] == "N"], s[T["cls"] == c])
        boots = []
        for _ in range(n_boot):
            ni = rng.choice(neg_ids, len(neg_ids)); pi = rng.choice(pos_ids, len(pos_ids))
            neg = np.concatenate([s[T["id"] == i] for i in ni]); pos = np.concatenate([s[T["id"] == i] for i in pi])
            boots.append(auc(neg, pos))
        out[c] = {"auc": a, "ci95": [float(x) for x in np.quantile(boots, [0.025, 0.975])]}
    return out


def classify(T: dict, feat: str, protocol: str, seed: int = 52):
    """Balanced accuracy of a 4-class softmax (N, IR, B, OR) under a validation protocol."""
    X, y = T[feat], T["cls"]
    pred = np.empty(len(y), dtype=object)
    if protocol == "windows":
        rng = np.random.default_rng(seed)
        te = rng.random(len(y)) < 0.3
        pred[te] = Softmax().fit(X[~te], y[~te]).predict(X[te])
        return balanced_accuracy(y[te], pred[te].astype(str))
    if protocol == "load":
        for L in range(4):
            te = T["load"] == L
            pred[te] = Softmax().fit(X[~te], y[~te]).predict(X[te])
        return balanced_accuracy(y, pred.astype(str))
    if protocol == "size":
        accs = []
        for k, s in enumerate((7, 14, 21)):
            te = (T["size"] == s) | ((y == "N") & (T["load"] == k))
            p = Softmax().fit(X[~te], y[~te]).predict(X[te])
            accs.append(balanced_accuracy(y[te], p))
        return float(np.mean(accs))
    raise ValueError(protocol)
