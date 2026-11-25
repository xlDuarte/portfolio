"""Physics-based bearing diagnosis: is there a comb at a defect frequency in the envelope spectrum?

No fault labels are used. For every 1-second window the indicator of each fault type is the
harmonic prominence (dB) of its defect frequency in the squared envelope spectrum, computed with
the shaft speed of the record. Two pre-processing paths, as in Smith and Randall's CWRU benchmark
(MSSP 64–65, 2015):

* ``cpw``: cepstral pre-whitening of the whole band, then SES;
* ``sk``:  band-pass on the spectral-kurtosis maximum, then SES.

Decision: the fault type with the largest indicator, if that indicator exceeds a threshold τ set
on healthy windows only (the 99th percentile of the maximum indicator, so a 1 % false-alarm rate
by construction). The normal windows that are scored are never those used to set τ: the threshold
for the normal records at load L comes from the normal records at the other three loads.
"""
from __future__ import annotations

import numpy as np

from . import dsp
from .data import FS, Record, windows
from .kinematics import FAULT_FREQ, SKF_6205

TYPES = ("OR", "IR", "B")
WIN = 12_000                                  # 1 s: 1 Hz resolution, ≈ 30 shaft revolutions


def indicators(rec: Record, method: str = "cpw", win: int = WIN, fmax: float = 600.0):
    """(n_windows, 3) harmonic prominence for OR, IR, B and the demodulation band per window."""
    fq = SKF_6205.frequencies(rec.fr)
    out, bands = [], []
    for w in windows(rec.x, win):
        if method == "cpw":
            y = dsp.cpw(w)
            bands.append((0.0, FS / 2, 0.0))
        elif method == "sk":
            fc, bw, k = dsp.sk_band(w, FS)
            y = dsp.bandpass(w, fc - bw / 2, fc + bw / 2, FS)
            bands.append((fc, bw, k))
        else:
            raise ValueError(method)
        f, S = dsp.ses(y, FS, fmax)
        out.append([dsp.harmonic_prominence(f, S, fq[FAULT_FREQ[t]]) for t in TYPES])
    return np.array(out), np.array(bands)


def threshold(H_normal: np.ndarray, q: float = 0.99) -> float:
    return float(np.quantile(H_normal.max(axis=1), q))


def decide(H: np.ndarray, tau: float) -> np.ndarray:
    """Predicted class per window: 'N' below τ, else the fault type of the largest indicator."""
    best = np.array(TYPES)[np.argmax(H, axis=1)]
    return np.where(H.max(axis=1) > tau, best, "N")


def evaluate(records: list[Record], method: str = "cpw", q: float = 0.99):
    """Window-level predictions for every record, with leave-one-load-out thresholds for normals."""
    H = {r.id: indicators(r, method)[0] for r in records}
    normals = [r for r in records if r.cls == "N"]
    tau_all = threshold(np.vstack([H[r.id] for r in normals]), q)
    rows = []
    for r in records:
        if r.cls == "N":
            tau = threshold(np.vstack([H[n.id] for n in normals if n.load_hp != r.load_hp]), q)
        else:
            tau = tau_all
        pred = decide(H[r.id], tau)
        rows.append({"id": r.id, "cls": r.cls, "size": r.size_mils, "load": r.load_hp, "rpm": r.rpm, "tau": tau,
                     "H_mean": H[r.id].mean(axis=0), "pred": pred, "acc": float(np.mean(pred == r.cls)),
                     "majority": max(set(pred), key=list(pred).count)})
    return rows, tau_all


def confusion(rows, classes=("N",) + TYPES):
    M = np.zeros((len(classes), len(classes)), int)
    for r in rows:
        for p in r["pred"]:
            M[classes.index(r["cls"]), classes.index(p)] += 1
    return M
