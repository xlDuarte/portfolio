#!/usr/bin/env python3
"""Project #027: Industrial Forgings Sales Regression.

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
    print(json.dumps(evaluate(27),indent=2,ensure_ascii=False))
