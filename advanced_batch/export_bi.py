"""Export only the fictional BI events of project #100 as a typed CSV for Power BI."""
from __future__ import annotations
import argparse
import csv
from pathlib import Path
from .engine import connect,generate,ingest

def export_bi(path:str|Path="advanced_batch/reports/synthetic_bi.csv",count:int=96)->dict:
    if not isinstance(count,int) or not 24<=count<=2000:raise ValueError("count 24..2000")
    events=generate(100,count)
    output=Path(path)
    output.parent.mkdir(parents=True,exist_ok=True)
    fields=["line","planned_min","good_units","good_ideal_min","revenue_brl","event_id"]
    with open(output,"w",newline="",encoding="utf-8") as stream:
        writer=csv.DictWriter(stream,fieldnames=fields)
        writer.writeheader()
        for event in events:
            p=event["payload"]
            writer.writerow({"event_id":event["event_id"],"line":p["line"],
                             "planned_min":p["planned_min"],"good_units":p["good_units"],
                             "good_ideal_min":p["good_units"]*p["ideal_cycle_min"],
                             "revenue_brl":round(p["good_units"]*p["unit_price_brl"],2)})
    return {"csv_path":str(output),"rows":len(events),
            "source":"exclusively synthetic, exported for Power BI manual import"}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="advanced_batch/reports/synthetic_bi.csv")
    p.add_argument("--count",type=int,default=96)
    args=p.parse_args()
    print(export_bi(args.output,args.count))
