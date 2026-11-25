"""Diagnostic signature matching in the order domain (#052).

A signature is the squared envelope spectrum of a window after cepstral pre-whitening, expressed
in dB above its own running median (so the background is 0 dB) and resampled on an axis of shaft
orders (f / f_r). On that axis a defect comb sits at the same place whatever the speed, so a
signature recorded at one load can match a fault recorded at another. The baseline keeps the
frequency axis in Hz.

Matching is nearest-neighbour by cosine similarity against a library of class mean signatures.
Two library designs are evaluated:

* ``load``: library from 0 hp, queries at 1–3 hp (same bearings, different speed);
* ``size``: library from the two other fault sizes, queries at the held-out size (a different
  damaged bearing); the healthy bearing is split by load.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import median_filter

from . import dsp
from .data import FS, Record, windows
from .diagnosis import WIN

ORDERS = np.arange(0.5, 16.0, 0.02)           # up to 3×BPFI ≈ 16.2 orders
HZ = np.arange(15.0, 480.0, 0.6)              # the same span in Hz at ≈ 1 800 rpm


def signature(w: np.ndarray, fr: float, axis: str = "order") -> np.ndarray:
    f, S = dsp.ses(dsp.cpw(w), FS, 600.0)
    db = 10 * np.log10(np.maximum(S, 1e-30) / np.maximum(median_filter(S, size=41, mode="nearest"), 1e-30))
    db = np.clip(db, 0, None)
    grid = ORDERS * fr if axis == "order" else HZ
    v = np.interp(grid, f, db)
    return v / (np.linalg.norm(v) + 1e-12)


def signatures(records: list[Record], axis: str):
    rows = []
    for r in records:
        for w in windows(r.x, WIN):
            rows.append((r.id, r.cls, r.size_mils, r.load_hp, signature(w, r.fr, axis)))
    return {"id": np.array([x[0] for x in rows]), "cls": np.array([x[1] for x in rows]), "size": np.array([x[2] for x in rows]),
            "load": np.array([x[3] for x in rows]), "V": np.array([x[4] for x in rows])}


def match(lib_V, lib_cls, Q):
    """Nearest class centroid by cosine similarity; returns predicted class and best similarity."""
    classes = np.unique(lib_cls)
    C = np.array([lib_V[lib_cls == c].mean(0) for c in classes])
    C /= np.linalg.norm(C, axis=1, keepdims=True)
    sim = Q @ C.T
    return classes[np.argmax(sim, axis=1)], sim.max(axis=1)


def evaluate(T: dict, design: str):
    """Per-class top-1 accuracy and balanced accuracy for a library design."""
    y, pred = T["cls"], np.empty(len(T["cls"]), dtype=object)
    if design == "load":
        lib = T["load"] == 0
        pred[~lib], _ = match(T["V"][lib], y[lib], T["V"][~lib])
        mask = ~lib
    elif design == "size":
        mask = np.zeros(len(y), bool)
        for k, s in enumerate((7, 14, 21)):
            te = (T["size"] == s) | ((y == "N") & (T["load"] == k))
            pred[te], _ = match(T["V"][~te], y[~te], T["V"][te])
            mask |= te
    else:
        raise ValueError(design)
    per = {c: float(np.mean(pred[mask & (y == c)] == c)) for c in ("N", "IR", "B", "OR")}
    return per, float(np.mean(list(per.values())))
