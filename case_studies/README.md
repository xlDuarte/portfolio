# Five executable industrial analytics case studies

All datasets in `data/` are deterministic and **entirely synthetic**, generated with random seed 20261021. No customer operations, financial benefit or model validation on industry data is claimed.

## Run locally

```bash
python -m pip install -r requirements/case-studies.txt
python case_studies/generate_data.py
python case_studies/analytics.py
python -m unittest discover -s tests -v
```

The five studies are: weighted industrial OEE, SQL-based OTIF, Ridge CAPEX regression with holdout baseline, B2B churn logistic classifier with ROC-AUC/PR-AUC/Brier, and strictly one-step-ahead rolling-origin seasonal naive demand forecast. Each case has input schemas in `DATA_DICTIONARY.md`, direct executable code, sample data and machine-readable results in `reports/metrics.json`. Do not interpret synthetic predictive scores as external generalization.

### XGBoost (implementado e testado)

O projeto `#021` também treina um estimador `XGBRegressor` de verdade. Execute `python -m case_studies.xgboost_capex`. Os resultados de holdout referem-se exclusivamente à amostra sintética gerada.
