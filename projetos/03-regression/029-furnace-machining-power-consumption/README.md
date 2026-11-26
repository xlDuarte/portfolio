> **Atualização científica (fase 5b):** balanço de energia de um forno elétrico de tratamento térmico (paredes com condução não linear, convecção natural de Churchill–Chu e radiação; porta com fator de forma e troca de ar de Linden; carga com calor específico da EN 1993-1-2) e energia de corte por Kienzle e Gutowski, com coeficientes da VDI 3323 e de medições da ETH Zürich. 199 kWh/t (faixa de 90 %: 193 a 208), 84 % da energia na carga; o tratamento térmico de um metro de barra gasta 6,8 vezes a energia de um passe de desbaste. Forno, carga e torno são hipotéticos. Método em [docs/physics/THERMAL.md](../../../docs/physics/THERMAL.md).

# #029 — Furnace & Machining Power Consumption

**Status:** implementation of a real regression training/evaluation workflow on a fully **SYNTHETIC** deterministic fixture; no industrial, financial, medical, educational or customer data were observed.

## Business question
Forecast daily electrical consumption from production plans, ambient temperature and planned loading, not realized energy.

## Reproducible implementation
- **Input:** [`regression_batch/data/029.csv`](../../../regression_batch/data/029.csv); `029` uniquely generated scenarios; row-level data dictionary in [`regression_batch/DATA_DICTIONARY.md`](../../../regression_batch/DATA_DICTIONARY.md).
- **Features known at prediction time:** planned_furnace_hours, planned_machine_hours, planned_tonnage, ambient_temp_c, furnace_load_pct, tariff_period_index, process.
- **Target:** `target_value` in kWh/day.
- **Actual libraries:** Pandas, NumPy, Scikit-learn (`DummyRegressor`, `Ridge`, preprocessing), XGBoost (`XGBRegressor`), Matplotlib.
- **Holdouts:** chronological, 60% train, 20% calibration, 20% untouched test. All fitted preprocessing is restricted to training rows. Conformal-style residual quantile uses calibration split only.
- **Metrics:** holdout MAE, RMSE, R², WAPE, interval width and empirical coverage; naive median and Ridge baseline MAE are included; no predetermined claims of superiority.
- **Outputs:** [`regression_batch/reports/029.json`](../../../regression_batch/reports/029.json), [`regression_batch/reports/029_predictions.csv`](../../../regression_batch/reports/029_predictions.csv), [`regression_batch/figures/029.svg`](../../../regression_batch/figures/029.svg), notebook and [site page](../../../site/cases/029/index.html).

## Run
```bash
python -m pip install -r requirements/regression.txt
python projetos/03-regression/029-furnace-machining-power-consumption/main.py
python -m regression_batch.engine 29 --save
```

## Limitations
Synthetic causal relationships were explicitly written by the generator and therefore **do not establish predictive performance on real-world data**. Future real sources require license/privacy clearance, missingness & drift checks, entity/time-safe splitting, recalibration and a human-reviewed model card. In project #024, predictions must not drive hiring or certification decisions; #026 is **not** a legally valid insurance quotation.
