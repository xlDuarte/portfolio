"""Specific cutting energy (Kienzle) and machine-tool electricity (Gutowski) for #029.

**Cutting force.** Kienzle (1952): F_c = k_c1.1 · b · h^(1 − m_c), with chip width b = a_p/sin κ
and uncut chip thickness h = f·sin κ (turning). The specific energy of the cut is then

    u = F_c v_c / (a_p f v_c) = k_c1.1 · h^(−m_c)        [N/mm² ≡ mJ/mm³]

so thicker chips remove metal with less energy per mm³ (size effect).

**Machine electricity.** Gutowski et al. (2006): P = P₀ + k·ṽ — a constant power to keep the
machine ready (P₀) plus a term proportional to the material removal rate ṽ. With the Kienzle
term divided by the drive efficiency η, the electricity per volume is

    e = P₀/ṽ + u/η                                        [J/mm³]

which falls steeply with removal rate when P₀ dominates.

Coefficients. Catalogue values per VDI 3323 material group (ISCAR technical guide, "Materials
group" table) and the measured Ck45 coefficients of Klippel et al. (ETH Zürich, 2022,
arXiv:2209.04197, table C.17, dry orthogonal cutting, rake 0°), which spread with cutting speed.
The lathe (P₀, η) is hypothetical.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# ISCAR / VDI 3323, non-alloy and low-alloy steels: (label, tensile strength MPa, kc1 N/mm², mc)
VDI3323 = [
    ("Aço carbono < 0,25 % C, recozido", 420, 1350, 0.21),
    ("Aço carbono ≥ 0,25 % C, recozido", 650, 1500, 0.22),
    ("Aço carbono < 0,55 % C, temperado e revenido", 850, 1675, 0.24),
    ("Aço carbono ≥ 0,55 % C, recozido", 750, 1700, 0.24),
    ("Aço carbono ≥ 0,55 % C, temperado e revenido", 1000, 1900, 0.24),
    ("Aço baixa liga, recozido", 600, 1775, 0.24),
]

# Klippel et al. (2022), Ck45, table C.17 — values as published (one per tested cutting speed).
CK45_ETH_KC = [1935, 1803, 1417, 1729, 1672, 1707, 1716, 1794, 1851, 1575, 1368]
CK45_ETH_MC = [0.19, 0.17, 0.51, 0.35, 0.32, 0.28, 0.26, 0.22, 0.22, 0.27, 0.29]
CK45_TENSILE_MPA = 671


def specific_energy(h_mm, kc11, mc):
    """J/mm³ for uncut chip thickness h (mm); k_c in N/mm² is mJ/mm³, hence the 1e-3."""
    return 1e-3 * kc11 * np.asarray(h_mm, float) ** (-mc)


@dataclass(frozen=True)
class Lathe:
    P0: float = 4000.0     # W, machine ready (spindle, hydraulics, coolant, controls)
    eta: float = 0.80      # spindle drive efficiency
    P_spindle_max: float = 22e3


def turning_pass(d0_mm, d1_mm, length_mm, vc_m_min, f_mm, kappa_deg=95.0, kc11=1500, mc=0.22, lathe=Lathe()):
    """One longitudinal pass: power, time and electricity."""
    ap = (d0_mm - d1_mm) / 2
    k = np.radians(kappa_deg)
    h = f_mm * np.sin(k)
    b = ap / np.sin(k)
    Fc = kc11 * b * h ** (1 - mc)                        # N
    Pc = Fc * vc_m_min / 60                              # W
    mrr = vc_m_min * 1000 / 60 * f_mm * ap               # mm³/s (at the mean diameter ≈ d0)
    vol = np.pi / 4 * (d0_mm**2 - d1_mm**2) * length_mm  # mm³
    t = vol / mrr
    P = lathe.P0 + Pc / lathe.eta
    return {"ap": ap, "h": h, "Fc": Fc, "Pc": Pc, "mrr": mrr, "vol": vol, "t": t, "P": P,
            "E_J": P * t, "e_J_mm3": P / mrr, "u_J_mm3": Pc / mrr, "feasible": Pc / lathe.eta <= lathe.P_spindle_max}


def removal_rate_sweep(kc11, mc, lathe=Lathe(), ap=5.0, vc=200.0, feeds=np.linspace(0.05, 0.5, 46)):
    rows = [turning_pass(80, 80 - 2 * ap, 1000, vc, f, kc11=kc11, mc=mc, lathe=lathe) for f in feeds]
    return {"f": feeds, "mrr": np.array([r["mrr"] for r in rows]), "e": np.array([r["e_J_mm3"] for r in rows]),
            "u": np.array([r["u_J_mm3"] for r in rows]), "share_idle": np.array([lathe.P0 / r["P"] for r in rows]),
            "feasible": np.array([r["feasible"] for r in rows])}
