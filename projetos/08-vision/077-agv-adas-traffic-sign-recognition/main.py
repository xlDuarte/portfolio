#!/usr/bin/env python3
"""Project #77: AGV and ADAS sign recognition; OpenCV analysis of synthetic scenes."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from vision_batch.engine import cli
if __name__=="__main__":cli(77)
