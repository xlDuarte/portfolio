#!/usr/bin/env python3
"""#98: Engineering Document & Invoice Classifier; actual domain-specific synthetic pipeline."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from advanced_batch.engine import cli
if __name__=="__main__":cli(98)
