"""Energy balance of an electric batch heat-treatment furnace (#029).

The furnace and its charge are hypothetical; the physics and the material data are standard:

1. **Walls.** Steady 1-D conduction through refractory layers whose conductivity varies linearly
   with temperature, k = k₀ + k₁T. For one layer the flux is exact: q·L = ∫k dT, so given the hot
   face temperature and q the cold face follows from a quadratic. The outer shell loses heat by
   natural convection and radiation, q = h_c(T_s)(T_s − T_∞) + εσ(T_s⁴ − T_sur⁴), with
   h_c from Churchill & Chu (1975) for vertical faces and the Incropera/Lloyd–Moran correlations
   for the roof (hot face up) and the underside (hot face down). Air properties from Sutherland's
   law at the film temperature. The flux q is the root of the residual (Brent's method).
2. **Open door.** Radiation from the near-isothermal chamber through an aperture of a thick wall
   whose jambs are refractory: with reradiating jambs the exchange factor is (1 + F₁₂)/2, where F₁₂
   is the view factor between the two aligned faces of the opening (Incropera, eq. 13.30 and
   table 13.2). Hot gas leaves through the top of the opening and room air enters at the bottom;
   the exchange flow is V̇ = (C_d W/3)·√(g′H³) with g′ = g Δρ/ρ̄ (Linden, 1999). The
   Boussinesq formula is stretched at an 835 K temperature difference: an order of magnitude.
3. **Charge.** Round bars heated by radiation and convection, 1-D radial conduction solved by
   implicit finite differences with the temperature-dependent specific heat and conductivity of
   carbon steel from EN 1993-1-2 (eq. 3.2 and 3.3), including the latent peak near 735 °C. The
   chamber holds its setpoint while the installed power allows; above that the chamber temperature
   is the root of the power balance at each step.
4. **Cold start.** Transient conduction in the multilayer wall (implicit, properties lagged one
   step) gives the heat stored in the lining and the time to reach steady losses.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace

import numpy as np
from scipy.optimize import brentq

SIGMA = 5.670374419e-8
G = 9.80665
K0 = 273.15


# ------------------------------------------------------------------------------------------------
# materials
# ------------------------------------------------------------------------------------------------
def air(T):
    """Dry air at 1 atm: density, viscosity, conductivity, c_p, Prandtl (T in K)."""
    T = np.asarray(T, float)
    mu = 1.716e-5 * (T / 273.15) ** 1.5 * (273.15 + 110.4) / (T + 110.4)
    k = 0.02414 * (T / 273.15) ** 1.5 * (273.15 + 194.0) / (T + 194.0)
    rho = 101325.0 / (287.05 * T)
    cp = 1006.0
    return rho, mu, k, cp, mu * cp / k


def steel_cp(T_c):
    """Specific heat of carbon steel, J/(kg K), EN 1993-1-2 eq. 3.2 (T in °C, 20–1200)."""
    T = np.clip(np.asarray(T_c, float), 20.0, 1200.0)
    return np.select(
        [T < 600, T < 735, T < 900],
        [425 + 0.773 * T - 1.69e-3 * T**2 + 2.22e-6 * T**3, 666 + 13002 / (738 - np.minimum(T, 737.9)),
         545 + 17820 / (np.maximum(T, 731.1) - 731)],
        650.0,
    )


def steel_k(T_c):
    """Thermal conductivity of carbon steel, W/(m K), EN 1993-1-2 eq. 3.3 (T in °C)."""
    T = np.asarray(T_c, float)
    return np.where(T < 800, 54 - 3.33e-2 * T, 27.3)


def steel_enthalpy(T1, T0=25.0, n=2000):
    """∫c_p dT in J/kg (trapezoid on a fine grid; the 735 °C peak is integrable)."""
    T = np.linspace(T0, T1, n)
    return float(np.trapezoid(steel_cp(T), T))


@dataclass(frozen=True)
class Layer:
    name: str
    L: float      # m
    k0: float     # W/(m K)
    k1: float     # W/(m K²), k = k0 + k1·T(°C)
    rho: float    # kg/m³
    cp: float     # J/(kg K)
    t_max: float  # °C, service limit

    def k(self, T):
        return self.k0 + self.k1 * np.asarray(T, float)

    def cold_face(self, T_hot, q):
        """Cold-face temperature for flux q through the layer (exact for linear k(T))."""
        a, b = self.k1 / 2, self.k0
        c = -(self.k0 * T_hot + self.k1 / 2 * T_hot**2 - q * self.L)
        if abs(a) < 1e-15:
            return -c / b
        return (-b + np.sqrt(b * b - 4 * a * c)) / (2 * a)


# Hypothetical lining, typical catalogue magnitudes (stated as hypotheses on the page).
LINING = (
    Layer("Tijolo isolante classe 26", 0.230, 0.17, 1.3e-4, 800.0, 1000.0, 1430.0),
    Layer("Placa de silicato de cálcio", 0.100, 0.05, 1.0e-4, 250.0, 1000.0, 1000.0),
    Layer("Carcaça de aço", 0.006, 45.0, 0.0, 7850.0, 480.0, 400.0),
)


# ------------------------------------------------------------------------------------------------
# natural convection on the shell
# ------------------------------------------------------------------------------------------------
def h_natural(Ts, Tinf, L, orientation):
    """Natural-convection coefficient (W/m²K) of an isothermal plate at Ts (°C) in still air."""
    if Ts <= Tinf:
        return 0.0
    Tf = (Ts + Tinf) / 2 + K0
    rho, mu, k, cp, Pr = air(Tf)
    nu, alpha = mu / rho, k / (rho * cp)
    Ra = G * (1 / Tf) * (Ts - Tinf) * L**3 / (nu * alpha)
    if orientation == "vertical":   # Churchill & Chu (1975), all Ra
        Nu = (0.825 + 0.387 * Ra ** (1 / 6) / (1 + (0.492 / Pr) ** (9 / 16)) ** (8 / 27)) ** 2
    elif orientation == "up":       # hot surface facing up, L = A/P
        Nu = 0.54 * Ra**0.25 if Ra < 1e7 else 0.15 * Ra ** (1 / 3)
    elif orientation == "down":     # hot surface facing down, L = A/P
        Nu = 0.52 * Ra**0.2
    else:
        raise ValueError(orientation)
    return float(Nu * k / L)


def q_out(Ts, face, Tinf, eps):
    return h_natural(Ts, Tinf, face.L_char, face.orientation) * (Ts - Tinf) + eps * SIGMA * ((Ts + K0) ** 4 - (Tinf + K0) ** 4)


@dataclass(frozen=True)
class Face:
    name: str
    area: float        # m², mean of inner and outer areas
    L_char: float      # m, convection length
    orientation: str


def wall_steady(T_hot, face, lining=LINING, Tinf=25.0, eps=0.9):
    """Steady flux q (W/m²), shell temperature and interface temperatures for one face."""

    def chain(q):
        T = [T_hot]
        for lay in lining:
            T.append(lay.cold_face(T[-1], q))
        return T

    def resid(q):
        Ts = chain(q)[-1]
        return q - q_out(Ts, face, Tinf, eps)

    ok = lambda q: bool(np.isfinite(chain(q)[-1]) and chain(q)[-1] > Tinf)
    lo, hi = 1.0, 20000.0           # bisect the largest flux whose shell stays warmer than the room
    with np.errstate(invalid="ignore"):
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if ok(mid) else (lo, mid)
        q = brentq(resid, 1.0, lo, xtol=1e-6)
    T = chain(q)
    return {"q": q, "Ts": T[-1], "interfaces": T, "Q": q * face.area}


# ------------------------------------------------------------------------------------------------
# furnace
# ------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Furnace:
    W: float = 1.0           # inner width, m
    H: float = 1.0           # inner height, m
    D: float = 1.5           # inner depth, m
    T_set: float = 860.0     # °C
    T_amb: float = 25.0
    eps_shell: float = 0.9
    door_w: float = 0.8      # opening, m
    door_h: float = 0.7
    Cd: float = 0.6          # discharge coefficient of the doorway
    door_open_s: float = 180.0   # per cycle (unload + load)
    P_max: float = 120e3     # installed heating power, W
    h_in: float = 15.0       # W/m²K, lining → chamber gas while the door is open
    lining: tuple = field(default=LINING)

    @property
    def wall_L(self):
        return sum(l.L for l in self.lining)

    def faces(self):
        L = self.wall_L
        W2, H2, D2 = self.W + 2 * L, self.H + 2 * L, self.D + 2 * L
        mean = lambda a, b: 0.5 * (a + b)
        return [
            Face("Paredes laterais", 2 * mean(self.H * self.D, H2 * D2), H2, "vertical"),
            Face("Frente e fundo", 2 * mean(self.W * self.H, W2 * H2), H2, "vertical"),
            Face("Teto", mean(self.W * self.D, W2 * D2), W2 * D2 / (2 * (W2 + D2)), "up"),
            Face("Base (suspensa)", mean(self.W * self.D, W2 * D2), W2 * D2 / (2 * (W2 + D2)), "down"),
        ]

    def wall_losses(self, T=None):
        T = self.T_set if T is None else T
        out = {f.name: wall_steady(T, f, self.lining, self.T_amb, self.eps_shell) for f in self.faces()}
        return out

    def wall_loss_W(self, T=None):
        return sum(v["Q"] for v in self.wall_losses(T).values())

    def door(self, T=None, h_in=None):
        """Radiative and convective loss (W) while the door is open.

        Convection: the doorway exchange flow V̇ = (C_d W/3)√(g′H³) brings room air in; the chamber
        gas is taken as well mixed and heated by the hot lining with coefficient h_in, so its
        temperature T_g solves ρ_o V̇ c_p (T_g − T_∞) = h_in A_in (T − T_g), with V̇ itself depending
        on T_g. Without that limit (T_g = T) the loss would be several times the installed power.
        """
        T = self.T_set if T is None else T
        h_in = self.h_in if h_in is None else h_in
        X, Y = self.door_w / self.wall_L, self.door_h / self.wall_L
        F12 = view_factor_parallel(X, Y)
        Fbar = (1 + F12) / 2
        A = self.door_w * self.door_h
        q_rad = Fbar * A * SIGMA * ((T + K0) ** 4 - (self.T_amb + K0) ** 4)
        rho_o = float(air(self.T_amb + K0)[0])
        A_in = 2 * (self.W * self.H + self.W * self.D + self.H * self.D)

        def flow(Tg):
            rho_i = float(air(Tg + K0)[0])
            g_red = G * (rho_o - rho_i) / (0.5 * (rho_o + rho_i))
            return self.Cd * self.door_w / 3 * np.sqrt(max(g_red, 0.0) * self.door_h**3)

        Tg = T
        for _ in range(100):  # fixed point on the gas temperature
            mcp = rho_o * flow(Tg) * 1006.0
            Tg_new = (h_in * A_in * T + mcp * self.T_amb) / (h_in * A_in + mcp)
            if abs(Tg_new - Tg) < 1e-6:
                break
            Tg = 0.5 * (Tg + Tg_new)
        V = flow(Tg)
        q_conv = rho_o * V * 1006.0 * (Tg - self.T_amb)
        gas = float(air(T + K0)[0]) * self.W * self.H * self.D * 1006.0 * (T - self.T_amb)  # initial hot gas purged
        q_unlimited = rho_o * flow(T) * 1006.0 * (T - self.T_amb)
        return {"F12": F12, "Fbar": Fbar, "rad": q_rad, "conv": q_conv, "V": V, "T_gas": Tg,
                "purge_J": gas, "conv_unlimited": q_unlimited}


def view_factor_parallel(X, Y):
    """View factor between aligned parallel rectangles a×b at distance L, X=a/L, Y=b/L (Incropera table 13.2)."""
    Xb, Yb = np.sqrt(1 + X * X), np.sqrt(1 + Y * Y)
    return float(2 / (np.pi * X * Y) * (
        np.log(np.sqrt((1 + X * X) * (1 + Y * Y) / (1 + X * X + Y * Y)))
        + X * Yb * np.arctan(X / Yb) + Y * Xb * np.arctan(Y / Xb) - X * np.arctan(X) - Y * np.arctan(Y)))


# ------------------------------------------------------------------------------------------------
# charge heating
# ------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Charge:
    mass: float = 500.0          # kg
    radius: float = 0.040        # m, round bars Ø80
    rho: float = 7850.0
    eps: float = 0.7             # oxidized steel (EN 1993-1-2 uses 0.7 for carbon steel)
    exposure: float = 0.6        # fraction of the bar surface that sees the chamber (packing)
    h_conv: float = 10.0         # W/m²K, still furnace atmosphere
    T0: float = 25.0
    T_core_target: float = 850.0
    soak_s: float = 1800.0

    @property
    def area(self):
        length = self.mass / (self.rho * np.pi * self.radius**2)
        return 2 * np.pi * self.radius * length


def heat_charge(furn: Furnace, ch: Charge, nr=21, dt=10.0, t_max=6 * 3600):
    """Implicit radial FD; returns time series and energy terms (J). Door open at start and end."""
    r = np.linspace(0, ch.radius, nr)
    dr = r[1] - r[0]
    T = np.full(nr, ch.T0)
    # control volumes: node i owns [r_i - dr/2, r_i + dr/2] clipped to [0, R]
    rf = np.concatenate([[0.0], 0.5 * (r[1:] + r[:-1]), [ch.radius]])
    vol = np.pi * (rf[1:] ** 2 - rf[:-1] ** 2)                 # per metre of bar
    per_m = ch.mass / (ch.rho * np.pi * ch.radius**2)            # bar length, m
    A_s = ch.area
    Qw_set = furn.wall_loss_W()
    # wall loss vs chamber temperature (quasi-steady, walls already hot), interpolated
    Tg = np.linspace(furn.T_set - 400, furn.T_set, 21)
    Qw_tab = np.array([furn.wall_loss_W(t) for t in Tg])
    wall_at = lambda Tc: float(np.interp(Tc, Tg, Qw_tab))

    def q_surface(Tc, Ts):
        return ch.exposure * ch.eps * SIGMA * ((Tc + K0) ** 4 - (Ts + K0) ** 4) + ch.h_conv * (Tc - Ts)

    t, rows, soak_left = 0.0, [], None
    E = dict(charge=0.0, wall=0.0, total=0.0)
    while t < t_max:
        Ts = T[-1]
        need = q_surface(furn.T_set, Ts) * A_s + Qw_set
        if need <= furn.P_max:
            Tc, P = furn.T_set, need
        else:  # power-limited: chamber temperature solves P_max = charge + walls
            Tc = brentq(lambda x: q_surface(x, Ts) * A_s + wall_at(x) - furn.P_max, Ts + 1e-6, furn.T_set)
            P = furn.P_max
        qs = q_surface(Tc, Ts)
        # implicit step with properties at the previous temperature
        k = steel_k(T)
        C = ch.rho * steel_cp(T) * vol / dt
        kf = 0.5 * (k[1:] + k[:-1])
        cond = 2 * np.pi * rf[1:-1] * kf / dr                    # W/(K m) between nodes
        A = np.diag(C.copy())
        A[np.arange(nr - 1), np.arange(1, nr)] -= cond
        A[np.arange(1, nr), np.arange(nr - 1)] -= cond
        A[np.arange(nr - 1), np.arange(nr - 1)] += cond
        A[np.arange(1, nr), np.arange(1, nr)] += cond
        b = C * T
        b[-1] += qs * 2 * np.pi * ch.radius
        T_new = np.linalg.solve(A, b)
        dE = float(np.sum(ch.rho * steel_cp(0.5 * (T + T_new)) * vol * (T_new - T)) * per_m)
        E["charge"] += dE
        E["wall"] += wall_at(Tc) * dt
        E["total"] += P * dt
        T = T_new
        t += dt
        rows.append((t, T[0], T[-1], Tc, P))
        if soak_left is None and T[0] >= ch.T_core_target:
            soak_left = ch.soak_s
            t_core = t
        if soak_left is not None:
            soak_left -= dt
            if soak_left <= 0:
                break
    else:
        raise RuntimeError("charge did not reach the core target")
    d = furn.door()
    E["door_rad"] = d["rad"] * furn.door_open_s
    E["door_conv"] = d["conv"] * furn.door_open_s + 2 * d["purge_J"]   # two openings per cycle
    E_door = E["door_rad"] + E["door_conv"]
    E["total"] += E_door
    ts = np.array(rows)
    return {"t": ts[:, 0], "T_core": ts[:, 1], "T_surf": ts[:, 2], "T_chamber": ts[:, 3], "P": ts[:, 4],
            "t_core": t_core, "t_cycle": t + furn.door_open_s, "E": E, "T_mean_final": float(np.sum(T * vol) / np.sum(vol)),
            "power_limited_s": float(np.sum(ts[:, 4] >= furn.P_max - 1e-6) * dt)}


# ------------------------------------------------------------------------------------------------
# cold start of the lining
# ------------------------------------------------------------------------------------------------
def lining_transient(furn: Furnace, hours, T_init=None, mode="ramp", ramp_K_per_h=150.0, dt=60.0, dx=0.005):
    """Transient multilayer wall, per m² of one vertical face.

    mode="ramp": hot face follows min(T_set, T_start + ramp·t) — a start-up (T_start = hot-face
    temperature of the initial profile). mode="hold": hot face fixed at T_set.
    mode="off": heating off, chamber closed — hot face adiabatic (the chamber's own capacity is
    neglected). Returns heat in through the hot face, heat out through the shell and stored heat.
    """
    xs, props = [], []
    for lay in furn.lining:
        n = max(2, int(round(lay.L / dx)))
        edges = np.linspace(0, lay.L, n + 1) + (xs[-1][-1] if xs else 0.0)
        xs.append(edges)
        props += [lay] * n
    edges = np.concatenate([xs[0]] + [e[1:] for e in xs[1:]])
    dxs = np.diff(edges)
    n = len(dxs)
    T = np.full(n, furn.T_amb) if T_init is None else np.array(T_init, float)
    T_start = T[0]
    face = furn.faces()[0]
    rhoc = np.array([p.rho * p.cp for p in props]) * dxs
    steps = int(round(hours * 3600 / dt))
    q_in, q_out_, stored = [], [], []
    for s_ in range(steps):
        t = (s_ + 1) * dt
        k = np.array([p.k(Ti) for p, Ti in zip(props, T)])
        g = 1 / (dxs[:-1] / (2 * k[:-1]) + dxs[1:] / (2 * k[1:]))
        g_hot = 2 * k[0] / dxs[0]
        Ts = T[-1]
        h_tot = (h_natural(Ts, furn.T_amb, face.L_char, face.orientation)
                 + furn.eps_shell * SIGMA * ((Ts + K0) ** 2 + (furn.T_amb + K0) ** 2) * (Ts + furn.T_amb + 2 * K0))
        g_out = 1 / (dxs[-1] / (2 * k[-1]) + 1 / max(h_tot, 1e-9))
        A = np.diag(rhoc / dt)
        b = rhoc / dt * T
        A[np.arange(n - 1), np.arange(1, n)] -= g
        A[np.arange(1, n), np.arange(n - 1)] -= g
        A[np.arange(n - 1), np.arange(n - 1)] += g
        A[np.arange(1, n), np.arange(1, n)] += g
        if mode != "off":
            T_hot = furn.T_set if mode == "hold" else min(furn.T_set, T_start + ramp_K_per_h * t / 3600)
            A[0, 0] += g_hot
            b[0] += g_hot * T_hot
        A[-1, -1] += g_out
        b[-1] += g_out * furn.T_amb
        T = np.linalg.solve(A, b)
        q_in.append(g_hot * (T_hot - T[0]) if mode != "off" else 0.0)
        q_out_.append(g_out * (T[-1] - furn.T_amb))
        stored.append(float(np.sum(rhoc * (T - furn.T_amb))))
    return {"t_h": np.arange(1, steps + 1) * dt / 3600, "q_in": np.array(q_in), "q_out": np.array(q_out_),
            "stored_J_m2": np.array(stored), "T": T, "x": 0.5 * (edges[1:] + edges[:-1]), "dt": dt}


def steady_profile(furn: Furnace, hours=400.0):
    """Lining profile after a long hold at T_set (used as the hot, steady starting state)."""
    return lining_transient(furn, hours, mode="hold", dt=600.0)["T"]


def weekend(furn: Furnace, stop_hours=48.0, ready_ratio=1.5, tail_hours=72.0):
    """Hold the furnace hot through a production stop, or switch it off and reheat in time?

    Option A holds T_set for the whole stop. Option B switches off for x hours, then ramps the hot
    face at 150 K/h and holds; the furnace is ready when the hot face is at T_set and the lining
    absorbs at most ``ready_ratio`` × the steady loss. x is the longest off time that is ready by
    the end of the stop (bisection). Both options are integrated to the same horizon, stop +
    ``tail_hours``, so the heat the lining still absorbs after restart is charged to option B.
    Energies are for the whole furnace (per-m² result × mean lining area).
    """
    A = mean_wall_area(furn)
    T_hot = steady_profile(furn)
    H = stop_hours + tail_hours
    q_ss = float(lining_transient(furn, 1.0, T_init=T_hot, mode="hold")["q_in"][-1])

    def option_b(x):
        cool = lining_transient(furn, x, T_init=T_hot, mode="off") if x > 0 else {"T": T_hot}
        re = lining_transient(furn, H - x, T_init=cool["T"], mode="ramp")
        hot = re["t_h"] >= (furn.T_set - cool["T"][0]) / 150.0
        ready = hot & (re["q_in"] <= ready_ratio * q_ss)
        t_ready = float(re["t_h"][np.argmax(ready)]) if ready.any() else np.inf
        return x + t_ready, float(np.sum(re["q_in"]) * re["dt"]) * A, cool["T"][0], t_ready

    lo, hi = 0.0, stop_hours
    if option_b(0.0)[0] > stop_hours:
        lo = hi = 0.0
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if option_b(mid)[0] <= stop_hours:
            lo = mid
        else:
            hi = mid
        if hi - lo < 0.25:
            break
    ready_at, E_b, T_face, t_ready = option_b(lo)
    E_a = q_ss * H * 3600 * A
    return {"stop_h": stop_hours, "off_h": lo, "reheat_h": t_ready, "ready_at_h": ready_at,
            "hold_kwh": E_a / 3.6e6, "off_kwh": E_b / 3.6e6, "saving_kwh": (E_a - E_b) / 3.6e6,
            "T_face_min": float(T_face), "horizon_h": H, "q_ss": q_ss, "area": A}


def mean_wall_area(furn: Furnace):
    return sum(f.area for f in furn.faces())


def monte_carlo(n=400, seed=29, charge=Charge(), base=Furnace()):
    """Propagate the uncertain inputs to energy per tonne; returns samples and standardized rank coefficients."""
    rng = np.random.default_rng(seed)
    names = ["k do tijolo (×)", "k da placa (×)", "emissividade da carcaça", "emissividade da carga",
             "exposição da carga", "Cd da porta", "tempo de porta aberta (s)", "h interno com a porta aberta"]
    X = np.column_stack([rng.uniform(0.8, 1.2, n), rng.uniform(0.8, 1.2, n), rng.uniform(0.8, 0.95, n),
                         rng.uniform(0.6, 0.85, n), rng.uniform(0.45, 0.75, n), rng.uniform(0.5, 0.7, n),
                         rng.uniform(120, 300, n), rng.uniform(8, 25, n)])
    y, tcyc = np.empty(n), np.empty(n)
    for i, x in enumerate(X):
        lin = (replace(LINING[0], k0=LINING[0].k0 * x[0], k1=LINING[0].k1 * x[0]),
               replace(LINING[1], k0=LINING[1].k0 * x[1], k1=LINING[1].k1 * x[1]), LINING[2])
        f = replace(base, lining=lin, eps_shell=x[2], Cd=x[5], door_open_s=x[6], h_in=x[7])
        c = replace(charge, eps=x[3], exposure=x[4])
        r = heat_charge(f, c, dt=20.0)
        y[i] = r["E"]["total"] / 3.6e6 / (c.mass / 1000)
        tcyc[i] = r["t_cycle"] / 3600
    # standardized rank regression coefficients (Saltelli et al., 2004)
    rank = lambda a: np.argsort(np.argsort(a, axis=0), axis=0).astype(float)
    Rx, ry = rank(X), rank(y)
    Rx = (Rx - Rx.mean(0)) / Rx.std(0)
    ry = (ry - ry.mean()) / ry.std()
    beta, *_ = np.linalg.lstsq(np.column_stack([np.ones(n), Rx]), ry, rcond=None)
    fit = np.column_stack([np.ones(n), Rx]) @ beta
    r2 = 1 - np.sum((ry - fit) ** 2) / np.sum(ry**2)
    return {"names": names, "kwh_t": y, "t_cycle_h": tcyc, "srrc": beta[1:], "r2": float(r2)}
