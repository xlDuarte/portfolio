#!/usr/bin/env python3
"""Project #006 — B2B Industrial E-Procurement Analysis. Reproducible analytics on labeled synthetic data."""
from pathlib import Path
import argparse
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from analytics_batch1.engine import run, save_report


def main():
    parser=argparse.ArgumentParser(description='Auditable project #006: B2B Industrial E-Procurement Analysis')
    parser.add_argument('--source',help='CSV with documented validated schema')
    parser.add_argument('--report-dir',help='Optional output directory for SVG graph, validated CSV and JSON')
    args=parser.parse_args()
    if args.report_dir and args.source:
        parser.error('--source and --report-dir cannot be combined in this CLI; use engine.run for external data')
    result=save_report(6,args.report_dir) if args.report_dir else run(6,args.source)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
