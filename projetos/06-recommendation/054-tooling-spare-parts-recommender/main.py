#!/usr/bin/env python3
"""#54 — Tooling & Spare Parts Recommender; domain-specific offline recommendation engine."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from recommendation_batch.engine import cli
if __name__=="__main__": cli(54)
