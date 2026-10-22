# Industrial Business & Finance Analytics — #081–#090

**Real code:** all ten projects execute Pandas, SQLite SQL statements read from disk, and project-specific Python calculations. Scikit-learn fits actual ML estimators in #081 and #088. Matplotlib generates distinct diagnostic PNGs; a Streamlit app serves an interactive view. **All data are deterministic, synthetically generated, and not SAP/Ariba records.**

| ID | Executable function | Evidence/guardrail |
|---|---|---|
| 081 | Account contribution-margin 12-month LTV RandomForestRegressor | Account-disjoint train/test, median baseline, MAE/R² |
| 082 | Weighted OEE, availability, performance, quality and quota | Ratio of aggregated ideal good minutes to planned minutes |
| 083 | Simulated campaign ROI and randomized control arm | Margin lift, spend and counterfactual assumption |
| 084 | SQL aggregation + ABC and RFM | Cumulative sales Pareto, rank-based quintiles |
| 085 | SOX-like payment control alerts | SQL window tests: duplicate, weekend, split, approval |
| 086 | Operational risk heatmap | Full 5×5 count and threshold |
| 087 | CAPEX portfolio NPV | Discounted year 1–4 cash flows, exact binary knapsack over 12 fictional projects |
| 088 | Billing reconciliation and seasonal Ridge forecast | Revenue vs ledger, 30/6 temporal split, 3 future months |
| 089 | Procurement spend analytics | Supplier HHI, category Pareto, on-time delivery; not complete OTIF |
| 090 | Manufacturing transformation costs | Peak/off-peak tariffs, overtime, weighted cost/unit and variance |

## Execute

```bash
python -m pip install -r requirements-business.txt
python -m unittest discover -s tests -p test_business_batch.py -v
python -m business_batch.engine 82 --save
python -m business_batch.engine 87 --save
python -m business_batch.engine 90 --save
python -m streamlit run business_batch/app.py
```

Each numbered main.py in projetos/09-business/ executes its real domain case. SQLite reads queries from business_batch/sql/081.sql through 090.sql (not illustrative SQL).

## Synthetic data model and exports

The fixtures() function generates eleven relational source tables with stable customer, invoice, shift, payment, risk, CAPEX, campaign, ledger, procurement, manufacturing and billing grains. validate_tables() enforces unique IDs, referential integrity, non-null values and physical OEE constraints. Running any case with --save writes:

- exports/raw/*.csv: all eleven fictional source facts and one customer dimension.
- exports/NNN_query.csv: exact SQLite query result.
- reports/NNN.json: numeric outputs, caveats and applied methodology.
- figures/NNN.png: domain-specific Matplotlib figure.

## Power BI artifacts: exact supported scope

powerbi/ contains a Power Query M import function, eleven table-specific .pq queries, and DAX measure expressions. These are **editable templates for manual Power BI Desktop import**, not a .pbix file, not a Power BI project deployed to the Service, and not executed by a DAX engine in CI. Table typing and relationships require Power BI Desktop review. The Python/SQLite/Streamlit pipeline runs independently. SAP/Ariba credentials, API ingestion, data refresh and RLS are absent.

## Quality and governance

Every source and record is entirely fabricated. No client/employee/vender personal or confidential data have been accessed. #081 model fits and predicts fictional targets, so no real corporate LTV performance is implied. #083 results do not establish any real causal lift. #085 flags are controls for human review, not fraud convictions or proven SOX violations. #086 is not an actual safety incident report. #087 discount rate and cash flows are illustrative. #088 tax assumptions are not tax advice and future actual revenues are unknown. #089 on-time rate is not fill rate. #090 tariffs, overtime rates and unit economics are fabricated and not a basis for price or payroll decisions.

Missing production-grade scope includes approved SAP extraction, authoritative master data, real booked facts, true A/B testing, fiscal sign-off, model and DAX validation, an actual maintained .pbix/.pbip file, refresh monitoring, credentials/RLS, audit trails and independent field performance measurement. These synthetic tests do not certify a portfolio score of 100/100.
