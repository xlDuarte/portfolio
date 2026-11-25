"""Synthetic bearing-fault vibration with known truth, to verify the diagnosis chain (#004).

Model (Randall and Antoni, MSSP 25, 2011, §2): a localised defect produces impacts at the defect
frequency f_d with a small random jitter of the inter-impact period (slip, σ ≈ 1 %), each exciting
a structural resonance (single degree of freedom, natural frequency f_n, damping ζ):

    x(t) = Σ_j q(t_j)·A·h(t − t_j) + Σ_k B_k sin(2π k f_r t + φ_k) + n(t)
    h(t) = e^(−ζ ω_n t) sin(ω_d t),  ω_d = ω_n √(1 − ζ²)

q(t) is the load-zone modulation: 1 for an outer-race defect (fixed in the load zone), the
shaft-periodic 1 − m(1 − cos 2π f_r t)/2 for an inner-race defect that passes through it once per
revolution. Shaft harmonics B_k and, optionally, a gear-mesh comb (mesh order 27, six harmonics,
amplitude ``mesh_amp``) mask the spectrum, as discrete components do on a real machine; n(t) is
white noise.
SNR is defined as 20·log10(A / σ_n), the peak impact amplitude over the noise standard deviation.
"""
from __future__ import annotations

import numpy as np

from .kinematics import FAULT_FREQ, SKF_6205


def fault_signal(kind: str, snr_db: float, fs: float = 12_000.0, duration: float = 1.0, fr: float = 29.95,
                 fn: float = 3_500.0, zeta: float = 0.05, jitter: float = 0.01, mod_depth: float = 0.8,
                 shaft_amp=(0.5, 0.25, 0.1), mesh_amp: float = 0.0, rng: np.random.Generator | None = None) -> np.ndarray:
    rng = rng or np.random.default_rng()
    n = int(fs * duration)
    t = np.arange(n) / fs
    x = sum(a * np.sin(2 * np.pi * (k + 1) * fr * t + rng.uniform(0, 2 * np.pi)) for k, a in enumerate(shaft_amp))
    if mesh_amp:
        x = x + sum(mesh_amp / k * np.sin(2 * np.pi * k * 27 * fr * t + rng.uniform(0, 2 * np.pi)) for k in range(1, 7))
    x = x + rng.standard_normal(n)
    if kind == "N":
        return x
    fd = SKF_6205.frequencies(fr)[FAULT_FREQ[kind]]
    A = 10 ** (snr_db / 20)
    wn = 2 * np.pi * fn
    th = np.arange(int(0.02 * fs)) / fs                         # 20 ms of ring-down
    h = np.exp(-zeta * wn * th) * np.sin(wn * np.sqrt(1 - zeta ** 2) * th)
    tj, T = rng.uniform(0, 1 / fd), 1 / fd
    while tj < duration:
        q = 1.0 if kind == "OR" else 1 - mod_depth * (1 - np.cos(2 * np.pi * fr * tj)) / 2
        i = int(tj * fs)
        seg = h[: n - i]
        x[i:i + len(seg)] += q * A * seg
        tj += T * (1 + jitter * rng.standard_normal())
    return x
