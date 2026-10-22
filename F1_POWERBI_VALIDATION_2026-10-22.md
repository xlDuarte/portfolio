# Corrective implementation — 22 Oct 2026

**Scope:** research-quality F1 model training, standalone synthetic results page, PBIP/DAX source project, checks and Vercel synchronization.

## Confirmed checks

- Vercel production deployed from `a1773c3e1ca15f8f604cae785814265168d538a5` (separate from pending PR updates).
- Existing open PRs #18–#28 are Dependabot updates; no unreviewed dependency major-version bumps were merged automatically.
- Research F1 engine trains two baselines + six third-party estimators with chronological holdout event grouping.
- Synthetic fixture yielded structurally consistent Plackett–Luce predictions (one win, three podium slots and ten point slots per 12-driver race).
- PBIP includes five Import tables, six dimension-to-fact relationships, sixteen DAX measures, one report page and four card visual definitions. KPI reference calculations produced by Python fixture.
- The local ten regression tests passed (F1 training, cutoffs, duplicate entrants, project schema and KPI reference).

## Important gaps (not solved)

- **Power BI Desktop validation**: cannot certify model import, data refresh, actual DAX evaluation, card rendering, cross-filter behavior or a PBIX without a Microsoft Tabular runtime and verified connection. The deliverable is PBIP source, not an approved dashboard.
- **F1 actual accuracy**: no licensed race dataset, no leave-one-season-out test, no validated probability calibration on real FIA/FastF1 observations, no SHAP evaluation, no DNF/safety-car simulator and no operational live API. Existing heuristic path is preserved; the trained path is an explicit separate method.
- **End-to-end testing**: production Vercel READY does not verify every interactive route. A Playwright browser acceptance pass on deployed domain remains necessary.
- **Security/CI**: Pull Request validation on GitHub must finish, including all repo-wide checks; dependency upgrade PRs must be individually reviewed.

## Verification commands

```bash
python -m unittest discover -s tests -p test_f1_trained_pipeline.py -v
python -m unittest discover -s tests -p test_powerbi_semantic_model.py -v
python f1-predictive-intelligence/ml/training/trained_pipeline.py --synthetic-demo --output synthetic_eval.json
```
