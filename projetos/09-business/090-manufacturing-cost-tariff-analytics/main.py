#!/usr/bin/env python3
"""Project #90: actual SQL, financial KPI computation and synthetic source data."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from business_batch.engine import cli
if __name__=="__main__":cli(90)
