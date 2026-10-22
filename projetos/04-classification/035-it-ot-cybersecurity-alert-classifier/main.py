#!/usr/bin/env python3
"""#35: IT OT Cybersecurity Alert Triage; actual classification training, only synthetic data."""
from pathlib import Path
import sys
import json
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from classification_batch.engine import evaluate

if __name__ == "__main__":
    print(json.dumps(evaluate(35),ensure_ascii=False,indent=2))
