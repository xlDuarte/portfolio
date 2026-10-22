#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F1-PIP synthetic walk-forward ranking simulation; no external models trained, no SHAP
Author: Gabriel Reis Duarte (@gabrielrduarte)
"""
import math
import statistics
import random
from datetime import datetime
from typing import List, Dict, Any

class WalkForwardPredictionEngine:
    PLANNED_MODEL_CATALOG_NOT_IMPLEMENTED = [
        "Baseline_Grid",
        "Baseline_Standings",
        "Ridge_Regularized",
        "RandomForest_Ensemble",
        "GradientBoosting_Regressor",
        "XGBoost_Calibrated",
        "LightGBM_Ranker",
        "CatBoost_Probabilistic",
    ]

    @staticmethod
    def _platt_sigmoid(score: float, temp: float = 1.15) -> float:
        return 1.0 / (1.0 + math.exp(score / temp))

    @classmethod
    def predict_event_walk_forward(
        cls,
        train_events: List[Dict[str, Any]],
        target_event: Dict[str, Any],
        as_of_timestamp: str,
        horizon: str = "POST_QUALI"
    ) -> Dict[str, Any]:
        def parse_tz(s):
            try:
                dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
            except (AttributeError, TypeError, ValueError) as exc:
                raise ValueError("Timestamps must be ISO-8601 with timezone") from exc
            if dt.tzinfo is None or dt.utcoffset() is None:
                raise ValueError("Timezone required: timestamps must use Z or numeric offset")
            return dt

        as_of = parse_tz(as_of_timestamp)
        if horizon not in ("PRE_QUALI", "POST_QUALI"):
            raise ValueError("Unsupported prediction horizon")
        if not target_event.get("entries"):
            raise ValueError("At least one race entry required")
        codes = [entry["driver_code"] for entry in target_event["entries"]]
        if len(set(codes)) != len(codes):
            raise ValueError("Duplicate driver codes")
        for ev in train_events:
            if parse_tz(ev["event_timestamp_utc"]) >= as_of:
                raise ValueError(f"Look-ahead violation on {ev['event_id']}")
        if parse_tz(target_event["snapshot_timestamp_utc"]) > as_of:
            raise ValueError("Target snapshot newer than as_of_timestamp")

        driver_hist: Dict[str, List[float]] = {}
        team_hist: Dict[str, List[float]] = {}
        for ev in train_events:
            for row in ev["results"]:
                driver_hist.setdefault(row["driver_code"], []).append(float(row["finish_pos"]))
                team_hist.setdefault(row["constructor"], []).append(float(row["finish_pos"]))

        global_mean_pos = 10.5
        raw_latents = []
        for entry in target_event["entries"]:
            d = entry["driver_code"]
            c = entry["constructor"]
            d_obs = driver_hist.get(d, [])
            t_obs = team_hist.get(c, [])
            team_prior = statistics.mean(t_obs) if t_obs else global_mean_pos
            n_d = len(d_obs)
            w = n_d / (n_d + 4.0)
            driver_skill = w * (statistics.mean(d_obs) if d_obs else team_prior) + (1.0 - w) * team_prior

            grid_pos = float(entry.get("grid_pos", team_prior)) if horizon != "PRE_QUALI" else team_prior
            clean_air_delta_s = float(entry.get("clean_air_delta_s", 0.0))
            weather_mod = float(entry.get("weather_skill_delta_s", 0.0))

            c_grid = 0.42 * (grid_pos - global_mean_pos)
            c_pace = 4.10 * clean_air_delta_s
            c_team = 0.28 * (team_prior - global_mean_pos)
            c_drv = 0.22 * (driver_skill - team_prior)
            c_wea = 1.65 * weather_mod
            exp_pos = max(1.0, min(20.0, global_mean_pos + c_grid + c_pace + c_team + c_drv + c_wea))

            heuristic_values = {
                "base_value_pos": global_mean_pos,
                "grid_position_impact": round(c_grid, 3),
                "clean_air_pace_impact": round(c_pace, 3),
                "constructor_pace_impact": round(c_team, 3),
                "driver_skill_pooled_impact": round(c_drv, 3),
                "weather_track_interaction": round(c_wea, 3),
            }
            raw_latents.append((entry, exp_pos, heuristic_values))

        # Sequential Plackett-Luce simulated rankings: mutually exclusive results.
        # win probabilities sum to 1, podium to min(3, starters), points to min(10, starters).
        # These are CONDITIONAL ranking probabilities: DNF is reported separately,
        # not simulated as an absorbing outcome. Real F1 points also depend on classification.
        weights = [math.exp(-(pos - 1.0) / 3.2) for _, pos, _ in raw_latents]
        counts = [[0, 0, 0] for _ in raw_latents]
        sims = 20000
        rng = random.Random(20261021)
        for _ in range(sims):
            # Exponential race is mathematically equivalent to PL weighted sampling without replacement.
            ranking = sorted(range(len(weights)), key=lambda i: rng.expovariate(max(weights[i], 1e-15)))
            for rank, i in enumerate(ranking):
                if rank == 0: counts[i][0] += 1
                if rank < 3: counts[i][1] += 1
                if rank < 10: counts[i][2] += 1
        predictions = []
        for i, (entry, exp_pos, attrib) in enumerate(raw_latents):
            raw_dnf = float(entry.get("base_dnf_rate", 0.065))
            if not math.isfinite(raw_dnf) or not 0 <= raw_dnf <= 1:
                raise ValueError("base_dnf_rate must be within [0, 1]")
            predictions.append({
                "driver_code": entry["driver_code"],
                "driver_name": entry.get("driver_name", entry["driver_code"]),
                "constructor": entry["constructor"],
                "grid_pos": entry.get("grid_pos"),
                "expected_finish_pos": round(exp_pos, 2),
                "win_prob": counts[i][0] / sims,
                "podium_prob": counts[i][1] / sims,
                "points_prob": counts[i][2] / sims,
                "dnf_prob": round(raw_dnf, 4),
                "heuristic_attributions": attrib,
                "shap_explanation": attrib,  # Deprecated compatibility; NOT computed using SHAP.
            })

        predictions.sort(key=lambda x: x["expected_finish_pos"])
        for idx, p in enumerate(predictions, 1):
            p["predicted_rank"] = idx
        return {
            "event_id": target_event["event_id"],
            "horizon": horizon,
            "as_of_timestamp": as_of_timestamp,
            "predictions": predictions,
            "probability_basis": "Plackett-Luce Monte Carlo; conditional on classified finish; DNF independent",
            "not_trained_models": cls.PLANNED_MODEL_CATALOG_NOT_IMPLEMENTED,
        }


# Explicit trained-model API; legacy predict_event_walk_forward remains heuristic
# for existing callers and should not be mistaken for fitted predictions.
def _predict_event_trained(history, target_event, as_of_timestamp, models=None):
    from pathlib import Path
    import importlib.util
    research_file = Path(__file__).resolve().with_name('trained_pipeline.py')
    if not research_file.is_file():
        raise FileNotFoundError("F1 trained research pipeline not installed: " + str(research_file))
    spec = importlib.util.spec_from_file_location("f1_research_trained", research_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.fit_and_evaluate(history, target_event, as_of_timestamp, models=models)

WalkForwardPredictionEngine.predict_event_trained = staticmethod(_predict_event_trained)
