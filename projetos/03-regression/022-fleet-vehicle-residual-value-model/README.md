# #022 — Fleet & Vehicle Residual Value Model

**Status:** implementation of a real regression training/evaluation workflow on a fully **SYNTHETIC** deterministic fixture; no industrial, financial, medical, educational or customer data were observed.

## Business question
Estimated vehicle residual value using age, odometer, maintenance and powertrain; simulated market in Brazil.

## Reproducible implementation
- **Input:** [`regression_batch/data/022.csv`](../../../regression_batch/data/022.csv); `022` uniquely generated scenarios; row-level data dictionary in [`regression_batch/DATA_DICTIONARY.md`](../../../regression_batch/DATA_DICTIONARY.md).
- **Features known at prediction time:** age_years, odometer_km, service_score, incident_count, battery_health_pct, original_price_brl, powertrain.
- **Target:** `target_value` in BRL.
- **Actual libraries:** Pandas, NumPy, Scikit-learn (`DummyRegressor`, `Ridge`, preprocessing), XGBoost (`XGBRegressor`), Matplotlib.
- **Holdouts:** seeded split of independent rows, 60% train, 20% calibration, 20% untouched test. All fitted preprocessing is restricted to training rows. Conformal-style residual quantile uses calibration split only.
- **Metrics:** holdout MAE, RMSE, R², WAPE, interval width and empirical coverage; naive median and Ridge baseline MAE are included; no predetermined claims of superiority.
- **Outputs:** [`regression_batch/reports/022.json`](../../../regression_batch/reports/022.json), [`regression_batch/reports/022_predictions.csv`](../../../regression_batch/reports/022_predictions.csv), [`regression_batch/figures/022.svg`](../../../regression_batch/figures/022.svg), notebook and [site page](../../../site/cases/022/index.html).

## Run
```bash
python -m pip install -r requirements/regression.txt
python projetos/03-regression/022-fleet-vehicle-residual-value-model/main.py
python -m regression_batch.engine 22 --save
```

## Limitations
Synthetic causal relationships were explicitly written by the generator and therefore **do not establish predictive performance on real-world data**. Future real sources require license/privacy clearance, missingness & drift checks, entity/time-safe splitting, recalibration and a human-reviewed model card. In project #024, predictions must not drive hiring or certification decisions; #026 is **not** a legally valid insurance quotation.
