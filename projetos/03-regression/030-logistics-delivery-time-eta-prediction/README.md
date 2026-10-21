# #030 — Logistics Delivery Time (ETA) Prediction

**Status:** implementation of a real regression training/evaluation workflow on a fully **SYNTHETIC** deterministic fixture; no industrial, financial, medical, educational or customer data were observed.

## Business question
Predicted time to delivery from shipment attributes available at dispatch; forward holdout.

## Reproducible implementation
- **Input:** [`regression_batch/data/030.csv`](../../../regression_batch/data/030.csv); `030` uniquely generated scenarios; row-level data dictionary in [`regression_batch/DATA_DICTIONARY.md`](../../../regression_batch/DATA_DICTIONARY.md).
- **Features known at prediction time:** route_distance_km, forecast_traffic_index, stops_planned, cargo_weight_tons, forecast_rain_mm, dispatch_hour, border_crossings, transport_mode.
- **Target:** `target_value` in hours.
- **Actual libraries:** Pandas, NumPy, Scikit-learn (`DummyRegressor`, `Ridge`, preprocessing), XGBoost (`XGBRegressor`), Matplotlib.
- **Holdouts:** chronological, 60% train, 20% calibration, 20% untouched test. All fitted preprocessing is restricted to training rows. Conformal-style residual quantile uses calibration split only.
- **Metrics:** holdout MAE, RMSE, R², WAPE, interval width and empirical coverage; naive median and Ridge baseline MAE are included; no predetermined claims of superiority.
- **Outputs:** [`regression_batch/reports/030.json`](../../../regression_batch/reports/030.json), [`regression_batch/reports/030_predictions.csv`](../../../regression_batch/reports/030_predictions.csv), [`regression_batch/figures/030.svg`](../../../regression_batch/figures/030.svg), notebook and [site page](../../../site/cases/030/index.html).

## Run
```bash
python -m pip install -r requirements-regression.txt
python projetos/03-regression/030-logistics-delivery-time-eta-prediction/main.py
python -m regression_batch.engine 30 --save
```

## Limitations
Synthetic causal relationships were explicitly written by the generator and therefore **do not establish predictive performance on real-world data**. Future real sources require license/privacy clearance, missingness & drift checks, entity/time-safe splitting, recalibration and a human-reviewed model card. In project #024, predictions must not drive hiring or certification decisions; #026 is **not** a legally valid insurance quotation.
