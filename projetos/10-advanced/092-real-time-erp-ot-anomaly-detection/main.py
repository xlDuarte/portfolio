#!/usr/bin/env python3
"""Advanced industrial project #92: actual synthetic ETL/ML workflow."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from advanced_batch.engine import cli
if __name__=="__main__":cli(92)
