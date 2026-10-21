#!/usr/bin/env python3
"""Project #021 — Industrial Facility Capex Valuation.

Actual analytics case study (all source data are synthetic, NOT industry observations).
Requires requirements-case-studies.txt; source: case_studies/analytics.py.
"""
from pathlib import Path
import sys
import json
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from case_studies.analytics import run
from case_studies.xgboost_capex import evaluate_xgboost_capex

if __name__ == "__main__":
    print(json.dumps({'ridge':run('capex'), 'xgboost':evaluate_xgboost_capex()}, ensure_ascii=False, indent=2))
