# F1-PIP: actually trained walk-forward ranking models (research track)

This research implementation **trains the eight named algorithms**, four of which use external estimators (Ridge, RandomForest, GradientBoosting, XGBoost, LightGBM and CatBoost models plus two baselines). It does **not** transform synthetic tests into real-world F1 validation.

```bash
pip install -r requirements-f1-research.txt
python f1-predictive-intelligence/ml/training/trained_pipeline.py --synthetic-demo --output f1_synthetic_evaluation.json
```

For authorized event data, prepare `events.json` as an array of event objects and `target.json` as an event with **only pre-race features**. Run:

```bash
python f1-predictive-intelligence/ml/training/trained_pipeline.py \
  --events-json events.json --target-json target.json \
  --as-of 2026-10-22T17:00:00+00:00 --output prediction.json
```

**Event schema:** `event_id`, `event_timestamp_utc`, `snapshot_timestamp_utc`, `entries` (driver_code, constructor, grid_pos, optional clean_air_delta_s/weather_skill_delta_s), `results` (driver_code, constructor, finish_pos). Use ISO-8601 timezone-aware timestamps. `target.json` must omit results.

**Data leakage guard:** every training row uses ONLY previously completed race results. Entire later races are set aside for scoring and temperature tuning. There is no per-driver random split, and as-of cutoffs reject future events/snapshots.

**Model semantics:** baseline grid, baseline historical standings, Ridge, RandomForest, GradientBoosting, XGBoost regression with later-event temperature tuning, LightGBM lambdarank, and CatBoost regression with later-event temperature tuning. The `*_Calibrated`/`*_Probabilistic` names **do not imply externally validated probabilities**. Probabilities arise from a Plackett–Luce finishing-order Monte Carlo; DNF is outside this research track. Validation metrics are themselves used for model selection and temperature tuning, so an entirely untouched test season is mandatory before claiming measured generalization. No SHAP is claimed by this new engine.

**Requirements not yet met:** real licensed FIA/FastF1 data ingestion and provenance, team-dependent race pace features validated pre-race, retirement/SC/red-flag dynamics, empirically calibrated win/podium/points probabilities, SHAP feature contributions, multi-season untouched external benchmarks, full API/UI integration, live monitoring.
