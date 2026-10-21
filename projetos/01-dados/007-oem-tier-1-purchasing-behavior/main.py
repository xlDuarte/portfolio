#!/usr/bin/env python3
"""Project #007 — OEM & Tier-1 Purchasing Behavior. Reproducible analytics on labeled synthetic data."""
from pathlib import Path
import argparse
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from analytics_batch1.engine import run, save_report


def main():
    parser=argparse.ArgumentParser(description='Auditable project #007: OEM & Tier-1 Purchasing Behavior')
    parser.add_argument('--source',help='CSV with documented validated schema')
    parser.add_argument('--report-dir',help='Optional output directory for SVG graph, validated CSV and JSON')
    args=parser.parse_args()
    if args.report_dir and args.source:
        parser.error('--source and --report-dir cannot be combined in this CLI; use engine.run for external data')
    result=save_report(7,args.report_dir) if args.report_dir else run(7,args.source)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
