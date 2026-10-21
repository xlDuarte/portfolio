#!/usr/bin/env python3
"""#014 Motorsport Telemetry & Lap Benchmarks — real EDA computations on reproducible SYNTHETIC data."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from analytics_eda.engine import run, save_report

def main():
    parser=argparse.ArgumentParser(description="EDA #014: Motorsport Telemetry & Lap Benchmarks")
    parser.add_argument('--source',help='Optional CSV with the documented case schema')
    parser.add_argument('--report-dir',help='Output directory for SVG, Plotly HTML, CSV and metrics')
    args=parser.parse_args()
    if args.source and args.report_dir:
        parser.error('--report-dir uses versioned fixture; to evaluate your own CSV use --source')
    result=save_report(14,args.report_dir) if args.report_dir else run(14,args.source)
    print(json.dumps(result,ensure_ascii=False,indent=2,default=str))

if __name__=='__main__': main()
