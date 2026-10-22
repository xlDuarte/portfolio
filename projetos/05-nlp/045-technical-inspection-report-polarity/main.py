#!/usr/bin/env python3
"""NLP #45 — Technical Inspection Report Polarity. Artificial samples; actual trained text classifier."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from nlp_batch.engine import cli
if __name__=="__main__":cli(45)
