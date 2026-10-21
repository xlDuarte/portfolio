#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project #109: F1 & Motorsport Telemetry Race Replay & Live GPS Track Position Engine
Built 100% from Scratch — Original Mathematical & Kinematic Architecture
Author: Gabriel Reis Duarte (@gabrielrduarte)
Stack: Python, Parametric Circuit Splines, Kinematic Velocity Profiler, Multi-Car Telemetry Sync

Description:
Reconstructs a multi-car motorsport race session from scratch using arc-length parameterized
circuit geometry C(s) = (X(s), Y(s), kappa(s)) modeled on Interlagos (4,309 m, 15 turns,
3 sectors, 2 DRS zones). Computes physics-informed speed, RPM, gear, throttle, brake pressure,
tyre compound degradation, and real-time interval gaps (Delta-t) at 20 Hz.
"""

import math
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class CarEntry:
    car_number: str
    driver_code: str
    team_name: str
    compound: str        # SOFT, MEDIUM, HARD, INTER
    base_grip_mu: float  # peak friction coefficient
    power_factor: float  # engine/aero efficiency multiplier
    tyre_age_laps: int


class ParametricCircuitEngine:
    """
    Generates closed-loop 2D track coordinates (x, y) and local curvature kappa(s)
    parameterized by normalized lap distance u = s / L in [0, 1].
    """
    def __init__(self, track_name="Interlagos GP Circuit", length_m=4309.0):
        self.track_name = track_name
        self.length_m = length_m
        # Control harmonics representing Interlagos-like elevation & corner complexes
        self.harmonics_x = [(1, 420.0, 0.0), (2, 135.0, 0.8), (3, -75.0, 1.9), (5, 42.0, -0.6)]
        self.harmonics_y = [(1, 260.0, -1.4), (2, -110.0, 0.3), (4, 68.0, 1.1), (6, -32.0, 2.2)]

    def sample_point(self, s_meters: float) -> Dict[str, float]:
        u = (s_meters % self.length_m) / self.length_m
        theta = 2.0 * math.pi * u
        x = sum(amp * math.cos(k * theta + ph) for k, amp, ph in self.harmonics_x)
        y = sum(amp * math.sin(k * theta + ph) for k, amp, ph in self.harmonics_y)

        # First and second derivatives wrt theta for curvature kappa
        dx = sum(-k * amp * math.sin(k * theta + ph) for k, amp, ph in self.harmonics_x)
        dy = sum(k * amp * math.cos(k * theta + ph) for k, amp, ph in self.harmonics_y)
        ddx = sum(-(k ** 2) * amp * math.cos(k * theta + ph) for k, amp, ph in self.harmonics_x)
        ddy = sum(-(k ** 2) * amp * math.sin(k * theta + ph) for k, amp, ph in self.harmonics_y)

        denom = math.pow(dx * dx + dy * dy, 1.5) or 1.0
        curvature = abs(dx * ddy - dy * ddx) / denom
        sector = 1 if u < 0.29 else (2 if u < 0.74 else 3)
        drs_active_zone = 1 if (0.14 <= u <= 0.27 or 0.78 <= u <= 0.96) else 0
        return {
            "s_m": round(s_meters % self.length_m, 1),
            "u_norm": round(u, 4),
            "x_m": round(x, 2),
            "y_m": round(y, 2),
            "curvature": round(curvature, 6),
            "sector": sector,
            "drs_zone": drs_active_zone,
        }


class TelemetryReplaySimulator:
    """
    Simulates synchronized multi-car telemetry frames from scratch without external dependencies.
    """
    COMPOUND_DEG = {
        "SOFT":   {"grip_bonus": 1.045, "deg_per_lap": 0.0032},
        "MEDIUM": {"grip_bonus": 1.000, "deg_per_lap": 0.0018},
        "HARD":   {"grip_bonus": 0.968, "deg_per_lap": 0.0010},
        "INTER":  {"grip_bonus": 0.890, "deg_per_lap": 0.0022},
    }

    def __init__(self, circuit: ParametricCircuitEngine, roster: List[CarEntry]):
        self.circuit = circuit
        self.roster = roster

    def compute_car_telemetry_at(self, car: CarEntry, race_time_s: float) -> Dict[str, object]:
        comp = self.COMPOUND_DEG.get(car.compound, self.COMPOUND_DEG["MEDIUM"])
        eff_grip = car.base_grip_mu * comp["grip_bonus"] - (car.tyre_age_laps * comp["deg_per_lap"])

        # Average lap speed modulated by grip and power factor
        mean_speed_mps = (58.8 * (eff_grip / 1.65) ** 0.35) * car.power_factor
        total_dist_m = race_time_s * mean_speed_mps
        current_lap = int(total_dist_m // self.circuit.length_m) + 1
        s_lap = total_dist_m % self.circuit.length_m

        pt = self.circuit.sample_point(s_lap)
        # Local cornering speed limit v_max_corner ~ sqrt(mu * g / curvature)
        curv_scaled = pt["curvature"] * 18.5
        corner_v_kmh = min(338.0, 95.0 + (245.0 / (1.0 + 380.0 * curv_scaled)) * eff_grip * car.power_factor)
        drs_boost = 11.5 if (pt["drs_zone"] and corner_v_kmh > 250.0) else 0.0
        speed_kmh = min(346.0, corner_v_kmh + drs_boost)

        # Derive longitudinal channels (Throttle %, Brake bar, Gear 1..8, RPM)
        throttle_pct = max(0.0, min(100.0, (speed_kmh - 105.0) / 2.15))
        brake_bar = max(0.0, min(115.0, (235.0 - speed_kmh) * 0.95)) if speed_kmh < 210.0 else 0.0
        gear = max(1, min(8, int(speed_kmh // 41) + 1))
        rpm = int(7800 + ((speed_kmh % 41) / 41.0) * 4300)
        lat_g = round(min(5.2, (speed_kmh / 3.6) ** 2 * curv_scaled / 9.81), 2)

        return {
            "car": car.car_number,
            "driver": car.driver_code,
            "compound": car.compound,
            "lap": current_lap,
            "total_dist_m": round(total_dist_m, 1),
            "s_m": pt["s_m"],
            "x_m": pt["x_m"],
            "y_m": pt["y_m"],
            "sector": pt["sector"],
            "speed_kmh": round(speed_kmh, 1),
            "rpm": rpm,
            "gear": gear,
            "throttle_pct": round(throttle_pct, 1),
            "brake_bar": round(brake_bar, 1),
            "drs": "OPEN" if drs_boost > 0 else "CLOSED",
            "lat_g": lat_g,
        }

    def snapshot_leaderboard(self, race_time_s: float) -> List[Dict[str, object]]:
        frames = [self.compute_car_telemetry_at(c, race_time_s) for c in self.roster]
        frames.sort(key=lambda f: f["total_dist_m"], reverse=True)
        leader_dist = frames[0]["total_dist_m"]
        for idx, f in enumerate(frames, 1):
            f["position"] = idx
            gap_m = leader_dist - f["total_dist_m"]
            f["gap_to_leader_s"] = round(gap_m / 60.5, 3)
        return frames


if __name__ == "__main__":
    circuit = ParametricCircuitEngine()
    roster = [
        CarEntry("#01", "VER", "Red Bull Racing", "SOFT", 1.72, 1.012, 6),
        CarEntry("#16", "LEC", "Scuderia Ferrari", "MEDIUM", 1.70, 1.008, 8),
        CarEntry("#44", "HAM", "Mercedes-AMG", "HARD", 1.69, 1.005, 11),
        CarEntry("#88", " Cup", "Porsche 992 GT3 Cup", "SOFT", 1.58, 0.945, 4),
    ]
    sim = TelemetryReplaySimulator(circuit, roster)
    board = sim.snapshot_leaderboard(race_time_s=1425.0)
    print("=" * 78)
    print(f"[F1 TELEMETRY RACE REPLAY ENGINE - BUILT FROM SCRATCH] Track: {circuit.track_name}")
    print("-" * 78)
    for row in board:
        print(
            f" P{row['position']} | {row['car']} {row['driver']:<4} ({row['compound']:<6}) | "
            f"Lap {row['lap']:02d} @ {row['s_m']:>6.1f}m | {row['speed_kmh']:>5.1f} km/h | "
            f"Gear {row['gear']} ({row['rpm']} RPM) | DRS: {row['drs']:<6} | Gap: +{row['gap_to_leader_s']:.3f}s"
        )
    print("=" * 78)
