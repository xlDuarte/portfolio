# #026 — Industrial Equipment Insurance Pricing

**Status:** implementation of a real regression training/evaluation workflow on a fully **SYNTHETIC** deterministic fixture; no industrial, financial, medical, educational or customer data were observed.

## Business question
Estimated synthetic insurance premium for machinery and fleets; cannot be used for real underwriting.

## Reproducible implementation
- **Input:** [`regression_batch/data/026.csv`](../../../regression_batch/data/026.csv); `026` uniquely generated scenarios; row-level data dictionary in [`regression_batch/DATA_DICTIONARY.md`](../../../regression_batch/DATA_DICTIONARY.md).
- **Features known at prediction time:** replacement_value_brl, equipment_age_years, annual_use_hours, maintenance_score, deductible_pct, security_score, equipment_type.
- **Target:** `target_value` in BRL/year.
- **Actual libraries:** Pandas, NumPy, Scikit-learn (`DummyRegressor`, `Ridge`, preprocessing), XGBoost (`XGBRegressor`), Matplotlib.
- **Holdouts:** seeded split of independent rows, 60% train, 20% calibration, 20% untouched test. All fitted preprocessing is restricted to training rows. Conformal-style residual quantile uses calibration split only.
- **Metrics:** holdout MAE, RMSE, R², WAPE, interval width and empirical coverage; naive median and Ridge baseline MAE are included; no predetermined claims of superiority.
- **Outputs:** [`regression_batch/reports/026.json`](../../../regression_batch/reports/026.json), [`regression_batch/reports/026_predictions.csv`](../../../regression_batch/reports/026_predictions.csv), [`regression_batch/figures/026.svg`](../../../regression_batch/figures/026.svg), notebook and [site page](../../../site/cases/026/index.html).

## Run
```bash
python -m pip install -r requirements-regression.txt
python projetos/03-regression/026-industrial-equipment-insurance-pricing/main.py
python -m regression_batch.engine 26 --save
```

## Limitations
Synthetic causal relationships were explicitly written by the generator and therefore **do not establish predictive performance on real-world data**. Future real sources require license/privacy clearance, missingness & drift checks, entity/time-safe splitting, recalibration and a human-reviewed model card. In project #024, predictions must not drive hiring or certification decisions; #026 is **not** a legally valid insurance quotation.
