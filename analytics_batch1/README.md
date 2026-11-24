# Batch 1 — Project studies #001–#009

These are nine **distinct, executable** analyses, not renamed copies of a telemetry template. Each reads a versioned synthetic CSV, validates its schema and constraints, calculates domain-specific KPIs with real Pandas/NumPy operations, and can render a Matplotlib chart via `save_report`.

## Reproduce

```bash
python -m pip install -r requirements/case-studies.txt
python -m analytics_batch1.generate
python -m analytics_batch1.engine 4 --report-dir /tmp/nvh-report
python -m unittest tests.test_analytics_batch1 -v
```

Run any `projetos/01-dados/00N-*/main.py` from root with `--source` (CSV) or `--report-dir`. Jupyter notebooks under `notebooks/` import the same module; run from repo root. `site/cases/00N/` holds static, pre-rendered demonstration snapshots. The CSVs are fictitious fixtures, not SAP extracts or real plants. Inference of intervention effectiveness or business ROI is **not** warranted.

## Project-specific methodologies

| ID | Data grain | Method | Primary output | Limitation |
|---|---|---|---|---|
| 001 | operator | paired gains + reproducible bootstrap CI | mean learning gains | observational not causal |
| 002 | sale line | net sales, margin, SKU ABC | revenue / margin / ABC | fictitious inventory |
| 003 | document revision | metadata quality, duplicate keys, review age | completeness/staleness | no external index |
| 004 | accelerometer sample | Hann-window RFFT + harmonic orders | frequency / amplitude | no calibrated sensor |
| 005 | portal session | deflection proxy and topic grouping | self-service rate | not impact estimate |
| 006 | completed purchase request | lead-time pipeline | days / spend / quoted savings | only completed cohort |
| 007 | purchase order | spend shares / HHI concentration | supplier concentration | not market HHI |
| 008 | shift reading | weighted energy intensity | kWh/unit and cost | mix not normalized |
| 009 | registered asset | straight-line accounting book value + discounted future cashflows | book value and illustrative PV | not appraised price |

## Remaining stack gaps

- **Power BI:** has not been run or validated. The datasets are ready to import. Authoring an actual report in Power BI Desktop and auditing a `.pbip` is necessary before marking it fulfilled.
- **SAP:** no production source or connector; input CSV is illustrative. `--source` supports user-approved external CSV, subject to schema validation.
- These analyses demonstrate methods and reproducibility **on synthetic fixtures only**. A separate external test dataset is needed for production claims.
