#!/usr/bin/env python3
"""#64: Rolling Mill Electricity Demand Forecast; real time-series models evaluated on synthetic observations."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from timeseries_batch.engine import cli
if __name__=="__main__": cli(64)
