#!/usr/bin/env python3
"""#67: Machining Center & Dock Slot Forecast; deterministic fixture with actual ETS and Prophet fitting."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from timeseries_batch.engine import cli
if __name__=="__main__": cli(67)
