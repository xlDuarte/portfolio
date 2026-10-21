# Synthetic datasets — provenance and business definitions

Generator: `generate_data.py` using deterministic `random.Random(20261021)`. This creates **toy data**, not actual company records. No confidential or operational data are used.

| Dataset | Grain | Primary key | Metrics | Limitations |
|---|---|---|---|---|
| oee_shifts.csv | production shift | date + line | availability = run/planned; performance = ideal_cycle*total/run; quality = good/total; OEE = ideal_cycle*good/planned | simplified shifts; no real downtime taxonomy |
| supply_orders.csv | purchase order | order_id | OTIF requires on_time AND delivered_qty >= ordered_qty; exposure = undelivered qty * unit value | all carrier correlations are scripted assumptions |
| capex_projects.csv | hypothetical CAPEX project | project_id | target = observed_cost_brl, simulated by hidden coefficients + noise | random sample order does not provide real prospective validation |
| b2b_churn.csv | hypothetical account | account_id | target = churned_90d (binary), factors use simulated log-odds | labels are simulated; retention causality not proven |
| demand_daily.csv | material/day | date+material | target = demand_units; evaluation by strictly lagged 7-day mean | artificial seasonality; no exogenous features |

The `requirements-case-studies.txt` is separate from the optional package list for legacy 111 demos. CSV files use UTF-8, ISO-8601 dates, BRL for money (fictional). Define privacy controls and contract permissions when switching to real datasets.
