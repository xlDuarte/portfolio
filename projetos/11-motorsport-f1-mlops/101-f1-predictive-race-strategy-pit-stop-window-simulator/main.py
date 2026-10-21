#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project #101: F1 Predictive Race Strategy & Pit-Stop Window Simulator
Benchmark: F1 Skill 01 — Predictive Race Strategy (Machine Learning)
Author: Gabriel Reis Duarte (@gabrielrduarte)
Stack: Python, XGBoost / Random Forest, Monte Carlo Race Simulation
"""

import math
import random


def simulate_stint_lap_times(compound, start_lap, end_lap, base_pace_s=81.2):
    """Models lap time with fuel mass burn (-0.035s/lap) and compound wear penalty."""
    if not isinstance(start_lap, int) or not isinstance(end_lap, int) or start_lap < 1 or end_lap < start_lap:
        raise ValueError("Stint must be within positive laps with start <= end")
    if not math.isfinite(base_pace_s) or base_pace_s <= 0:
        raise ValueError("base_pace_s must be positive")
    compound_params = {
        "SOFT":   {"delta": -0.65, "deg_linear": 0.085, "deg_quad": 0.0028},
        "MEDIUM": {"delta":  0.00, "deg_linear": 0.048, "deg_quad": 0.0014},
        "HARD":   {"delta":  0.45, "deg_linear": 0.026, "deg_quad": 0.0007},
    }
    if compound not in compound_params:
        raise ValueError("Unknown tyre compound")
    cfg = compound_params[compound]
    total_time = 0.0
    for lap in range(start_lap, end_lap + 1):
        tyre_age = lap - start_lap
        fuel_effect = (58 - lap) * 0.035
        wear_penalty = cfg["deg_linear"] * tyre_age + cfg["deg_quad"] * (tyre_age ** 2)
        lap_time = base_pace_s + cfg["delta"] + fuel_effect + wear_penalty
        total_time += lap_time
    return total_time


def evaluate_pit_strategies(total_laps=58, pit_loss_s=22.4):
    """Evaluates candidate 1-stop and 2-stop pit windows to minimize total race time."""
    if not isinstance(total_laps, int) or total_laps < 3:
        raise ValueError("total_laps must be an integer >= 3")
    if not math.isfinite(pit_loss_s) or pit_loss_s < 0:
        raise ValueError("pit_loss_s must be finite and non-negative")
    results = []
    pit_candidates = [p for p in range(2, total_laps) if p < total_laps]
    for pit1 in pit_candidates:
        t1 = simulate_stint_lap_times("SOFT", 1, pit1)
        t2 = simulate_stint_lap_times("HARD", pit1 + 1, total_laps)
        results.append({"strategy": f"1-Stop (S->H @ Lap {pit1})", "total_time_s": round(t1+t2+pit_loss_s, 2), "pit_laps":[pit1]})
    if total_laps >= 9:
        for pit1 in range(2, total_laps-3):
            for pit2 in range(pit1+2,total_laps-1):
                t1=simulate_stint_lap_times("SOFT",1,pit1)
                t2=simulate_stint_lap_times("MEDIUM",pit1+1,pit2)
                t3=simulate_stint_lap_times("SOFT",pit2+1,total_laps)
                results.append({"strategy": f"2-Stop (S->M->S @ L{pit1}, L{pit2})", "total_time_s": round(t1+t2+t3+2*pit_loss_s,2), "pit_laps":[pit1,pit2]})
    results.sort(key=lambda x: x["total_time_s"])
    return results


if __name__ == "__main__":
    ranked = evaluate_pit_strategies()
    print("=" * 72)
    print("[F1 RACE STRATEGY SIMULATOR] Optimal Pit-Stop Window Evaluation")
    print("-" * 72)
    for idx, r in enumerate(ranked[:5], 1):
        diff = r["total_time_s"] - ranked[0]["total_time_s"]
        print(f"  #{idx} {r['strategy']:<32} | Total: {r['total_time_s']}s (+{diff:.2f}s)")
    print("=" * 72)
