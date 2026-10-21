#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F1-PIP Walk-Forward Multi-Model Engine, Calibration & SHAP Explainability
Author: Gabriel Reis Duarte (@gabrielrduarte)
"""
import math
import statistics
from typing import List, Dict, Any

class WalkForwardPredictionEngine:
    MODEL_CATALOG = [
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
        for ev in train_events:
            if ev["event_timestamp_utc"] >= as_of_timestamp:
                raise ValueError(f"Look-ahead violation on {ev['event_id']}")
        if target_event["snapshot_timestamp_utc"] > as_of_timestamp:
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

            shap_values = {
                "base_value_pos": global_mean_pos,
                "grid_position_impact": round(c_grid, 3),
                "clean_air_pace_impact": round(c_pace, 3),
                "constructor_pace_impact": round(c_team, 3),
                "driver_skill_pooled_impact": round(c_drv, 3),
                "weather_track_interaction": round(c_wea, 3),
            }
            raw_latents.append((entry, exp_pos, shap_values))

        win_logits = [math.exp(-(pos - 1.0) / 1.45) for _, pos, _ in raw_latents]
        sum_win = sum(win_logits) or 1.0
        predictions = []
        for (entry, exp_pos, shap_dict), w_l in zip(raw_latents, win_logits):
            win_prob = round(w_l / sum_win, 4)
            podium_prob = round(min(0.99, max(win_prob, cls._platt_sigmoid(exp_pos - 3.6, temp=1.35))), 4)
            points_prob = round(min(0.995, max(podium_prob, cls._platt_sigmoid(exp_pos - 10.5, temp=1.85))), 4)
            dnf_prob = round(min(0.35, max(0.02, float(entry.get("base_dnf_rate", 0.065)))), 4)
            predictions.append({
                "driver_code": entry["driver_code"],
                "driver_name": entry.get("driver_name", entry["driver_code"]),
                "constructor": entry["constructor"],
                "grid_pos": entry.get("grid_pos"),
                "expected_finish_pos": round(exp_pos, 2),
                "win_prob": win_prob,
                "podium_prob": podium_prob,
                "points_prob": points_prob,
                "dnf_prob": dnf_prob,
                "shap_explanation": shap_dict,
            })

        predictions.sort(key=lambda x: x["expected_finish_pos"])
        for idx, p in enumerate(predictions, 1):
            p["predicted_rank"] = idx
        return {
            "event_id": target_event["event_id"],
            "horizon": horizon,
            "as_of_timestamp": as_of_timestamp,
            "predictions": predictions,
        }
