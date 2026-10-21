#!/usr/bin/env python3
"""#103 Onboard Motorsport OpenCV Optical-Flow Feature Tracking.

Reproducible synthetic camera frames; no claim to real F1 footage or hardware
calibration. See motorsport/optical_flow.py for implementation.
"""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from motorsport.optical_flow import run

if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
