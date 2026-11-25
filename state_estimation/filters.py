"""Batched Extended and Unscented Kalman filters for the single-track model.

Batched means the same filter runs on N independent Monte Carlo realisations at once (arrays of
shape (N, n)), which makes consistency statistics (NEES, NIS) cheap to estimate.

Filter state:  x = [v_x, v_y, r, b_g]          (b_g gyro bias, random walk)
       or      x = [v_x, v_y, r, b_g, λ]       (λ lateral friction scale, random walk) — joint
                                                 estimation of the grip the car is using
Inputs:        u = [δ_meas, a_x,meas]
Measurements:  z = [r_gyro = r + b_g,  a_y,  v_x,wheel]

Prediction uses RK4 on the axle bicycle model (one step of length dt). EKF Jacobians are central
finite differences; the UKF uses the scaled unscented transform (Wan & van der Merwe, 2000) with
α = 0.5, β = 2, κ = 0. Joseph-form covariance update in the EKF; symmetrisation after every step.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .bicycle import BicycleParams, axle_loads, slip_angles


def fy_scaled(tyre, alpha, fz, lam):
    """Pure-slip lateral force with the friction scale λ given per sample (array), keeping K_y fixed."""
    C = tyre.pCy1
    mu0 = tyre.mu_y(fz) / tyre.lambda_muy
    D = mu0 * lam * fz
    K = tyre.cornering_stiffness(fz)
    B = K / (C * D + 1e-9)
    E = min(tyre.pEy1, 1.0)
    x = B * alpha
    return D * np.sin(C * np.arctan(x - E * (x - np.arctan(x))))


def fy_linear(tyre, alpha, fz, lam):
    """Linear tyre: F_y = K_y α, no saturation (the textbook linear bicycle)."""
    return tyre.cornering_stiffness(fz) * alpha


@dataclass
class Model:
    p: BicycleParams
    tyre: object
    dt: float
    augmented: bool = False     # estimate λ as a state
    lam_fixed: float = 1.0      # λ used when not augmented
    force: callable = fy_scaled

    @property
    def n(self) -> int:
        return 5 if self.augmented else 4

    def _deriv(self, x, u):
        vx, vy, r = x[..., 0], x[..., 1], x[..., 2]
        lam = x[..., 4] if self.augmented else np.full_like(vx, self.lam_fixed)
        delta, ax = u[..., 0], u[..., 1]
        af, ar = slip_angles(self.p, vx, vy, r, delta)
        fzf, fzr = axle_loads(self.p, vx, ax)
        fyf = 2 * self.force(self.tyre, af, fzf / 2, lam)
        fyr = 2 * self.force(self.tyre, ar, fzr / 2, lam)
        ay = (fyf * np.cos(delta) + fyr) / self.p.m
        d = np.zeros_like(x)
        d[..., 0] = ax + vy * r
        d[..., 1] = ay - vx * r
        d[..., 2] = (self.p.a * fyf * np.cos(delta) - self.p.b * fyr) / self.p.iz
        return d, ay

    def f(self, x, u):
        dt = self.dt
        k1, _ = self._deriv(x, u)
        k2, _ = self._deriv(x + 0.5 * dt * k1, u)
        k3, _ = self._deriv(x + 0.5 * dt * k2, u)
        k4, _ = self._deriv(x + dt * k3, u)
        return x + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)

    def h(self, x, u):
        _, ay = self._deriv(x, u)
        return np.stack([x[..., 2] + x[..., 3], ay, x[..., 0]], axis=-1)


def _sym(P):
    return 0.5 * (P + np.swapaxes(P, -1, -2))


def _jac(fun, x, u, eps):
    """Central-difference Jacobian of fun at x (batched): returns (N, m, n)."""
    n = x.shape[-1]
    cols = []
    for j in range(n):
        e = np.zeros(n)
        e[j] = eps[j]
        cols.append((fun(x + e, u) - fun(x - e, u)) / (2 * eps[j]))
    return np.stack(cols, axis=-1)


class EKF:
    def __init__(self, model: Model, Q, R, eps=None):
        self.m, self.Q, self.R = model, np.asarray(Q, float), np.asarray(R, float)
        self.eps = np.array([1e-3, 1e-4, 1e-5, 1e-6, 1e-4][:model.n]) if eps is None else eps

    def step(self, x, P, u_prev, u, z):
        F = _jac(self.m.f, x, u_prev, self.eps)
        xp = self.m.f(x, u_prev)
        Pp = _sym(F @ P @ np.swapaxes(F, -1, -2) + self.Q)
        H = _jac(self.m.h, xp, u, self.eps)
        nu = z - self.m.h(xp, u)
        S = _sym(H @ Pp @ np.swapaxes(H, -1, -2) + self.R)
        K = Pp @ np.swapaxes(H, -1, -2) @ np.linalg.inv(S)
        xn = xp + (K @ nu[..., None])[..., 0]
        I_KH = np.eye(self.m.n) - K @ H
        Pn = _sym(I_KH @ Pp @ np.swapaxes(I_KH, -1, -2) + K @ self.R @ np.swapaxes(K, -1, -2))
        return xn, Pn, nu, S


class UKF:
    def __init__(self, model: Model, Q, R, alpha=0.5, beta=2.0, kappa=0.0):
        self.m, self.Q, self.R = model, np.asarray(Q, float), np.asarray(R, float)
        n = model.n
        lam = alpha * alpha * (n + kappa) - n
        self.c = n + lam
        self.wm = np.full(2 * n + 1, 1.0 / (2 * self.c))
        self.wc = self.wm.copy()
        self.wm[0] = lam / self.c
        self.wc[0] = lam / self.c + (1 - alpha * alpha + beta)

    def _sigma(self, x, P):
        L = np.linalg.cholesky(self.c * _sym(P) + 1e-12 * np.eye(P.shape[-1]))
        cols = np.swapaxes(L, -1, -2)                   # rows = columns of L
        return np.concatenate([x[:, None, :], x[:, None, :] + cols, x[:, None, :] - cols], axis=1)

    def step(self, x, P, u_prev, u, z):
        X = self._sigma(x, P)                            # (N, 2n+1, n)
        Xp = self.m.f(X, u_prev[:, None, :])
        xp = np.einsum("k,nki->ni", self.wm, Xp)
        dX = Xp - xp[:, None, :]
        Pp = _sym(np.einsum("k,nki,nkj->nij", self.wc, dX, dX) + self.Q)
        X2 = self._sigma(xp, Pp)
        Z = self.m.h(X2, u[:, None, :])
        zp = np.einsum("k,nki->ni", self.wm, Z)
        dZ = Z - zp[:, None, :]
        dX2 = X2 - xp[:, None, :]
        S = _sym(np.einsum("k,nki,nkj->nij", self.wc, dZ, dZ) + self.R)
        C = np.einsum("k,nki,nkj->nij", self.wc, dX2, dZ)
        K = C @ np.linalg.inv(S)
        nu = z - zp
        xn = xp + (K @ nu[..., None])[..., 0]
        Pn = _sym(Pp - K @ S @ np.swapaxes(K, -1, -2))
        return xn, Pn, nu, S


def run(filt, x0, P0, U, Z):
    """Run a filter over a batch: U (N, T, 2), Z (N, T, 3). Returns states, covariances, NIS."""
    N, T, _ = Z.shape
    n = x0.shape[-1]
    xs = np.empty((N, T, n))
    Ps = np.empty((N, T, n, n))
    nis = np.empty((N, T))
    x, P = x0.copy(), P0.copy()
    xs[:, 0], Ps[:, 0], nis[:, 0] = x, P, np.nan
    for k in range(1, T):
        x, P, nu, S = filt.step(x, P, U[:, k - 1], U[:, k], Z[:, k])
        xs[:, k], Ps[:, k] = x, P
        nis[:, k] = np.einsum("ni,nij,nj->n", nu, np.linalg.inv(S), nu)
    return xs, Ps, nis
