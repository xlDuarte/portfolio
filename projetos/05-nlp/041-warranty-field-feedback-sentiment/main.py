#!/usr/bin/env python3
"""NLP #41 — Warranty & Field Feedback Sentiment. Artificial samples; real text processing."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from nlp_batch.engine import cli
if __name__=="__main__":
    cli(41)
