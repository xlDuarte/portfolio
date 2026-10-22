#!/usr/bin/env python3
"""#63: Plant Thermal Load Weather Forecast; real forecasting of wholly synthetic industrial series."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from timeseries_batch.engine import cli
if __name__=="__main__": cli(63)
