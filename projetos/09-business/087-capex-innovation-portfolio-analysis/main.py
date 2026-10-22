#!/usr/bin/env python3
"""Project #87: real SQL and Python financial analysis on synthetic data."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from business_batch.engine import cli
if __name__=="__main__":cli(87)
