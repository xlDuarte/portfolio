#!/usr/bin/env python3
"""Project #80: Metallurgical microstructure classifier; actual image analysis of synthetic frames."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from vision_batch.engine import cli
if __name__=="__main__":cli(80)
