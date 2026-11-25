"""Signal processing for bearing diagnostics.

* Cepstral pre-whitening (Randall and Sawalhi, 2011): y = IFFT(X/|X|). Setting the spectrum
  magnitude to one removes discrete components (shaft harmonics, gear mesh) and flattens the
  resonances, leaving the phase, where the impulsive bearing signal lives.
* Spectral kurtosis by STFT (Antoni, MSSP 20, 2006): SK(f) = ⟨|X(t,f)|⁴⟩ / ⟨|X(t,f)|²⟩² − 2,
  zero for stationary Gaussian noise and positive in bands where impulses dominate. Computed for
  several window lengths (the "kurtogram"); the maximum selects the demodulation band.
* Squared envelope spectrum (SES): spectrum of |analytic signal|², where a train of impacts at a
  defect frequency shows up as a comb of lines at that frequency and its harmonics.
"""
from __future__ import annotations

import numpy as np
from scipy.signal import butter, hilbert, sosfiltfilt, stft


def cpw(x: np.ndarray) -> np.ndarray:
    X = np.fft.rfft(x - x.mean())
    mag = np.abs(X)
    mag[mag == 0] = 1.0
    return np.fft.irfft(X / mag, n=len(x))


def bandpass(x: np.ndarray, lo: float, hi: float, fs: float, order: int = 4) -> np.ndarray:
    hi = min(hi, 0.49 * fs)
    lo = min(max(lo, 1.0), 0.8 * hi)
    sos = butter(order, [lo, hi], btype="bandpass", fs=fs, output="sos")
    return sosfiltfilt(sos, x)


def ses(x: np.ndarray, fs: float, fmax: float = 1000.0):
    """Squared envelope spectrum up to fmax: (frequency, amplitude), amplitude normalised by length."""
    e2 = np.abs(hilbert(x)) ** 2
    e2 = e2 - e2.mean()
    S = np.abs(np.fft.rfft(e2 * np.hanning(len(e2)))) / len(e2)
    f = np.fft.rfftfreq(len(e2), 1 / fs)
    m = f <= fmax
    return f[m], S[m]


def kurtogram(x: np.ndarray, fs: float, nws=(16, 24, 32)):
    """STFT spectral kurtosis for each window length. Returns list of (nw, freqs, SK)."""
    out = []
    for nw in nws:
        f, _, Z = stft(x, fs=fs, nperseg=nw, noverlap=3 * nw // 4, boundary=None, padded=False)
        p2 = np.abs(Z) ** 2
        sk = np.mean(p2 ** 2, axis=1) / np.maximum(np.mean(p2, axis=1) ** 2, 1e-30) - 2.0
        sk[(f < fs / nw) | (f > fs / 2 - fs / nw)] = 0.0          # discard edge bins
        out.append((nw, f, sk))
    return out


def sk_band(x: np.ndarray, fs: float, nws=(16, 24, 32)):
    """(centre, bandwidth, SK) of the kurtogram maximum; bandwidth = 2·fs/nw (Hann main lobe).

    Windows are kept short (bandwidth 750–1500 Hz) because the demodulation band must be several
    times wider than the highest defect frequency (BPFI ≈ 160 Hz) to keep its harmonics.
    """
    best = max(((nw, f[np.argmax(sk)], sk.max()) for nw, f, sk in kurtogram(x, fs, nws)), key=lambda t: t[2])
    nw, fc, k = best
    bw = 2 * fs / nw
    return float(np.clip(fc, bw / 2 + 5, fs / 2 - bw / 2 - 5)), float(bw), float(k)


def harmonic_prominence(f: np.ndarray, S: np.ndarray, f0: float, n_harm: int = 3, tol: float = 0.015,
                        ref_halfwidth: float = 12.0) -> float:
    """Mean over the first harmonics of 10·log10(peak / local median), in dB.

    The peak is searched in ±tol around k·f0 (slip and speed uncertainty); the reference is the
    median of the SES within ±ref_halfwidth Hz, excluding the search window. 0 dB means the
    harmonic is indistinguishable from the local background.
    """
    df = f[1] - f[0]
    vals = []
    for k in range(1, n_harm + 1):
        c = k * f0
        w = max(tol * c, 1.5 * df)
        win = np.abs(f - c) <= w
        ref = (np.abs(f - c) <= ref_halfwidth) & ~win
        if not win.any() or ref.sum() < 5:
            continue
        vals.append(10 * np.log10(S[win].max() / max(np.median(S[ref]), 1e-30)))
    return float(np.mean(vals)) if vals else 0.0


def features(x: np.ndarray) -> dict[str, float]:
    """Time-domain condition indicators."""
    xc = x - x.mean()
    rms = np.sqrt(np.mean(xc ** 2))
    return {"rms": float(rms), "kurtosis": float(np.mean(xc ** 4) / rms ** 4), "crest": float(np.abs(xc).max() / rms),
            "skew": float(np.mean(xc ** 3) / rms ** 3)}
