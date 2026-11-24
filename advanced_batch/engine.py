"""Industrial API/ETL/ML workflows #091-#100 on synthetic events.

No live SAP/OT, real hiring decisions, production control commands, certified
safety alerts, Kafka availability or deployed Power BI workspace is claimed.
"""
from __future__ import annotations
from contextlib import closing
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta, timezone
from math import ceil

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, mean_absolute_error, roc_auc_score, f1_score
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

ROOT=Path(__file__).resolve().parent
SPECS={int(k):v for k,v in json.loads((ROOT/"specs.json").read_text(encoding="utf-8")).items()}
SEED=20261022

def generate(project:int, count:int=96, seed:int=SEED)->list[dict]:
    """Deterministic event envelope and domain-specific payload."""
    if project not in SPECS:raise ValueError("Unknown project")
    if not isinstance(count,int) or isinstance(count,bool) or not 24<=count<=2000:
        raise ValueError("count must be 24..2000")
    rng=np.random.default_rng(seed+project)
    start=datetime(2025,1,1,tzinfo=timezone.utc)
    skills=["python","sql","maintenance","plc","power bi","mechanical","quality","safety"]
    prefixes={
        "invoice":["Nota fiscal registrada no ERP", "Boleto de pagamento recebido","Fatura de fornecedor processada"],
        "drawing":["Desenho mecânico de montagem", "Especificação de tolerância geométrica", "Projeto técnico de engrenagem"],
        "contract":["Contrato de fornecimento e cláusula de SLA","Acordo comercial com prazo de vigência", "Contrato B2B de serviços"],
    }
    events=[]
    for i in range(count):
        if project==91:
            payload={"vendor_id":f"V{i%16:03d}","otif":round(float(rng.uniform(.60,1)),4),
                     "quality_rate":round(float(rng.uniform(.78,1)),4),
                     "approved":bool(i%13!=0),"documents_valid":bool(i%9!=0)}
        elif project==92:
            payload={"asset":f"OT-{i%8:02d}","amount_brl":round(float(rng.lognormal(8, .35)*(8 if i%31==0 else 1)),2),
                     "temperature_c":round(float(rng.normal(71,6)+(46 if i%29==0 else 0)),2),
                     "commands":int(rng.poisson(11)+(80 if i%37==0 else 0))}
        elif project==93:
            required=skills[i%len(skills):i%len(skills)+3]
            candidate=list(sorted(set(rng.choice(skills,4,replace=False))))
            payload={"profile_id":f"FAKE-P{i:03d}","project_skills":required,
                     "profile_skills":candidate,"available_hours":int(rng.integers(8,60)),"cleared":bool(i%11!=0)}
        elif project==94:
            target=max(0,int(60+8*np.sin(i*2*np.pi/12)+.24*i+rng.normal(0,3)))
            payload={"sku":"ICS-42","weekly_demand":target,"stock_qty":int(480-(i%28)*6),
                     "supplier_lead_weeks":3,"safety_stock":85}
        elif project==95:
            tenure=int(rng.integers(2,64));late=int(rng.integers(0,8))
            issue=int(rng.integers(0,6));util=float(rng.uniform(.1,.95))
            score=-2.6+.38*late+.28*issue-.025*tenure-.7*util
            prob=1/(1+np.exp(-score))
            payload={"contract_id":f"C{i:05d}","tenure_months":tenure,"late_deliveries":late,
                     "service_issues":issue,"utilization":round(util,5),
                     "churn_label":int(rng.uniform()<prob)}
        elif project==96:
            hardness=int(rng.integers(160,420));thickness=float(rng.uniform(2,18))
            payload={"work_order":f"WO{i:04d}","material_hardness_hb":hardness,
                     "part_thickness_mm":round(thickness,2),"max_rpm":2000,"max_feed_mm_min":540,
                     "min_rpm":400}
        elif project==97:
            vib=float(rng.uniform(.3,9));temp=float(rng.uniform(40,110));cycles=int(rng.integers(300,15000))
            rul=max(1,round(280-14*vib-1.15*(temp-40)-.006*cycles+float(rng.normal(0,7)),2))
            payload={"asset_id":f"ASSET-{i:04d}","vibration_mm_s":round(vib,4),
                     "temperature_c":round(temp,3),"cycles":cycles,"rul_hours_label":rul}
        elif project==98:
            category=list(prefixes)[i%3]
            template=prefixes[category][(i//3)%3]
            payload={"document_id":f"DOC{i:05d}","text":f"{template}. Item {i:04d} unidade {i%7}.",
                     "document_type_label":category}
        elif project==99:
            payload={"line":f"LINE-{i%3}","defect_pct":round(float(rng.uniform(.1,7)),2),
                     "sensor_temp_c":round(float(rng.normal(78,11)),3),
                     "guard_open":bool(i%19==0),"emergency_stop":bool(i%43==0)}
        else:
            planned=int(rng.integers(420,490));runtime=int(planned-rng.integers(5,90))
            produced=int(runtime*float(rng.uniform(.72,.91)));good=int(produced-rng.integers(1,10))
            payload={"line":f"LINE-{i%3}","planned_min":planned,"run_min":runtime,
                     "total_units":produced,"good_units":good,"ideal_cycle_min":1.,
                     "unit_price_brl":round(float(rng.uniform(150,400)),2)}
        events.append({
            "event_id":f"P{project:03d}-E{i:06d}",
            "project_id":project,"sequence":i+1,"occurred_at":(start+timedelta(minutes=i)).isoformat(),
            "payload":payload,"origin":"SYNTHETIC","schema_version":1})
    return events

def validate_event(event:dict)->dict:
    if not isinstance(event,dict):raise ValueError("Event must be JSON object")
    required={"event_id","project_id","sequence","occurred_at","payload","origin","schema_version"}
    if set(event)!=required:raise ValueError("Invalid event envelope fields")
    project=event["project_id"]
    if not isinstance(project,int) or isinstance(project,bool) or project not in SPECS:
        raise ValueError("Unknown project")
    if not isinstance(event["event_id"],str) or not event["event_id"].startswith(f"P{project:03d}-"):
        raise ValueError("Event ID must match project")
    if not isinstance(event["sequence"],int) or event["sequence"]<1:
        raise ValueError("Invalid sequence")
    if event["origin"]!="SYNTHETIC" or event["schema_version"]!=1:
        raise ValueError("Only demo schema and synthetic provenance accepted")
    if not isinstance(event["payload"],dict) or not event["payload"]:
        raise ValueError("Missing domain payload")
    stamp=datetime.fromisoformat(event["occurred_at"])
    if stamp.tzinfo is None:raise ValueError("Timestamp requires timezone")
    return event

def connect(db_path:Path|str=":memory:")->sqlite3.Connection:
    conn=sqlite3.connect(str(db_path),timeout=15,check_same_thread=False)
    conn.row_factory=sqlite3.Row
    conn.execute("PRAGMA busy_timeout=10000")
    conn.execute("""CREATE TABLE IF NOT EXISTS events(
      event_id TEXT PRIMARY KEY,
      project_id INTEGER NOT NULL,
      sequence INTEGER NOT NULL,
      occurred_at TEXT NOT NULL,
      payload_json TEXT NOT NULL,
      origin TEXT NOT NULL,
      UNIQUE(project_id,sequence))""")
    conn.execute("CREATE INDEX IF NOT EXISTS events_project_seq ON events(project_id,sequence)")
    conn.commit()
    return conn

def ingest(conn:sqlite3.Connection,events:list[dict])->dict:
    if not isinstance(events,list) or not events:raise ValueError("Nonempty event list required")
    before=conn.total_changes
    # All event validations happen BEFORE any write, keeping the batch atomic.
    for item in events:validate_event(item)
    with conn:
        for event in events:
            row=conn.execute("SELECT payload_json,project_id,sequence,occurred_at FROM events WHERE event_id=?",
                             (event["event_id"],)).fetchone()
            if row:
                if (json.loads(row["payload_json"])!=event["payload"] or
                    row["project_id"]!=event["project_id"] or
                    row["sequence"]!=event["sequence"] or
                    row["occurred_at"]!=event["occurred_at"]):
                    raise ValueError("Conflicting duplicate event identity")
                continue
            conn.execute("INSERT INTO events VALUES(?,?,?,?,?,?)",
                (event["event_id"],event["project_id"],event["sequence"],event["occurred_at"],
                 json.dumps(event["payload"],sort_keys=True),event["origin"]))
    return {"received":len(events),"inserted":conn.total_changes-before,
            "deduplicated":len(events)-(conn.total_changes-before)}

def read_events(conn:sqlite3.Connection,project:int,limit:int=2000)->list[dict]:
    if project not in SPECS:raise ValueError("Unknown project")
    if not isinstance(limit,int) or limit<1 or limit>2000:raise ValueError("Invalid limit")
    rows=conn.execute("SELECT * FROM events WHERE project_id=? ORDER BY sequence LIMIT ?",
                      (project,limit)).fetchall()
    return [{"event_id":r["event_id"],"project_id":r["project_id"],
             "sequence":r["sequence"],"occurred_at":r["occurred_at"],
             "payload":json.loads(r["payload_json"]),"origin":r["origin"],
             "schema_version":1} for r in rows]

def _rounded(v):return round(float(v),5)

def analyze(project:int,events:list[dict]|None=None)->dict:
    if project not in SPECS:raise ValueError("Unknown project")
    records=generate(project) if events is None else events
    if not records:raise ValueError("No records")
    for e in records:
        validate_event(e)
        if e["project_id"]!=project:raise ValueError("Mixed project batch")
    data=pd.DataFrame([e["payload"] for e in records])
    if project==91:
        data["risk"]=100*(.35*(1-data.otif)+.35*(1-data.quality_rate)+
                          .15*(~data.approved)+.15*(~data.documents_valid))
        allowed=data[data.approved & data.documents_valid].copy()
        result={"eligible_vendors":int(allowed.vendor_id.nunique()),
                "review_cases":int((data.risk>=30).sum()),
                "mean_risk_score":_rounded(data.risk.mean()),
                "top_review_events":[str(s) for s in data.loc[data.risk>=30,"vendor_id"].head(10)],
                "score_formula":"100*(.35*(1-OTIF)+.35*(1-quality)+.15*not_approved+.15*invalid_documents)",
                "decisions_executed":False}
    elif project==92:
        cols=["amount_brl","temperature_c","commands"]
        # Chronological reference fit excludes latest 25% of stream observations.
        cut=int(len(data)*.75)
        train=data.iloc[:cut][cols]
        test=data.iloc[cut:][cols]
        model=IsolationForest(n_estimators=80,contamination=.09,random_state=SEED,n_jobs=1).fit(train)
        flags=model.predict(test)==-1
        result={"model":"sklearn IsolationForest fitted on historical synthetic signals",
                "historical_train_rows":len(train),"unseen_stream_rows":len(test),
                "unseen_anomalies":int(flags.sum()),"outlier_fraction":_rounded(np.mean(flags)),
                "last_event_ids":[e["event_id"] for e in records[cut:][-5:]],
                "fraud_detected":False}
    elif project==93:
        matches=[]
        for row in data.itertuples():
            required=set(row.project_skills);offered=set(row.profile_skills)
            coverage=len(required&offered)/max(len(required),1)
            if row.cleared and row.available_hours>=16:
                matches.append({"profile_id":row.profile_id,"skills_coverage":_rounded(coverage),
                                "matched_skills":sorted(required&offered)})
        matches.sort(key=lambda r:(-r["skills_coverage"],r["profile_id"]))
        result={"eligible_synthetic_profiles":len(matches),"sample_recommendations":matches[:8],
                "staffing_or_hiring_decision_executed":False,
                "policy":"A descriptive fictional skills match, never a candidate rejection or ranking in real HR"}
    elif project==94:
        vals=data.weekly_demand.to_numpy(dtype=float)
        cut=len(vals)-12
        def x(idx):
            idx=np.asarray(idx,dtype=float)
            return np.column_stack([idx,np.sin(2*np.pi*idx/12),np.cos(2*np.pi*idx/12)])
        estimator=Ridge(alpha=1.0).fit(x(np.arange(cut)),vals[:cut])
        predicted=np.maximum(0,estimator.predict(x(np.arange(cut,len(vals)))))
        forecast=np.maximum(0,Ridge(alpha=1.).fit(x(np.arange(len(vals))),vals).predict(
                            x(np.arange(len(vals),len(vals)+6))))
        lead=int(data.supplier_lead_weeks.iloc[-1])
        safety=int(data.safety_stock.iloc[-1])
        reorder=ceil(float(np.mean(forecast))*lead)+safety
        result={"model":"Ridge fit with trend and seasonal sin/cos",
                "historical_train_weeks":cut,"untouched_test_weeks":12,
                "test_mae_units":_rounded(mean_absolute_error(vals[cut:],predicted)),
                "future_six_week_forecast_units":[int(round(v)) for v in forecast],
                "reorder_point_units":reorder,"latest_stock_units":int(data.stock_qty.iloc[-1]),
                "reorder_recommended":bool(data.stock_qty.iloc[-1]<reorder),
                "purchase_order_created":False}
    elif project==95:
        features=["tenure_months","late_deliveries","service_issues","utilization"]
        y=data.churn_label.to_numpy()
        idx_train,idx_test=train_test_split(np.arange(len(data)),test_size=.25,
                           random_state=SEED,stratify=y)
        model=LogisticRegression(max_iter=1000).fit(data.iloc[idx_train][features],y[idx_train])
        probs=model.predict_proba(data.iloc[idx_test][features])[:,1]
        result={"model":"sklearn LogisticRegression trained on artificial contract labels",
                "train_contracts":len(idx_train),"untouched_test_contracts":len(idx_test),
                "test_roc_auc":_rounded(roc_auc_score(y[idx_test],probs)),
                "test_f1":_rounded(f1_score(y[idx_test],probs>=.5,zero_division=0)),
                "last_test_probabilities":[_rounded(v) for v in probs[:8]],
                "commercial_decisions_executed":False}
    elif project==96:
        proposals=[]
        for row in data.itertuples():
            # Constrained non-actuating static engineering demonstration.
            rpm=max(row.min_rpm,min(row.max_rpm,round(2000-2.2*(row.material_hardness_hb-160))))
            feed=max(60,min(row.max_feed_mm_min,round(510-10*row.part_thickness_mm)))
            proposals.append({"order":row.work_order,"rpm":rpm,"feed_mm_min":feed})
        result={"proposals":proposals[:10],"records_evaluated":len(proposals),
                "all_within_bounds":all(400<=p["rpm"]<=2000 and 60<=p["feed_mm_min"]<=540
                                        for p in proposals),
                "actual_mes_commands_sent":False,
                "limits":"Unvalidated hypothetical setup, requires tool maker/machine sign-off"}
    elif project==97:
        features=["vibration_mm_s","temperature_c","cycles"]
        idx_train,idx_test=train_test_split(np.arange(len(data)),test_size=.25,random_state=SEED)
        model=RandomForestRegressor(n_estimators=60,min_samples_leaf=2,random_state=SEED,n_jobs=1)
        model.fit(data.iloc[idx_train][features],data.rul_hours_label.iloc[idx_train])
        pred=np.maximum(0,model.predict(data.iloc[idx_test][features]))
        result={"model":"sklearn RandomForestRegressor for synthetic RUL hours",
                "train_assets":len(idx_train),"untouched_test_assets":len(idx_test),
                "rul_test_mae_hours":_rounded(mean_absolute_error(
                    data.rul_hours_label.iloc[idx_test],pred)),
                "example_predicted_rul_hours":[_rounded(v) for v in pred[:8]],
                "maintenance_orders_created":False}
    elif project==98:
        text=data.text.tolist();labels=data.document_type_label.tolist()
        train_idx,test_idx=train_test_split(np.arange(len(data)),test_size=.25,
                                             stratify=labels,random_state=SEED)
        model=Pipeline([("tfidf",TfidfVectorizer(ngram_range=(1,2),strip_accents="unicode")),
                        ("classifier",LogisticRegression(max_iter=700,random_state=SEED))])
        model.fit([text[i] for i in train_idx],[labels[i] for i in train_idx])
        predicted=model.predict([text[i] for i in test_idx])
        result={"model":"Scikit-learn TF-IDF + LogisticRegression fitted on synthetic documents",
                "train_documents":len(train_idx),"unseen_documents":len(test_idx),
                "test_accuracy":_rounded(accuracy_score([labels[i] for i in test_idx],predicted)),
                "classes":sorted(set(labels)),
                "sample_predictions":[str(s) for s in predicted[:8]],
                "document_classification_human_review_required":True}
    elif project==99:
        alarm=(data.defect_pct>4)|(data.sensor_temp_c>98)|data.guard_open|data.emergency_stop
        alerts=data.loc[alarm].copy()
        result={"inspected_events":len(data),"alert_count":int(alarm.sum()),
                "high_defect_events":int((data.defect_pct>4).sum()),
                "open_guard_events":int(data.guard_open.sum()),
                "emergency_stop_events":int(data.emergency_stop.sum()),
                "recent_alert_lines":alerts.line.tail(8).tolist(),
                "equipment_shutdown_executed":False,
                "human_safety_review_required":True}
    else:
        # Metrics use a SQL aggregation over actual persisted event rows.
        with closing(connect()) as conn:
            ingest(conn,records)
            sql=conn.execute("""
              SELECT json_extract(payload_json, '$.line') AS line,
                     SUM(json_extract(payload_json,'$.planned_min')) AS planned_min,
                     SUM(json_extract(payload_json,'$.good_units')) AS good_units,
                     SUM(json_extract(payload_json,'$.run_min')) AS run_min,
                     SUM(json_extract(payload_json,'$.total_units')) AS total_units,
                     SUM(json_extract(payload_json,'$.good_units')*
                         json_extract(payload_json,'$.ideal_cycle_min')) AS good_ideal_min,
                     SUM(json_extract(payload_json,'$.good_units')*
                         json_extract(payload_json,'$.unit_price_brl')) AS revenue_brl
              FROM events WHERE project_id=100 GROUP BY line ORDER BY line
            """).fetchall()
        lines=[{"line":r["line"],"oee_pct":_rounded(100*r["good_ideal_min"]/r["planned_min"]),
                "synthetic_revenue_brl":_rounded(r["revenue_brl"]),
                "good_units":int(r["good_units"]),"planned_min":int(r["planned_min"])}
               for r in sql]
        total_good=sum(r["good_ideal_min"] for r in sql)
        total_planned=sum(r["planned_min"] for r in sql)
        result={"storage":"SQLite JSON1 materialized events",
                "lines":lines,"weighted_oee_pct":_rounded(100*total_good/total_planned),
                "total_revenue_brl":_rounded(sum(r["revenue_brl"] for r in sql)),
                "refresh":"explicit event ingestion, query on request; not connected to Power BI",
                "dax_executed":False}
    return {"project_id":project,"title":SPECS[project]["title"],
            "sample_count":len(records),"status":"EXECUTED against 100% SYNTHETIC events",
            "metrics":result,"sap_connected":False,"kafka_broker_verified":False,
            "production_ready":False}

def cli(project:int|None=None):
    import argparse
    p=argparse.ArgumentParser(description="Ten advanced industrial workflows on synthetic data")
    if project is None:p.add_argument("project",type=int,choices=sorted(SPECS))
    p.add_argument("--count",type=int,default=96)
    p.add_argument("--save",action="store_true")
    args=p.parse_args()
    chosen=project if project is not None else args.project
    generated=generate(chosen,count=args.count)
    report=analyze(chosen,generated)
    if args.save:
        (ROOT/"reports").mkdir(exist_ok=True)
        (ROOT/"reports"/f"{chosen:03d}.json").write_text(
            json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        with closing(connect(ROOT/"reports"/f"{chosen:03d}.sqlite3")) as db:ingest(db,generated)
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__":cli()
