#!/usr/bin/env python3
"""Project #031 — B2B Industrial Contract Churn Prediction.

Actual analytics case study (all source data are synthetic, NOT industry observations).
Requires requirements-case-studies.txt; source: case_studies/analytics.py.
"""
from pathlib import Path
import sys
import json
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from case_studies.analytics import run

if __name__ == "__main__":
    print(json.dumps(run('churn'), ensure_ascii=False, indent=2))
