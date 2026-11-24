"""Pacejka Magic Formula tyre model (pure slip, MF 6.1 structure, no camber or turn slip).

Reference: H. B. Pacejka, *Tire and Vehicle Dynamics*, 3rd ed., Butterworth-Heinemann, 2012,
ch. 4 (Magic Formula) and the MF-Tyre 6.1 equations for load and inflation-pressure dependence.

Units: forces in N, slip angle in rad, slip ratio dimensionless, pressure in Pa.

The coefficients in :data:`RACE_SLICK` are a plausible *hypothesis* for a dry racing slick, chosen
to reproduce the order of magnitude reported in the literature (peak friction 1.6–1.9, peak slip
angle 6–9 degrees, falling friction with load). They are not measured on any real tyre.
The MF scaling factors ``lambda_muy`` and ``lambda_mux`` are what :mod:`vehicle_dynamics.calibrate`
identifies from telemetry; the curve shape is not identifiable from speed traces and stays as assumed.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np


@dataclass(frozen=True)
class MagicFormula:
    # nominal conditions
    fz0: float = 3500.0            # N, nominal load
    p0: float = 1.6e5              # Pa, nominal inflation pressure (gauge)
    # lateral, pure slip
    pCy1: float = 1.45             # shape factor C
    pDy1: float = 1.80             # peak friction at Fz0
    pDy2: float = -0.30            # load sensitivity of peak friction (per unit dfz)
    pEy1: float = -0.20            # curvature factor
    pKy1: float = 52.0             # max cornering stiffness / Fz0 (1/rad)
    pKy2: float = 2.6              # load at which Ky peaks / Fz0
    ppy1: float = -0.25            # pressure effect on Ky
    ppy2: float = 0.30             # pressure effect on Ky load at peak
    ppy3: float = -0.05            # pressure effect on mu (linear)
    ppy4: float = -0.40            # pressure effect on mu (quadratic); negative gives an optimum pressure
    # longitudinal, pure slip
    pCx1: float = 1.60
    pDx1: float = 1.90
    pDx2: float = -0.28
    pEx1: float = 0.10
    pKx1: float = 45.0             # slip stiffness / Fz (per unit slip)
    pKx2: float = -0.10
    lambda_muy: float = 1.0        # lateral friction scaling λ_μy (calibrated)
    lambda_mux: float = 1.0        # longitudinal friction scaling λ_μx (calibrated)

    def scaled(self, lambda_muy: float | None = None, lambda_mux: float | None = None) -> "MagicFormula":
        return replace(self, lambda_muy=float(self.lambda_muy if lambda_muy is None else lambda_muy),
                       lambda_mux=float(self.lambda_mux if lambda_mux is None else lambda_mux))

    # -- helpers ---------------------------------------------------------------------------------
    def _dfz(self, fz):
        return (np.asarray(fz, float) - self.fz0) / self.fz0

    def _dpi(self, p):
        return (np.asarray(p, float) - self.p0) / self.p0

    # -- lateral -----------------------------------------------------------------------------------
    def mu_y(self, fz, p=None):
        """Peak lateral friction coefficient D/Fz as a function of load and pressure."""
        dfz = self._dfz(fz)
        dpi = self._dpi(self.p0 if p is None else p)
        return (self.pDy1 + self.pDy2 * dfz) * (1 + self.ppy3 * dpi + self.ppy4 * dpi ** 2) * self.lambda_muy

    def cornering_stiffness(self, fz, p=None):
        """K_y = dFy/dalpha at alpha = 0 (N/rad), MF 6.1 form without camber."""
        fz = np.asarray(fz, float)
        dpi = self._dpi(self.p0 if p is None else p)
        return (self.pKy1 * self.fz0 * (1 + self.ppy1 * dpi)
                * np.sin(2.0 * np.arctan(fz / (self.pKy2 * (1 + self.ppy2 * dpi) * self.fz0))))

    def fy(self, alpha, fz, p=None):
        """Pure-slip lateral force (N); sign follows alpha."""
        fz = np.asarray(fz, float)
        C = self.pCy1
        D = self.mu_y(fz, p) * fz
        K = self.cornering_stiffness(fz, p)
        B = K / (C * D + 1e-12)
        E = np.minimum(self.pEy1, 1.0)
        x = B * np.asarray(alpha, float)
        return D * np.sin(C * np.arctan(x - E * (x - np.arctan(x))))

    def peak_slip_angle(self, fz, p=None):
        """Slip angle of the lateral force peak (rad), found numerically on a fine grid."""
        a = np.linspace(0.0, 0.35, 3501)
        f = self.fy(a, fz, p)
        return float(a[int(np.argmax(f))])

    # -- longitudinal --------------------------------------------------------------------------------
    def mu_x(self, fz):
        return (self.pDx1 + self.pDx2 * self._dfz(fz)) * self.lambda_mux

    def fx(self, kappa, fz):
        fz = np.asarray(fz, float)
        C = self.pCx1
        D = self.mu_x(fz) * fz
        K = fz * (self.pKx1 + self.pKx2 * self._dfz(fz))
        B = K / (C * D + 1e-12)
        E = min(self.pEx1, 1.0)
        x = B * np.asarray(kappa, float)
        return D * np.sin(C * np.arctan(x - E * (x - np.arctan(x))))

    # -- capacity used by the quasi-steady-state envelope ---------------------------------------------
    def capacity(self, fz):
        """Peak force capacities (Fx_max, Fy_max) in N at load fz; zero for unloaded tyres."""
        fz = np.maximum(np.asarray(fz, float), 0.0)
        return self.mu_x(fz) * fz, self.mu_y(fz) * fz


RACE_SLICK = MagicFormula()
