#!/usr/bin/env python3
"""#51 — dedicated Streamlit view over the shared industrial engine."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from recommendation_batch.app import run_app
if __name__=="__main__": run_app(51)
