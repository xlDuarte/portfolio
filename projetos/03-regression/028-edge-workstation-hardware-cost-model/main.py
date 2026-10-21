#!/usr/bin/env python3
"""Project #028: Edge & Workstation Hardware Cost Model.

Actual scikit-learn Ridge, DummyRegressor baseline, XGBoost; Pandas/NumPy
and Matplotlib figures. Only synthetic fixtures, not industry measurements.
"""
from pathlib import Path
import json
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from regression_batch.engine import evaluate

if __name__ == '__main__':
    print(json.dumps(evaluate(28),indent=2,ensure_ascii=False))
