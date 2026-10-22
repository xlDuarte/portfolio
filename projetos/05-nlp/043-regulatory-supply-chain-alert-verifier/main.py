#!/usr/bin/env python3
"""NLP #43 — Regulatory & Supply Chain Alert Verifier. Artificial samples; real text processing."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from nlp_batch.engine import cli
if __name__=="__main__":
    cli(43)
