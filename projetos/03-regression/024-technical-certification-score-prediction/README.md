# #024 — Technical Certification Score Prediction

**Status:** implementation of a real regression training/evaluation workflow on a fully **SYNTHETIC** deterministic fixture; no industrial, financial, medical, educational or customer data were observed.

## Business question
Estimated technical certification outcome for simulated trainees; should never be used for real hiring decisions.

## Reproducible implementation
- **Input:** [`regression_batch/data/024.csv`](../../../regression_batch/data/024.csv); `024` uniquely generated scenarios; row-level data dictionary in [`regression_batch/DATA_DICTIONARY.md`](../../../regression_batch/DATA_DICTIONARY.md).
- **Features known at prediction time:** training_hours, practice_score, prior_score, study_weeks, attendance_pct, difficulty_index, certification_track.
- **Target:** `target_value` in score points.
- **Actual libraries:** Pandas, NumPy, Scikit-learn (`DummyRegressor`, `Ridge`, preprocessing), XGBoost (`XGBRegressor`), Matplotlib.
- **Holdouts:** seeded split of independent rows, 60% train, 20% calibration, 20% untouched test. All fitted preprocessing is restricted to training rows. Conformal-style residual quantile uses calibration split only.
- **Metrics:** holdout MAE, RMSE, R², WAPE, interval width and empirical coverage; naive median and Ridge baseline MAE are included; no predetermined claims of superiority.
- **Outputs:** [`regression_batch/reports/024.json`](../../../regression_batch/reports/024.json), [`regression_batch/reports/024_predictions.csv`](../../../regression_batch/reports/024_predictions.csv), [`regression_batch/figures/024.svg`](../../../regression_batch/figures/024.svg), notebook and [site page](../../../site/cases/024/index.html).

## Run
```bash
python -m pip install -r requirements/regression.txt
python projetos/03-regression/024-technical-certification-score-prediction/main.py
python -m regression_batch.engine 24 --save
```

## Limitations
Synthetic causal relationships were explicitly written by the generator and therefore **do not establish predictive performance on real-world data**. Future real sources require license/privacy clearance, missingness & drift checks, entity/time-safe splitting, recalibration and a human-reviewed model card. In project #024, predictions must not drive hiring or certification decisions; #026 is **not** a legally valid insurance quotation.
