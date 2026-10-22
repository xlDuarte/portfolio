#!/usr/bin/env python3
"""Business #85: SOX Payment Audit & Anomaly Detection. Executable SQLite/Python analysis, entirely synthetic."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from business_batch.engine import cli
if __name__=="__main__":cli(85)
