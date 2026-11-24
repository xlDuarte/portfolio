"""Vehicle kinematics and a lumped brake-disc thermal model from OpenF1 samples.

Used by ``scripts/build_hero_data.py``. Everything here is deterministic and vectorised with
NumPy/SciPy; no randomness and no network access.

Kinematics
    Positions (decimetres) and telemetry are resampled onto a uniform clock. Speed comes from
    the car's own speed channel (more accurate than differentiating noisy positions); heading
    comes from the smoothed path. Savitzky-Golay filters give smoothed values and derivatives
    in one step, which avoids the noise amplification of finite differences.

        a_long = dv/dt
        a_lat  = v * dpsi/dt       (psi = heading, unwrapped; positive = turning left)

    Known bias: OpenF1 car data arrives at ~3.7 Hz, so the 1.25 s (speed) and 1.75 s (path)
    windows attenuate short peaks. Expect braking peaks of -3 to -4 g where onboard loggers
    would show about -5 g. The values are shown as "estimated from public data".

Brake disc thermal model (illustrative estimate, not a measurement)
    One front disc as a single thermal mass:

        m c dT/dt = eta * P_disc(t) - h(v) A (T - T_amb) - eps sigma A (T^4 - T_amb^4)

    with P_disc = share of the braking power that is not supplied by aerodynamic drag:

        F_brake = max(0, -m_car a_long - 0.5 rho CdA v^2),  P_disc = F_brake * v * bias_front / 2

    Integrated with classical RK4. Every parameter is declared in ``BrakeDiscModel``.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.signal import savgol_filter

G0 = 9.80665                  # m/s^2, standard gravity
SIGMA = 5.670374419e-8        # W/(m^2 K^4), Stefan-Boltzmann constant
KELVIN = 273.15


@dataclass(frozen=True)
class Kinematics:
    t: np.ndarray             # s, uniform clock
    speed: np.ndarray         # m/s, smoothed
    a_long: np.ndarray        # m/s^2
    a_lat: np.ndarray         # m/s^2

    @property
    def a_long_g(self) -> np.ndarray:
        return self.a_long / G0

    @property
    def a_lat_g(self) -> np.ndarray:
        return self.a_lat / G0


def resample_linear(t_src: np.ndarray, values: np.ndarray, t_dst: np.ndarray) -> np.ndarray:
    """Linear interpolation, clamped at the ends."""
    return np.interp(t_dst, t_src, values)


def resample_hold(t_src: np.ndarray, values: np.ndarray, t_dst: np.ndarray) -> np.ndarray:
    """Zero-order hold: the last known value (for discrete channels such as gear or brake)."""
    idx = np.clip(np.searchsorted(t_src, t_dst, side="right") - 1, 0, len(values) - 1)
    return values[idx]


def kinematics(t: np.ndarray, x_m: np.ndarray, y_m: np.ndarray, speed_ms: np.ndarray,
               speed_window: int = 5, path_window: int = 7) -> Kinematics:
    """Longitudinal and lateral acceleration on a uniform clock ``t``."""
    if len(t) < max(speed_window, path_window):
        raise ValueError("series shorter than the smoothing window")
    dt = float(np.median(np.diff(t)))
    if not np.allclose(np.diff(t), dt, rtol=1e-6, atol=1e-9):
        raise ValueError("kinematics() needs a uniform clock")
    v = savgol_filter(speed_ms, speed_window, 2)
    a_long = savgol_filter(speed_ms, speed_window, 2, deriv=1, delta=dt)
    vx = savgol_filter(x_m, path_window, 3, deriv=1, delta=dt)
    vy = savgol_filter(y_m, path_window, 3, deriv=1, delta=dt)
    heading = np.unwrap(np.arctan2(vy, vx))
    yaw_rate = savgol_filter(heading, path_window, 2, deriv=1, delta=dt)
    return Kinematics(t=t, speed=np.maximum(v, 0.0), a_long=a_long, a_lat=np.maximum(v, 0.0) * yaw_rate)


@dataclass(frozen=True)
class BrakeDiscModel:
    """Declared parameters. Values are engineering estimates for a 2024 F1 car, not team data."""
    car_mass_kg: float = 880.0          # 798 kg minimum incl. driver + ~80 kg fuel early in the race
    front_bias: float = 0.57            # share of braking force on the front axle
    heat_to_disc: float = 0.80          # share of friction heat that goes into the disc (rest: pads, caliper)
    disc_mass_kg: float = 1.3           # carbon-carbon front disc
    disc_c: float = 1400.0              # J/(kg K), carbon-carbon specific heat at high temperature
    area_m2: float = 0.16               # effective convective/radiative area incl. ventilation holes
    emissivity: float = 0.85
    h0: float = 40.0                    # W/(m^2 K), still-air convection
    h1: float = 6.0                     # W/(m^2 K) per m/s, forced convection through the brake duct
    air_density: float = 1.16           # kg/m^3, ~30 °C at sea level
    cda_m2: float = 1.3                 # drag area
    ambient_c: float = 25.0
    spin_up_passes: int = 3             # repeat the window to approach a periodic steady state
    substeps: int = 5                   # RK4 steps per sample interval
    notes: tuple[str, ...] = field(default=(
        "Illustrative lumped model; engine braking, pad wear and duct opening are ignored.",
        "Initial temperature: end state of the previous pass (periodic steady-state approximation).",
    ))

    def disc_power(self, speed: np.ndarray, a_long: np.ndarray) -> np.ndarray:
        drag = 0.5 * self.air_density * self.cda_m2 * speed ** 2
        f_brake = np.maximum(0.0, -self.car_mass_kg * a_long - drag)
        return f_brake * speed * self.front_bias / 2.0

    def _dTdt(self, temp_k: float, power: float, speed: float) -> float:
        amb = self.ambient_c + KELVIN
        h = self.h0 + self.h1 * speed
        loss = h * self.area_m2 * (temp_k - amb) + self.emissivity * SIGMA * self.area_m2 * (temp_k ** 4 - amb ** 4)
        return (self.heat_to_disc * power - loss) / (self.disc_mass_kg * self.disc_c)

    def simulate(self, t: np.ndarray, speed: np.ndarray, a_long: np.ndarray, start_c: float = 500.0) -> np.ndarray:
        """Disc temperature in °C at every sample of ``t`` (classical RK4 with linear input hold)."""
        power = self.disc_power(speed, a_long)
        temp = start_c + KELVIN
        out = np.empty_like(t, dtype=float)
        for _ in range(self.spin_up_passes):
            out[0] = temp
            for i in range(len(t) - 1):
                h = (t[i + 1] - t[i]) / self.substeps
                for s in range(self.substeps):
                    f0, f1 = s / self.substeps, (s + 0.5) / self.substeps
                    p0, p1 = power[i] + (power[i + 1] - power[i]) * f0, power[i] + (power[i + 1] - power[i]) * f1
                    p2 = power[i] + (power[i + 1] - power[i]) * (s + 1) / self.substeps
                    v0, v1 = speed[i] + (speed[i + 1] - speed[i]) * f0, speed[i] + (speed[i + 1] - speed[i]) * f1
                    v2 = speed[i] + (speed[i + 1] - speed[i]) * (s + 1) / self.substeps
                    k1 = self._dTdt(temp, p0, v0)
                    k2 = self._dTdt(temp + 0.5 * h * k1, p1, v1)
                    k3 = self._dTdt(temp + 0.5 * h * k2, p1, v1)
                    k4 = self._dTdt(temp + h * k3, p2, v2)
                    temp += h / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
                out[i + 1] = temp
        return out - KELVIN
