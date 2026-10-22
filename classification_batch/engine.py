"""Reproducible, explicitly SYNTHETIC industrial classification demonstrations #031-#040.
No observed business data, deployed decisioning or demonstrated business impact.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
ROOT = Path(__file__).resolve().parent
CONFIG = {int(k):v for k,v in json.loads((ROOT/"config.json").read_text()).items()}
RANGES = {
"monthly_orders":(1,75),"late_shipments":(0,15),"support_tickets":(0,15),"tenure_months":(1,110),"price_change_pct":(-10,35),
"liquidity_ratio":(.2,3),"debt_ratio":(.05,1.5),"late_payments":(0,12),"years_operating":(1,45),"annual_revenue_m":(.2,100),
"sanction_alerts":(0,2),"late_filings":(0,8),"financial_leverage":(.2,5),"customer_concentration":(5,100),"audit_findings":(0,8),
"overtime_hours":(0,75),"absences":(0,12),"engagement_score":(0,100),"training_hours":(0,100),
"failed_logins":(0,70),"ip_reputation_risk":(0,1),"unexpected_ports":(0,10),"payload_entropy":(0,8),"asset_criticality":(1,5),
"vibration_mm_s":(.2,14),"oil_temp_c":(25,125),"pressure_variation":(0,24),"maintenance_age_days":(1,1000),"particle_count":(0,130),
"viscosity_change_pct":(0,35),"water_ppm":(0,2100),"oxidation_index":(0,8),"running_hours":(0,12000),
"amount_brl":(100,250000),"price_deviation_pct":(-20,80),"split_orders":(0,6),"weekend_flag":(0,1),"new_vendor_flag":(0,1),
"days_since_last_order":(1,365),"past_orders":(0,30),"stockout_events":(0,12),"active_machines":(1,35),"quoted_discount_pct":(0,25),
"supplier_delay_days":(0,45),"open_incidents":(0,12),"fill_rate_pct":(40,100),"capacity_utilization_pct":(40,120)
}
CATEGORIES = {
"contract_segment":["oem","tier1","aftermarket"],"sector":["steel","automotive","logistics"],
"jurisdiction":["domestic","international"],"shift":["day","night","mixed"],
"network_zone":["it","ot","dmz"],"pump_type":["centrifugal","hydraulic","gear"],
"lubricant_grade":["iso46","iso68","iso100"],"purchasing_group":["maintenance","operations","capex"],
"product_family":["bearings","hydraulics","tools"],"contract_type":["maintenance","freight","supply"]
}
def synthetic_data(project:int,n:int=600,seed:int=2026)->pd.DataFrame:
    if project not in CONFIG: raise ValueError("Unsupported project")
    if not isinstance(n,int) or n<150: raise ValueError("At least 150 observations required")
    cfg=CONFIG[project]; rng=np.random.default_rng(seed+project)
    d={name:rng.uniform(*RANGES[name],size=n) for name in cfg["numerics"]}
    d[cfg["categorical"]]=rng.choice(CATEGORIES[cfg["categorical"]],size=n)
    # Equation contains only known generated feature names, evaluated without builtins.
    z=eval(cfg["equation"],{"__builtins__":{}},d)
    z=(z-np.median(z))/max(np.std(z),1e-9)
    probability=1/(1+np.exp(-np.clip(z,-12,12)))
    y=rng.binomial(1,probability)
    frame=pd.DataFrame(d)
    frame.insert(0,"sample_id",[f"P{project:03d}-{i:05d}" for i in range(n)])
    frame["target_flag"]=y.astype(int)
    return frame
def validate(project:int,frame:pd.DataFrame)->None:
    cfg=CONFIG[project]
    required=["sample_id","target_flag",*cfg["numerics"],cfg["categorical"]]
    if len(frame)<150 or any(c not in frame for c in required):raise ValueError("Insufficient rows or columns")
    if frame[required].isnull().any().any() or frame.sample_id.duplicated().any():raise ValueError("Missing values or repeated IDs")
    if not set(frame.target_flag.unique()).issubset({0,1}) or frame.target_flag.nunique()<2:raise ValueError("Binary target must have both classes")
    for name in cfg["numerics"]:
        if not np.isfinite(pd.to_numeric(frame[name],errors="coerce")).all():raise ValueError("Invalid numeric predictor")
def evaluate(project:int,frame:pd.DataFrame|None=None)->dict:
    cfg=CONFIG[project]
    if frame is None:frame=synthetic_data(project)
    validate(project,frame)
    # Independent simulated entities only: stratified, seeded 60/20/20 split.
    from sklearn.model_selection import train_test_split
    tr,hold=train_test_split(frame,test_size=.4,random_state=2026,stratify=frame.target_flag)
    calibration,te=train_test_split(hold,test_size=.5,random_state=2026,stratify=hold.target_flag)
    features=[*cfg["numerics"],cfg["categorical"]]
    def preprocess():
        return ColumnTransformer([("numerics",StandardScaler(),cfg["numerics"]),("category",OneHotEncoder(handle_unknown="ignore",sparse_output=False),[cfg["categorical"]])])
    baseline=DummyClassifier(strategy="prior").fit(tr[features],tr.target_flag)
    lr=Pipeline([("preprocess",preprocess()),("model",LogisticRegression(max_iter=1200,random_state=2026))]).fit(tr[features],tr.target_flag)
    gb=Pipeline([("preprocess",preprocess()),("model",HistGradientBoostingClassifier(max_iter=100,max_depth=3,random_state=2026))]).fit(tr[features],tr.target_flag)
    # Threshold optimized on calibration only; holdout never participates in selection.
    thresholds=np.arange(.15,.851,.05)
    calp=gb.predict_proba(calibration[features])[:,1]
    threshold=float(max(thresholds,key=lambda x:(f1_score(calibration.target_flag,calp>=x),-abs(x-.5))))
    p=gb.predict_proba(te[features])[:,1]
    pred=(p>=threshold).astype(int)
    return {"project_id":project,"title":cfg["title"],"source":"synthetic deterministic generator, not real observations",
            "train_rows":len(tr),"calibration_rows":len(calibration),"test_rows":len(te),
            "positive_test_count":int(te.target_flag.sum()),"threshold_selected_on_calibration":round(threshold,3),
            "dummy_roc_auc":round(float(roc_auc_score(te.target_flag,baseline.predict_proba(te[features])[:,1])),4),
            "logistic_roc_auc":round(float(roc_auc_score(te.target_flag,lr.predict_proba(te[features])[:,1])),4),
            "gradient_boosting_roc_auc":round(float(roc_auc_score(te.target_flag,p)),4),
            "average_precision":round(float(average_precision_score(te.target_flag,p)),4),
            "f1":round(float(f1_score(te.target_flag,pred)),4),"precision":round(float(precision_score(te.target_flag,pred,zero_division=0)),4),
            "recall":round(float(recall_score(te.target_flag,pred,zero_division=0)),4),
            "brier_score":round(float(brier_score_loss(te.target_flag,p)),4),
            "confusion_matrix":confusion_matrix(te.target_flag,pred,labels=[0,1]).tolist(),
            "leakage_control":"preprocessing fit on train; threshold optimized on calibration; test untouched",
            "limitation":"synthetic generated labels; no external validation, production decisioning or measured impact"}
if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("project",type=int,choices=sorted(CONFIG))
    args=parser.parse_args()
    print(json.dumps(evaluate(args.project),indent=2))
