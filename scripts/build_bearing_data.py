"""Build site/data/bearings-cwru.json (phase 4a: projects #004, #104, #052).

    python scripts/fetch_cwru.py          # once: verified cache of the 40 CWRU records
    python scripts/build_bearing_data.py

Real CWRU drive-end vibration (12 kHz, SKF 6205, loads 0–3 hp): physics-based envelope diagnosis
with two pre-processing paths, verification of the chain on simulated faults with known truth,
novelty detection and supervised classification under three validation protocols, and order-domain
signature matching. Deterministic (fixed seeds).
"""
from __future__ import annotations

import json
import platform
import sys
from pathlib import Path

import numpy as np
import scipy
from scipy.signal import welch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bearings import diagnosis as D  # noqa: E402
from bearings import dsp  # noqa: E402
from bearings import monitoring as M  # noqa: E402
from bearings import signatures as G  # noqa: E402
from bearings.data import CLASSES, FS, load_all, manifest, windows  # noqa: E402
from bearings.kinematics import FAULT_FREQ, SKF_6205  # noqa: E402
from bearings.learn import balanced_accuracy, roc  # noqa: E402
from bearings.simulate import fault_signal  # noqa: E402

OUT = ROOT / "site" / "data" / "bearings-cwru.json"
r3 = lambda x: round(float(x), 3)
EXAMPLES = (97, 105, 118, 130)
SNR = [-6, -3, 0, 3, 6, 9, 12]
N_SIM = 60


def sampling_check(records):
    """Is the healthy baseline really sampled at 12 kHz? The 1× shaft line must stand out."""
    x = next(r for r in records if r.id == 97).x
    out = {}
    for fs in (12_000, 48_000):
        f, P = welch(x, fs=fs, nperseg=2 ** 17)
        fr = 1796 / 60

        def prom(fx):
            i = np.argmin(abs(f - fx))
            w = (abs(f - fx) < 3) & (abs(f - fx) > 0.6)
            return float(10 * np.log10(P[max(i - 1, 0):i + 2].max() / np.median(P[w])))
        out[str(fs)] = {"shaft_1x_db": r3(prom(fr)), "line_60hz_db": r3(prom(60.0))}
    return out


def examples(records):
    ex = {}
    for r in records:
        if r.id not in EXAMPLES:
            continue
        w = windows(r.x, D.WIN)[0]
        f, S = dsp.ses(dsp.cpw(w), FS, 600)
        k = f <= 600
        ex[r.label] = {"id": r.id, "rpm": r.rpm, "freq": np.round(f[k][::1], 2).tolist(),
                       "ses_db": np.round(10 * np.log10(S[k] / np.median(S[k])), 2).tolist(),
                       "wave": np.round(w[:1200:2], 4).tolist(),
                       "fault_hz": {t: r3(v) for t, v in SKF_6205.frequencies(r.fr).items()}}
        if r.id == 130:
            ex[r.label]["kurtogram"] = [{"nw": nw, "freq": np.round(fk, 1).tolist(), "sk": np.round(sk, 3).tolist()}
                                        for nw, fk, sk in dsp.kurtogram(w, FS)]
    return ex


def detectability():
    """P(detect) vs SNR on simulated faults; thresholds at 1 % false alarm from fault-free simulations."""
    rng = np.random.default_rng(4)
    fq = SKF_6205.frequencies(29.95)

    def H(x, method, kind):
        if method == "cpw":
            y = dsp.cpw(x)
        elif method == "sk":
            fc, bw, _ = dsp.sk_band(x, FS)
            y = dsp.bandpass(x, fc - bw / 2, fc + bw / 2, FS)
        else:
            y = x
        f, S = dsp.ses(y, FS, 600)
        return dsp.harmonic_prominence(f, S, fq[FAULT_FREQ[kind]])

    out = {}
    for scen, mesh in (("ruido branco", 0.0), ("com engrenamento", 4.0)):
        tau = {m: float(np.quantile([max(H(fault_signal("N", 0, mesh_amp=mesh, rng=rng), m, k) for k in ("OR", "IR", "B"))
                                     for _ in range(200)], 0.99)) for m in ("raw", "cpw", "sk")}
        curves = {}
        for kind in ("OR", "IR"):
            curves[kind] = {m: [] for m in ("raw", "cpw", "sk")}
            for snr in SNR:
                sims = [fault_signal(kind, snr, mesh_amp=mesh, rng=rng) for _ in range(N_SIM)]
                for m in ("raw", "cpw", "sk"):
                    curves[kind][m].append(r3(np.mean([H(x, m, kind) > tau[m] for x in sims])))
        out[scen] = {"tau": {k: r3(v) for k, v in tau.items()}, "curves": curves}
    return {"snr_db": SNR, "n_sim": N_SIM, "scenarios": out}


def main() -> None:
    records = load_all()
    man = manifest()
    out = {"schema": 1, "generated_by": "scripts/build_bearing_data.py",
           "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
           "source": {k: man[k] for k in ("source", "canonical_url", "mirror", "mirror_commit", "fs_hz")} | {"records": len(records)},
           "bearing": {"name": SKF_6205.name, "n_balls": SKF_6205.n_balls, "ball_d_mm": r3(SKF_6205.ball_d * 1000),
                       "pitch_d_mm": r3(SKF_6205.pitch_d * 1000), "orders": {k: round(v, 4) for k, v in SKF_6205.orders().items()}},
           "sampling_check": sampling_check(records)}
    # --- physics diagnosis ------------------------------------------------------------------
    diag = {}
    for method in ("cpw", "sk"):
        rows, tau = D.evaluate(records, method)
        Mx = D.confusion(rows)
        y = np.concatenate([[r["cls"]] * len(r["pred"]) for r in rows]); p = np.concatenate([r["pred"] for r in rows])
        diag[method] = {"tau_db": r3(tau), "confusion": Mx.tolist(), "classes": ["N", *D.TYPES],
                        "balanced_accuracy": r3(balanced_accuracy(y, p)),
                        "records": [{"id": r["id"], "cls": r["cls"], "size": r["size"], "load": r["load"], "rpm": r["rpm"],
                                     "H": [r3(v) for v in r["H_mean"]], "acc": r3(r["acc"]), "majority": str(r["majority"])} for r in rows]}
        maj = [r for r in rows if r["cls"] != "N"]
        diag[method]["records_diagnosed"] = {c: f"{sum(r['majority'] == c for r in maj if r['cls'] == c)}/{sum(r['cls'] == c for r in maj)}" for c in D.TYPES}
        print(method, "balanced", diag[method]["balanced_accuracy"], diag[method]["records_diagnosed"])
    out["diagnosis"] = diag
    out["examples"] = examples(records)
    out["detectability"] = detectability()
    print("detectability", json.dumps(out["detectability"]["scenarios"])[:600])
    # --- monitoring (#104) ------------------------------------------------------------------
    T = M.table(records)
    mon = {"features_phys": M.PHYS, "n_bands": M.N_BANDS, "windows": int(len(T["cls"])), "detection": {}, "classification": {}}
    for feat in ("phys", "spec"):
        s, thr = M.detection(T, feat)
        summ = M.detection_summary(T, s)
        fa = {str(L): r3(np.mean(s[(T["cls"] == "N") & (T["load"] == L)] > thr[L])) for L in range(4)}
        det = {c: r3(np.mean([s[i] > thr[T["load"][i]] for i in np.where(T["cls"] == c)[0]])) for c in ("IR", "B", "OR")}
        allpos = s[T["cls"] != "N"]
        mon["detection"][feat] = {"auc": {c: {"auc": r3(v["auc"]), "ci95": [r3(x) for x in v["ci95"]]} for c, v in summ.items()},
                                  "false_alarm_by_load": fa, "detection_rate": det,
                                  "roc": [[r3(a), r3(b)] for a, b in roc(s[T["cls"] == "N"], allpos)]}
        mon["classification"][feat] = {pr: r3(M.classify(T, feat, pr)) for pr in ("windows", "load", "size")}
        print(feat, mon["detection"][feat]["auc"], fa, mon["classification"][feat])
    # healthy record at 0 hp versus the others: where it differs
    nP = T["phys"][T["cls"] == "N"]; nl = T["load"][T["cls"] == "N"]
    mon["healthy_by_load"] = {str(L): {"rms_g": r3(np.exp(nP[nl == L, 0]).mean()), "kurtosis": r3(np.exp(nP[nl == L, 1]).mean())} for L in range(4)}
    out["monitoring"] = mon
    # --- signatures (#052) -----------------------------------------------------------------
    sig = {}
    for axis in ("order", "hz"):
        TS = G.signatures(records, axis)
        sig[axis] = {d: (lambda pe: {"per_class": {k: r3(v) for k, v in pe[0].items()}, "balanced": r3(pe[1])})(G.evaluate(TS, d))
                     for d in ("load", "size")}
        if axis == "order":
            lib = TS["load"] == 0
            sig["centroids"] = {c: np.round(TS["V"][lib & (TS["cls"] == c)].mean(0)[::2] * 100, 3).tolist() for c in CLASSES}
            sig["orders"] = np.round(G.ORDERS[::2], 3).tolist()
    print("signatures", {a: sig[a] for a in ("order", "hz")})
    out["signatures"] = sig
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":"), allow_nan=False), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
