"""Hydraulic test rig (ZeMA, UCI "Condition monitoring of hydraulic systems"): pump leakage from the
physics of a fixed-displacement pump (#036) and oil viscosity and ageing from measured temperature
(#037).

Data: Helwig, Pignanelli and Schütze, I2MTC 2015; 2 205 load cycles of 60 s with the condition of
the cooler, valve, internal pump leakage and accumulator varied together. CC BY 4.0. The raw files
(≈ 730 MB of text) are not committed: ``scripts/fetch_hydraulic.py`` takes them from a public
mirror at a pinned commit, checks SHA-256 (two independent mirrors carry identical git blobs) and
caches 10 Hz pressure, power and flow, the 1 Hz channels and per-cycle statistics.

Physics used:

* **Pump flow.** A fixed-displacement pump at near-constant speed delivers Q = Q_th − Q_L(p, ν),
  where Q_L is the internal leakage. Laminar leakage through clearances scales as Δp/μ
  (Hagen–Poiseuille), so a healthy pump delivers less when the oil is hot and thin. On each load
  plateau of a cycle the flow at the reference pressure p_ref = 156 bar is read from a linear fit
  of flow on pressure.
* **Viscosity.** ASTM D341 (Walther): log₁₀ log₁₀(ν + 0.7) = A − B log₁₀ T, through two reference
  points. The rig's oil is not documented; an ISO VG 46 mineral oil with viscosity index ≈ 100
  (ν₄₀ = 46 mm²/s, ν₁₀₀ = 6.8 mm²/s) is assumed. Only the ratio ν(T)/ν(T_ref) enters the
  correction, and it varies little between VG 32 and VG 68 of the same viscosity index.
* **Temperature compensation.** Q_ref = Q_th − K/ν(T) is fitted on healthy-pump cycles of the
  training data; the leakage deficit ΔQ = Q_th − K/ν(T) − Q_ref is then a temperature-free
  measure of pump wear.
* **Hydraulic efficiency.** η = Σ p·Q / Σ P_el on the plateaus (p in bar, Q in L/min →
  p·Q/600 in kW).
* **Oil ageing (#037).** Oxidation follows Arrhenius kinetics, rate ∝ exp(−E_a/RT). With
  E_a = 66 kJ/mol the rate doubles every 10 °C around 65 °C (the usual rule of thumb for mineral
  oils); E_a = 50 and 80 kJ/mol bound the sensitivity. Relative ageing per cycle is computed from
  the measured tank temperature.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "hydraulic" / "manifest.json"
CACHE = ROOT / "data" / "external" / "hydraulic" / "cycles.npz"
FIXTURE = ROOT / "tests" / "fixtures" / "hydraulic_excerpt.npz"
P_REF = 156.0                        # bar, middle load plateau
NU40, NU100 = 46.0, 6.8              # mm²/s, assumed ISO VG 46, VI ≈ 100
R_GAS = 8.314462618
SENSORS = ("PS1", "PS2", "PS3", "PS4", "PS5", "PS6", "EPS1", "FS1", "FS2", "TS1", "TS2", "TS3", "TS4", "VS1", "CE", "CP", "SE")
LABELS = ("cooler", "valve", "pump", "accumulator", "stable")


def manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def load(path: Path = CACHE) -> dict:
    if not Path(path).exists():
        raise FileNotFoundError("hydraulic cache missing: run `python scripts/fetch_hydraulic.py`")
    z = np.load(path)
    return {k: z[k] for k in z.files}


# ------------------------------------------------------------------------------------------------
# viscosity and ageing
# ------------------------------------------------------------------------------------------------
def walther(T_c, nu40: float = NU40, nu100: float = NU100):
    """Kinematic viscosity (mm²/s) at T_c (°C) from two reference points, ASTM D341."""
    T1, T2 = 313.15, 373.15
    y1, y2 = np.log10(np.log10(nu40 + 0.7)), np.log10(np.log10(nu100 + 0.7))
    B = (y1 - y2) / (np.log10(T2) - np.log10(T1))
    A = y1 + B * np.log10(T1)
    return 10 ** (10 ** (A - B * np.log10(np.asarray(T_c) + 273.15))) - 0.7


def arrhenius_factor(T_c, T_ref_c: float = 40.0, Ea: float = 66e3):
    """Oxidation rate at T relative to T_ref."""
    T, Tr = np.asarray(T_c) + 273.15, T_ref_c + 273.15
    return np.exp(Ea / R_GAS * (1 / Tr - 1 / T))


def ea_for_doubling(T_c: float = 65.0, dT: float = 10.0) -> float:
    """Activation energy that doubles the rate between T − dT/2 and T + dT/2."""
    T1, T2 = T_c - dT / 2 + 273.15, T_c + dT / 2 + 273.15
    return R_GAS * np.log(2) / (1 / T1 - 1 / T2)


# ------------------------------------------------------------------------------------------------
# plateau features
# ------------------------------------------------------------------------------------------------
def plateau_mask(p10: np.ndarray, q10: np.ndarray, dp_tol: float = 0.3, settle: int = 10, p_max: float = 180.0):
    """Samples on a pressure plateau with flow through the main line: |Δp| < dp_tol between 10 Hz
    samples, at least ``settle`` samples (1 s) after the last step, flow above 2 L/min and below the
    relief segment (≈ 191 bar, no flow)."""
    dp = np.abs(np.diff(p10, axis=-1, prepend=p10[..., :1]))
    m = (dp < dp_tol) & (q10 > 2.0) & (p10 < p_max)
    step = dp >= dp_tol
    # forbid the `settle` samples following every step
    blocked = np.zeros_like(step)
    for k in range(settle):
        blocked[..., k:] |= step[..., : step.shape[-1] - k]
    return m & ~blocked


def plateau_features(p10, q10, e10):
    """Per cycle: flow at p_ref (L/min), flow-pressure slope (L/min/bar), hydraulic efficiency,
    number of plateau samples."""
    M = plateau_mask(p10, q10)
    out = np.full((len(p10), 4), np.nan)
    for i in range(len(p10)):
        m = M[i]
        if m.sum() < 30:
            continue
        A = np.column_stack([np.ones(m.sum()), p10[i, m] - P_REF])
        c = np.linalg.lstsq(A, q10[i, m], rcond=None)[0]
        eta = np.sum(p10[i, m] * q10[i, m]) / 600.0 / (np.sum(e10[i, m]) / 1000.0)
        out[i] = [c[0], c[1], eta, m.sum()]
    return out


class Compensation:
    """Healthy-pump model Q_ref = Q_th − K/ν(T), fitted on training cycles only."""

    def fit(self, q_ref, T_c):
        A = np.column_stack([np.ones(len(q_ref)), -1 / walther(T_c)])
        self.Qth, self.K = np.linalg.lstsq(A, q_ref, rcond=None)[0]       # K > 0: leakage conductance × ν
        self.resid_sd = float(np.std(q_ref - A @ np.array([self.Qth, self.K])))
        return self

    def expected(self, T_c):
        return self.Qth - self.K / walther(T_c)

    def deficit(self, q_ref, T_c):
        return self.expected(T_c) - q_ref


# ------------------------------------------------------------------------------------------------
# classification protocols
# ------------------------------------------------------------------------------------------------
def feature_sets(D: dict, train_mask: np.ndarray):
    """Statistical (mean and std of the 17 channels) and physics feature sets; the compensation is
    fitted on healthy-pump, stable cycles of the training rows only."""
    F = D["plateau"]
    T = D["TS1_mean"]
    prof = D["profile"]
    healthy = train_mask & (prof[:, 2] == 0) & (prof[:, 4] == 0) & np.isfinite(F[:, 0])
    comp = Compensation().fit(F[healthy, 0], T[healthy])
    raw = np.column_stack([F[:, 0], F[:, 1], F[:, 2], T])
    phys = np.column_stack([comp.deficit(F[:, 0], T), F[:, 2], T])
    return {"estatísticos": D["stats"], "físicos sem compensação": raw, "físicos com compensação": phys}, comp


def impute(X, train):
    med = np.nanmedian(X[train], axis=0)
    X = X.copy()
    idx = np.where(np.isnan(X))
    X[idx] = med[idx[1]]
    return X
