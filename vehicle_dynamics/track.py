"""Closed-circuit geometry from noisy position samples.

The racing line is modelled as a periodic curve ``r(s) = (x(s), y(s), z(s))`` written as a truncated
Fourier series in the reference arc length ``s ∈ [0, L)``. Each coordinate is fitted by penalised
least squares, with a roughness penalty equal to the integral of the squared second derivative:

    min_c ‖Φc − x‖² + λ ∫ x''(s)² ds  =  ‖Φc − x‖² + λ (L/2) Σ_k ω_k⁴ (a_k² + b_k²),  ω_k = 2πk/L

which is the periodic analogue of a cubic smoothing spline. λ is chosen by generalised
cross-validation (Craven & Wahba, 1979). Because the basis is periodic, the fitted line closes on
itself with continuous curvature, which the lap simulator needs.

Curvature is the signed planar curvature κ = (x'y'' − y'x'') / (x'² + y'²)^{3/2}; the grade is
θ = atan(dz/ds_h).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class FourierFit:
    length: float
    coef: np.ndarray            # (2K+1,) = [a0, a1..aK, b1..bK]
    lam: float
    gcv: float
    dof: float                  # effective degrees of freedom tr(H)
    rms: float                  # residual RMS of the fit (input units)

    @property
    def k(self) -> int:
        return (len(self.coef) - 1) // 2

    def __call__(self, s, d: int = 0):
        """Value (d = 0) or d-th derivative of the fitted coordinate at arc length s."""
        s = np.asarray(s, float)
        k = np.arange(1, self.k + 1)
        w = 2 * np.pi * k / self.length
        ph = np.outer(s, w)
        a, b = self.coef[1: self.k + 1], self.coef[self.k + 1:]
        # derivative of cos(wx) and sin(wx): rotate phase by d·π/2 and scale by w^d
        c = np.cos(ph + d * np.pi / 2) * w ** d
        sn = np.sin(ph + d * np.pi / 2) * w ** d
        out = c @ a + sn @ b
        if d == 0:
            out = out + self.coef[0]
        return out


def _design(s, length, k):
    w = 2 * np.pi * np.arange(1, k + 1) / length
    ph = np.outer(s, w)
    return np.hstack([np.ones((len(s), 1)), np.cos(ph), np.sin(ph)])


def fourier_smooth(s, values, length: float, k: int, lambdas=None) -> FourierFit:
    """Penalised periodic least squares with λ chosen by GCV over a log grid."""
    s = np.asarray(s, float) % length
    values = np.asarray(values, float)
    phi = _design(s, length, k)
    w = 2 * np.pi * np.arange(1, k + 1) / length
    pen = np.concatenate([[0.0], w ** 4, w ** 4]) * (length / 2)
    ptp, ptx = phi.T @ phi, phi.T @ values
    n = len(values)
    best = None
    for lam in (np.logspace(-2, 8, 61) if lambdas is None else lambdas):
        a = ptp + lam * np.diag(pen)
        coef = np.linalg.solve(a, ptx)
        resid = values - phi @ coef
        dof = float(np.trace(np.linalg.solve(a, ptp)))
        rss = float(resid @ resid)
        gcv = n * rss / max(n - dof, 1e-9) ** 2
        if best is None or gcv < best.gcv:
            best = FourierFit(length, coef, float(lam), gcv, dof, float(np.sqrt(rss / n)))
    return best


@dataclass
class Track:
    s: np.ndarray               # arc length of the resampled line (m), starts at 0
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray
    kappa: np.ndarray           # signed curvature (1/m), positive = left turn
    grade: np.ndarray           # rad, positive = uphill
    length: float
    fits: dict

    @property
    def ds(self) -> np.ndarray:
        return np.diff(np.append(self.s, self.length))

    def to_dict(self, decimals: int = 3) -> dict:
        r = lambda a, d=decimals: np.round(a, d).tolist()
        return {"length_m": round(self.length, 2), "s": r(self.s, 2), "x": r(self.x, 2), "y": r(self.y, 2),
                "z": r(self.z, 2), "kappa": r(self.kappa, 6), "grade": r(self.grade, 5),
                "fit": {k: {"harmonics": f.k, "lambda": f.lam, "dof": round(f.dof, 1), "residual_rms_m": round(f.rms, 3)}
                        for k, f in self.fits.items()}}


def build_track(s_ref, x, y, z, length_ref: float, k: int = 160, ds: float = 2.0) -> Track:
    """Fit x(s), y(s), z(s) to samples located at reference arc length s_ref and resample by true arc length."""
    fx = fourier_smooth(s_ref, x, length_ref, k)
    fy = fourier_smooth(s_ref, y, length_ref, k)
    fz = fourier_smooth(s_ref, z, length_ref, min(k, 40))
    # true arc length of the fitted curve (dense trapezoid)
    u = np.linspace(0, length_ref, 40001)
    speed = np.hypot(fx(u, 1), fy(u, 1))
    arc = np.concatenate([[0.0], np.cumsum(0.5 * (speed[1:] + speed[:-1]) * np.diff(u))])
    length = float(arc[-1])
    n = int(round(length / ds))
    s = np.linspace(0, length, n, endpoint=False)
    uu = np.interp(s, arc, u)
    x1, y1, x2, y2 = fx(uu, 1), fy(uu, 1), fx(uu, 2), fy(uu, 2)
    kappa = (x1 * y2 - y1 * x2) / np.power(x1 * x1 + y1 * y1, 1.5)
    dzdu = fz(uu, 1)
    grade = np.arctan(dzdu / np.hypot(x1, y1))
    return Track(s, fx(uu), fy(uu), fz(uu), kappa, grade, length, {"x": fx, "y": fy, "z": fz})


def project(points_xy, line_x, line_y, line_s):
    """Arc-length coordinate of each point on a dense polyline (nearest vertex, then local refine)."""
    p = np.asarray(points_xy, float)
    lx, ly = np.asarray(line_x), np.asarray(line_y)
    d2 = (p[:, 0:1] - lx[None, :]) ** 2 + (p[:, 1:2] - ly[None, :]) ** 2
    i = np.argmin(d2, axis=1)
    j = (i + 1) % len(lx)
    ex, ey = lx[j] - lx[i], ly[j] - ly[i]
    t = ((p[:, 0] - lx[i]) * ex + (p[:, 1] - ly[i]) * ey) / np.maximum(ex * ex + ey * ey, 1e-12)
    t = np.clip(t, -0.5, 1.5)
    seg = np.hypot(ex, ey)
    lateral = ((p[:, 0] - lx[i]) * ey - (p[:, 1] - ly[i]) * ex) / np.maximum(seg, 1e-12)
    return line_s[i] + t * seg, lateral



def minimum_curvature(track: Track, half_width: float, step: float = 4.0, k: int = 160) -> tuple[Track, np.ndarray]:
    """Minimum-curvature racing line inside a corridor of ±half_width around the reference line.

    Points move along the reference normals: p(s) = r(s) + n(s) N(s), |n| ≤ half_width. To first
    order in n, the curvature of the offset curve is κ_p ≈ κ + n'' + κ² n (sign convention: n and κ
    positive to the left), so the discretised objective Σ (κ_i + (D₂n)_i / Δs² + κ_i² n_i)² is a convex
    quadratic in n with box bounds — the minimum-curvature problem of Braghin et al. (2008) in the
    linearised form used by Heilmeier et al. (2019). It is solved by L-BFGS-B with the analytic
    gradient on a grid of ``step`` metres, and the result is re-fitted with the periodic Fourier
    smoother. Two passes re-linearise around the new line.

    Returns the new track and the lateral offset (m, positive to the left) on the reference grid.
    """
    from scipy.optimize import minimize

    m = int(round(track.length / step))
    sg = np.linspace(0, track.length, m, endpoint=False)
    rx = np.interp(sg, track.s, track.x, period=track.length)
    ry = np.interp(sg, track.s, track.y, period=track.length)
    rz = np.interp(sg, track.s, track.z, period=track.length)
    tx = np.roll(rx, -1) - np.roll(rx, 1)
    ty = np.roll(ry, -1) - np.roll(ry, 1)
    norm = np.hypot(tx, ty)
    nx, ny = -ty / norm, tx / norm

    kap = np.interp(sg, track.s, track.kappa, period=track.length)

    def d2(a):
        return np.roll(a, -1) - 2 * a + np.roll(a, 1)

    h2 = step * step

    def fun(n):
        e = kap + d2(n) / h2 + kap * kap * n
        g = 2 * (d2(e) / h2 + kap * kap * e)
        return e @ e, g

    sol = minimize(fun, np.zeros(m), jac=True, method="L-BFGS-B", bounds=[(-half_width, half_width)] * m,
                   options={"maxiter": 50000, "maxfun": 100000, "ftol": 1e-15, "gtol": 1e-12})
    px, py = rx + sol.x * nx, ry + sol.x * ny
    seg = np.hypot(np.diff(np.r_[px, px[0]]), np.diff(np.r_[py, py[0]]))
    s_new = np.concatenate([[0.0], np.cumsum(seg)[:-1]])
    new = build_track(s_new, px, py, rz, float(seg.sum()), k=k, ds=float(np.mean(track.ds)))
    offset = np.interp(track.s, sg, sol.x, period=track.length)
    return new, offset
