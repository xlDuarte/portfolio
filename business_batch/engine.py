"""Industrial Business Intelligence #081–#090 — executable SQLite/Pandas/ML analytics.

All source rows are generated from deterministic artificial scenarios.
SAP/Ariba schemas are only illustrative: NO live ERP, DAX runtime, Power BI
Desktop, real transactions, audited accounting, legal SOX compliance or
corporate performance are represented here.
"""
from __future__ import annotations
import argparse
import itertools
import json
import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
CONFIG={int(k):v for k,v in json.loads((ROOT/"config.json").read_text(encoding="utf-8")).items()}
SEED=20261022

def fixtures(seed:int=SEED) -> dict[str,pd.DataFrame]:
    """Deterministic, distinctly-grained ERP-like tables (all synthetic)."""
    if not isinstance(seed,int): raise ValueError("Integer seed required")
    rng=np.random.default_rng(seed)
    lines=np.array(["Heavy","Light","Turning"])
    sectors=np.array(["automotive","steel","industrial_service"])
    n=180
    customers=pd.DataFrame({
        "customer_id":[f"C{i:04d}" for i in range(n)],
        "segment":rng.choice(sectors,n),
        "tenure_months":rng.integers(3,65,n),
        "prior_12m_margin_brl":rng.uniform(12000,150000,n).round(2),
        "orders_12m":rng.integers(3,49,n),
        "late_orders_12m":rng.integers(0,8,n),
    })
    noise=rng.normal(0,8000,n)
    customers["future_12m_margin_brl"]=np.maximum(
        0,9000+.80*customers.prior_12m_margin_brl+650*customers.orders_12m
        -2200*customers.late_orders_12m+48*customers.tenure_months+noise).round(2)
    count=1200
    order_month=rng.integers(0,24,count)
    invoices=pd.DataFrame({
        "invoice_id":[f"I{i:05d}" for i in range(count)],
        "customer_id":rng.choice(customers.customer_id,count),
        "invoice_date":(pd.Timestamp("2024-01-01")+pd.to_timedelta(order_month*30+ rng.integers(0,28,count),unit="D")).strftime("%Y-%m-%d"),
        "amount_brl":rng.uniform(400,38000,count).round(2),
        "gross_margin_pct":rng.uniform(.09,.39,count).round(5),
    })
    invoices["contribution_margin_brl"]=(invoices.amount_brl*invoices.gross_margin_pct).round(2)
    m=480
    planned=rng.integers(420,481,m)
    downtime=rng.integers(4,95,m)
    operating=planned-downtime
    ideal_cycle=np.full(m,1.25)
    total=np.maximum(1,(operating*rng.uniform(.69,.95,m)/ideal_cycle).astype(int))
    good=np.maximum(0,total-rng.integers(0,13,m))
    shifts=pd.DataFrame({
        "shift_id":np.arange(m)+1,
        "date":(pd.Timestamp("2025-01-01")+pd.to_timedelta(np.arange(m)//3,unit="D")).strftime("%Y-%m-%d"),
        "line":np.tile(lines,160),
        "planned_min":planned,"downtime_min":downtime,"operating_min":operating,
        "ideal_cycle_min":ideal_cycle,"total_units":total,"good_units":good,
        "quota_units":rng.integers(280,370,m)
    })
    marketing_n=600
    randomized=rng.integers(0,2,marketing_n)
    segment=rng.integers(0,3,marketing_n)
    baseline=190+segment*35+rng.normal(0,33,marketing_n)
    campaigns=pd.DataFrame({"prospect_id":np.arange(marketing_n)+1,
        "segment":segment,"treated":randomized,
        "observed_margin_brl":np.round(baseline+randomized*72,2),
        "campaign_spend_brl":randomized*45.0})
    payments=pd.DataFrame({
        "payment_id":[f"PAY{i:05d}" for i in range(320)],
        "vendor_id":rng.choice([f"V{i:03d}" for i in range(22)],320),
        "invoice_ref":[f"INV{i:04d}" for i in range(320)],
        "payment_date":(pd.Timestamp("2025-01-01")+pd.to_timedelta(rng.integers(0,220,320),unit="D")).strftime("%Y-%m-%d"),
        "amount_brl":rng.uniform(500,15000,320).round(2),
        "approval_limit_brl":np.full(320,10000.0),
    })
    # Explicit anomalies for a non-fraud, manually reviewed rules demonstration.
    payments.loc[0,["vendor_id","invoice_ref","amount_brl"]]=["V001","DUP99",7800.]
    payments.loc[1,["vendor_id","invoice_ref","amount_brl"]]=["V001","DUP99",7800.]
    payments.loc[2,["vendor_id","payment_date","amount_brl"]]=["V005","2025-04-17",9800.]
    payments.loc[3,["vendor_id","payment_date","amount_brl"]]=["V005","2025-04-17",9700.]
    risk=pd.DataFrame({
        "event_id":[f"R{i:04d}" for i in range(130)],
        "plant":rng.choice(["Forge","Machining","Warehouse"],130),
        "hazard":rng.choice(["handling","equipment","fire","logistics"],130),
        "likelihood":rng.integers(1,6,130),"impact":rng.integers(1,6,130)
    })
    risk["risk_score"]=risk.likelihood*risk.impact
    ids=range(12)
    capex=pd.DataFrame({
        "project_id":[f"CAP{i:03d}" for i in ids],
        "name":[f"Fictional project {i:02d}" for i in ids],
        "capex_k_brl":rng.integers(180,600,12),
        "year1_k_brl":rng.integers(85,260,12),
        "year2_k_brl":rng.integers(85,260,12),
        "year3_k_brl":rng.integers(85,260,12),
        "year4_k_brl":rng.integers(85,260,12),
        "strategic_score":rng.integers(1,6,12)
    })
    month=pd.date_range("2023-01-01",periods=36,freq="MS")
    trend=np.arange(36)
    gross=np.maximum(10000,115000+2050*trend+14000*np.sin(2*np.pi*trend/12)+rng.normal(0,3100,36))
    discount=np.full(36,.025)
    tax=np.full(36,.12)
    billing=pd.DataFrame({"month":month.strftime("%Y-%m-%d"),"gross_brl":gross.round(2),
                          "discount_rate":discount,"tax_rate":tax})
    billing["net_revenue_brl"]=(billing.gross_brl*(1-discount)*(1-tax)).round(2)
    ledger=billing[["month","net_revenue_brl"]].rename(columns={"net_revenue_brl":"posted_revenue_brl"}).copy()
    ledger.loc[4,"posted_revenue_brl"]+=173.0
    ledger.loc[17,"posted_revenue_brl"]-=290.0
    # ERP-like purchasing facts: vendor, category, dates and actual unit prices.
    p=480
    categories=["bearings","hydraulics","tooling","energy"]
    supplier_ids=[f"V{i:03d}" for i in range(22)]
    suppliers={v:rng.choice(categories) for v in supplier_ids}
    vendor=rng.choice(supplier_ids,p)
    cat=[suppliers[v] for v in vendor]
    prices={"bearings":130,"hydraulics":420,"tooling":95,"energy":270}
    price=np.array([prices[c] for c in cat])*rng.uniform(.8,1.3,p)
    order_days=rng.integers(0,280,p)
    lead=rng.integers(2,22,p)
    actual=lead+rng.integers(-2,8,p)
    procurement=pd.DataFrame({
        "po_id":[f"PO{i:04d}" for i in range(p)],
        "vendor_id":vendor,"category":cat,
        "order_date":(pd.Timestamp("2025-01-01")+pd.to_timedelta(order_days,unit="D")).strftime("%Y-%m-%d"),
        "quantity":rng.integers(1,80,p),
        "unit_price_brl":price.round(2),"quoted_lead_days":lead,
        "actual_lead_days":actual})
    procurement["spend_brl"]=(procurement.quantity*procurement.unit_price_brl).round(2)
    d=300
    qty=rng.integers(8,46,d)
    peak=rng.uniform(90,480,d)
    offpeak=rng.uniform(300,1250,d)
    base_hours=rng.uniform(12,70,d)
    overtime=rng.uniform(0,18,d)
    materials=rng.uniform(800,4900,d)
    costs=pd.DataFrame({
        "batch_id":[f"B{i:04d}" for i in range(d)],
        "line":rng.choice(lines,d),"units":qty,"peak_kwh":peak.round(3),
        "offpeak_kwh":offpeak.round(3),"regular_hours":base_hours.round(3),
        "overtime_hours":overtime.round(3),
        "material_cost_brl":materials.round(2),
        "budget_unit_brl":rng.uniform(190,250,d).round(2)})
    return {"dim_customers":customers,"fact_invoices":invoices,"fact_shifts":shifts,
            "fact_campaigns":campaigns,"fact_payments":payments,"fact_risk":risk,
            "fact_capex":capex,"fact_billing":billing,"fact_ledger":ledger,
            "fact_procurement":procurement,"fact_costs":costs}

def validate_tables(tables:dict[str,pd.DataFrame])->None:
    if not isinstance(tables,dict) or not tables:raise ValueError("Table dictionary required")
    keys={"dim_customers":"customer_id","fact_invoices":"invoice_id",
          "fact_shifts":"shift_id","fact_campaigns":"prospect_id",
          "fact_payments":"payment_id","fact_risk":"event_id",
          "fact_capex":"project_id","fact_billing":"month","fact_ledger":"month",
          "fact_procurement":"po_id","fact_costs":"batch_id"}
    if set(keys)!=set(tables):raise ValueError("Unexpected or missing tables")
    for name,key in keys.items():
        df=tables[name]
        if df.empty or df[key].isna().any() or df[key].duplicated().any():
            raise ValueError("Invalid identifiers in "+name)
        if df.isna().any().any():raise ValueError("Null data in "+name)
    if not set(tables["fact_invoices"].customer_id)<=set(tables["dim_customers"].customer_id):
        raise ValueError("Orphan invoices")
    for col in ("planned_min","operating_min","good_units","total_units"):
        if (tables["fact_shifts"][col]<0).any():raise ValueError("Negative OEE input")
    shifts=tables["fact_shifts"]
    if (shifts.operating_min>shifts.planned_min).any() or (shifts.good_units>shifts.total_units).any():
        raise ValueError("Impossible OEE inputs")
    if (tables["fact_procurement"].quantity<=0).any():raise ValueError("Invalid PO quantity")

def open_sqlite(tables:dict[str,pd.DataFrame])->sqlite3.Connection:
    validate_tables(tables)
    conn=sqlite3.connect(":memory:")
    for name,frame in tables.items():
        frame.to_sql(name,conn,index=False,if_exists="replace")
    return conn

def sql_frame(project:int,conn:sqlite3.Connection)->pd.DataFrame:
    if project not in CONFIG:raise ValueError("Unknown business case")
    query=(ROOT/"sql"/f"{project:03d}.sql").read_text(encoding="utf-8")
    return pd.read_sql_query(query,conn)

def _native(value):
    """Serialize NumPy scalar results to plain JSON-compatible values."""
    if isinstance(value,(np.integer,)):return int(value)
    if isinstance(value,(np.floating,)):return float(value)
    if isinstance(value,(np.ndarray,)):return value.tolist()
    if isinstance(value,pd.Timestamp):return value.isoformat()
    return value

def _export_rows(df:pd.DataFrame,n=16)->list[dict]:
    return [{k:_native(v) for k,v in row.items()} for row in df.head(n).to_dict("records")]

def _regression(df:pd.DataFrame)->dict:
    features=["tenure_months","prior_12m_margin_brl","orders_12m","late_orders_12m"]
    x=df[features]
    y=df.future_12m_margin_brl
    tr,te=train_test_split(np.arange(len(df)),test_size=.25,random_state=SEED)
    model=RandomForestRegressor(n_estimators=85,min_samples_leaf=2,random_state=SEED,n_jobs=1)
    model.fit(x.iloc[tr],y.iloc[tr])
    pred=model.predict(x.iloc[te])
    baseline=np.full(len(te),float(y.iloc[tr].median()))
    return {"model":"Sklearn RandomForestRegressor (fitted on synthetic accounts)",
            "train_accounts":len(tr),"test_accounts":len(te),
            "target":"future_12m_margin_brl",
            "test_mae_brl":round(float(mean_absolute_error(y.iloc[te],pred)),2),
            "baseline_test_mae_brl":round(float(mean_absolute_error(y.iloc[te],baseline)),2),
            "test_r2":round(float(r2_score(y.iloc[te],pred)),5),
            "predictions":_export_rows(pd.DataFrame({
                "customer_id":df.customer_id.iloc[te].to_numpy(),
                "actual_future_margin_brl":y.iloc[te].to_numpy(),
                "predicted_future_margin_brl":np.round(pred,2)}),12),
            "risk":"Not a calibrated or approved account credit/revenue decision model"}

def _oee(df:pd.DataFrame)->dict:
    denom=df.planned_min.sum()
    availability=float(df.operating_min.sum()/denom)
    ideal=np.sum(df.total_units*df.ideal_cycle_min)
    performance=float(ideal/df.operating_min.sum())
    quality=float(df.good_units.sum()/df.total_units.sum())
    weighted_oee=float(np.sum(df.good_units*df.ideal_cycle_min)/denom)
    if not (0<=availability<=1 and 0<=quality<=1 and 0<=performance<=1):
        raise ValueError("Invalid OEE factors")
    return {"weighted_oee_pct":round(100*weighted_oee,3),
            "availability_pct":round(100*availability,3),
            "performance_pct":round(100*performance,3),
            "quality_pct":round(100*quality,3),
            "quota_attainment_pct":round(float(100*df.good_units.sum()/df.quota_units.sum()),3),
            "lines":_export_rows(df[["line","planned_min","operating_min","good_units","total_units","quota_units"]]),
            "calculation":"sum(good_units * ideal_cycle_min) / sum(planned_min)",
            "note":"Line aggregates are summed before deriving total OEE"}

def _campaign(df:pd.DataFrame)->dict:
    treated=df[df.treated==1];control=df[df.treated==0]
    if len(treated)<2 or len(control)<2:raise ValueError("Both assignment arms required")
    lift=float(treated.observed_margin_brl.mean()-control.observed_margin_brl.mean())
    spend=float(treated.campaign_spend_brl.sum())
    estimated_incremental=lift*len(treated)
    roi=(estimated_incremental-spend)/max(spend,1)
    return {"treated_n":len(treated),"control_n":len(control),
            "randomized_in_fixture":True,"observed_margin_lift_brl":round(lift,2),
            "campaign_spend_brl":round(spend,2),
            "estimated_incremental_margin_brl":round(estimated_incremental,2),
            "roi_pct":round(100*roi,3),
            "causality_note":"Simulated randomized assignment, no real-world causal identification"}

def _segment(df:pd.DataFrame,reference="2026-01-01")->dict:
    df=df.copy()
    df["last_date"]=pd.to_datetime(df.last_date)
    recency=(pd.Timestamp(reference)-df.last_date).dt.days
    if (recency<0).any():raise ValueError("Invoice dates after reference")
    df["recency_days"]=recency
    df=df.sort_values(["revenue_brl","customer_id"],ascending=[False,True]).reset_index(drop=True)
    total=df.revenue_brl.sum()
    df["cum_share"]=df.revenue_brl.cumsum()/max(total,.01)
    df["abc"]=np.where(df.cum_share<=.8,"A",np.where(df.cum_share<=.95,"B","C"))
    # Stable 1..5 quantile scores, with ties handled by rank first.
    for feature,ascending,label in [("recency_days",False,"r"),("orders",True,"f"),("revenue_brl",True,"m")]:
        df[label]=pd.qcut(df[feature].rank(method="first",ascending=ascending),
                         5,labels=[1,2,3,4,5]).astype(int)
    df["rfm"]=df["r"].astype(str)+df["f"].astype(str)+df["m"].astype(str)
    return {"accounts":len(df),
            "revenue_total_brl":round(float(total),2),
            "abc_counts":{key:int(val) for key,val in df.abc.value_counts().to_dict().items()},
            "top_accounts":_export_rows(df[["customer_id","orders","revenue_brl","recency_days","abc","rfm"]],12),
            "note":"ABC threshold based on cumulative net sales; scores are empirical quintiles"}

def _audit(df:pd.DataFrame)->dict:
    findings=df[(df.duplicate_ref==1)|(df.weekend_payment==1)|
                (df.limit_exceeded==1)|(df.possible_split==1)].copy()
    findings["flags"]=findings[["duplicate_ref","weekend_payment",
                                "limit_exceeded","possible_split"]].sum(axis=1)
    findings=findings.sort_values(["flags","payment_id"],ascending=[False,True])
    return {"payments_checked":len(df),"flagged_payments":len(findings),
            "flag_types":{col:int(df[col].sum()) for col in
                          ("duplicate_ref","weekend_payment","limit_exceeded","possible_split")},
            "findings_for_human_review":_export_rows(findings,18),
            "disclaimer":"SOX-like control signals only; not fraud, legal compliance or disciplinary conclusions"}

def _risks(df:pd.DataFrame)->dict:
    if not df.likelihood.between(1,5).all() or not df.impact.between(1,5).all():
        raise ValueError("Risk inputs must be integers 1..5")
    matrix=np.zeros((5,5),dtype=int)
    for row in df.itertuples():
        matrix[int(row.likelihood)-1,int(row.impact)-1]=int(row.events)
    critical=int(df.loc[df.likelihood*df.impact>=15,"events"].sum())
    return {"matrix_5x5":matrix.tolist(),"events":int(df.events.sum()),
            "critical_or_high_events":critical,
            "critical_share_pct":round(100*critical/max(1,int(df.events.sum())),3),
            "risk_scale":"probability 1..5 × impact 1..5, threshold ≥15",
            "not_observed_incidents":True}

def _capex(df:pd.DataFrame, budget_k_brl:float=1600,rate:float=.13)->dict:
    if not (0<budget_k_brl<1e6 and 0<=rate<1):raise ValueError("Invalid budget or discount")
    projects=df.copy()
    npv=-projects.capex_k_brl.to_numpy(dtype=float)
    for i in range(1,5):
        npv+=projects[f"year{i}_k_brl"].to_numpy(dtype=float)/(1+rate)**i
    projects["npv_k_brl"]=npv.round(4)
    # Exhaustive discrete knapsack on 12 proposals (2^12 combinations).
    costs=projects.capex_k_brl.to_numpy(dtype=float)
    best_idx=()
    best_npv=0.0
    for mask in range(1<<len(projects)):
        selection=tuple(i for i in range(len(projects)) if mask&(1<<i))
        total_cost=sum(costs[i] for i in selection)
        if total_cost>budget_k_brl:continue
        value=sum(npv[i] for i in selection)
        if value>best_npv+1e-9:
            best_npv=value;best_idx=selection
    total_cost=float(sum(costs[i] for i in best_idx))
    return {"algorithm":"exhaustive binary knapsack, 4096 feasible/infeasible subsets",
            "budget_k_brl":budget_k_brl,"discount_rate":rate,
            "selected_project_ids":projects.project_id.iloc[list(best_idx)].tolist(),
            "selected_capex_k_brl":round(total_cost,2),
            "selected_npv_k_brl":round(float(best_npv),3),
            "remaining_budget_k_brl":round(float(budget_k_brl-total_cost),2),
            "ranking":_export_rows(projects.sort_values("npv_k_brl",ascending=False)
                                  [["project_id","capex_k_brl","npv_k_brl"]],12),
            "note":"Purely hypothetical cash flows and independent projects; no real approved CAPEX"}

def _bill(df:pd.DataFrame)->dict:
    d=df.copy().sort_values("month").reset_index(drop=True)
    d["difference_brl"]=(d["net_revenue_brl"]-d["posted_revenue_brl"]).round(2)
    mismatch=d[d.difference_brl.abs()>.01]
    # A truly temporal holdout: 6 months not available at training time.
    n=len(d);cut=n-6
    def features(t):
        t=np.asarray(t,dtype=float)
        return np.column_stack((t,np.sin(2*np.pi*t/12),np.cos(2*np.pi*t/12)))
    t=np.arange(n)
    model=Ridge(alpha=1.0).fit(features(t[:cut]),d.net_revenue_brl.iloc[:cut])
    predicted=np.maximum(0,model.predict(features(t[cut:])))
    forecast=np.maximum(0,model.predict(features(np.arange(n,n+3))))
    return {"months":n,"reconciliation_mismatches":len(mismatch),
            "absolute_unreconciled_brl":round(float(mismatch.difference_brl.abs().sum()),2),
            "mismatches":_export_rows(mismatch[["month","net_revenue_brl","posted_revenue_brl","difference_brl"]],10),
            "temporal_train_months":cut,"untouched_test_months":6,
            "holdout_mae_brl":round(float(mean_absolute_error(d.net_revenue_brl.iloc[cut:],predicted)),2),
            "model":"sklearn Ridge fitted on time index, yearly sine/cosine",
            "future_months":(pd.date_range(pd.Timestamp(d.month.iloc[-1])+pd.offsets.MonthBegin(1),
                                            periods=3,freq="MS").strftime("%Y-%m-%d")).tolist(),
            "future_net_revenue_forecast_brl":[round(float(x),2) for x in forecast],
            "future_actuals_available":False,
            "accounting_note":"Synthetic tax/discount placeholders, not Brazilian tax or accounting advice"}

def _spend(df:pd.DataFrame)->dict:
    total=float(df.spend_brl.sum())
    vendors=df.groupby("vendor_id",as_index=False).agg(spend_brl=("spend_brl","sum"),
                                                        orders=("po_id","count"))
    shares=vendors.spend_brl/total
    hhi=float(np.square(shares).sum())
    categories=df.groupby("category",as_index=False).agg(spend_brl=("spend_brl","sum"))
    late=int((df.actual_lead_days>df.quoted_lead_days).sum())
    return {"purchase_orders":len(df),"total_spend_brl":round(total,2),
            "supplier_hhi":round(hhi,5),
            "on_time_delivery_pct":round(100*(1-late/len(df)),3),
            "category_spend":_export_rows(categories.sort_values("spend_brl",ascending=False)),
            "top_vendors":_export_rows(vendors.sort_values("spend_brl",ascending=False),10),
            "note":"Ariba-like fictional ledger only; supplier quality not validated"}

def _cost(df:pd.DataFrame)->dict:
    if not (df.units>0).all():raise ValueError("Nonpositive batch output")
    d=df.copy()
    d["energy_cost_brl"]=d.peak_kwh*.97+d.offpeak_kwh*.42
    d["labor_cost_brl"]=d.regular_hours*50+d.overtime_hours*50*1.5
    d["total_cost_brl"]=d.energy_cost_brl+d.labor_cost_brl+d.material_cost_brl
    d["unit_cost_brl"]=d.total_cost_brl/d.units
    d["variance_brl"]=d.total_cost_brl-d.budget_unit_brl*d.units
    line=d.groupby("line",as_index=False).agg(total_cost_brl=("total_cost_brl","sum"),
                                             units=("units","sum"),
                                             variance_brl=("variance_brl","sum"))
    line["weighted_unit_cost_brl"]=line.total_cost_brl/line.units
    return {"batches":len(d),"manufactured_units":int(d.units.sum()),
            "total_manufacturing_cost_brl":round(float(d.total_cost_brl.sum()),2),
            "weighted_unit_cost_brl":round(float(d.total_cost_brl.sum()/d.units.sum()),3),
            "energy_cost_brl":round(float(d.energy_cost_brl.sum()),2),
            "overtime_cost_brl":round(float((d.overtime_hours*50*1.5).sum()),2),
            "budget_variance_brl":round(float(d.variance_brl.sum()),2),
            "line_summary":_export_rows(line,10),
            "tariff_scenario_brl_per_kwh":{"peak":.97,"offpeak":.42},
            "note":"Simulated costs; tariffs and overtime are assumptions, not payroll rules"}

def evaluate(project:int,tables:dict|None=None,save:bool=False)->dict:
    if project not in CONFIG:raise ValueError("Unknown project")
    tables=fixtures() if tables is None else tables
    with open_sqlite(tables) as conn:
        sql=sql_frame(project,conn)
    if sql.empty:raise ValueError("SQL query returned no rows")
    methods={81:_regression,82:_oee,83:_campaign,84:_segment,85:_audit,
             86:_risks,87:_capex,88:_bill,89:_spend,90:_cost}
    result={"project_id":project,"title":CONFIG[project]["title"],
            "data_origin":"100% SYNTHETIC fictional ERP-like data",
            "sql_engine":"SQLite3 executing sql/{:03d}.sql".format(project),
            "sql_result_rows":len(sql),"metrics":methods[project](sql),
            "production_ready":False,"sap_ariba_connected":False,
            "power_bi_dax_executed":False,
            "limitations":"No real SAP, Ariba, Power BI Desktop, external validation, live ERP or audited business value"}
    if save:
        for folder in ("reports","exports","figures"):
            (ROOT/folder).mkdir(exist_ok=True)
        sql.to_csv(ROOT/"exports"/f"{project:03d}_query.csv",index=False)
        # CSV star/fact source tables can be imported into Power BI Desktop.
        # Do not mistake them for a .pbix or a DAX engine execution.
        (ROOT/"exports"/"raw").mkdir(exist_ok=True)
        for name,raw in tables.items():
            raw.to_csv(ROOT/"exports"/"raw"/f"{name}.csv",index=False)
        (ROOT/"reports"/f"{project:03d}.json").write_text(
            json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        chart(project,result,sql,ROOT/"figures"/f"{project:03d}.png")
    return result

def chart(project:int,result:dict,df:pd.DataFrame,filename:Path)->None:
    """Produce domain-specific diagnostic PNG, not a stock graph."""
    m=result["metrics"]
    fig,ax=plt.subplots(figsize=(9,4.6))
    if project==81:
        rows=m["predictions"];ax.scatter([r["actual_future_margin_brl"] for r in rows],
                                       [r["predicted_future_margin_brl"] for r in rows])
        ax.set(xlabel="True future contribution margin, synthetic BRL",
               ylabel="Predicted contribution margin, synthetic BRL")
    elif project==82:
        x=df.line.astype(str).to_numpy();y=df.good_units*df.ideal_cycle_min/df.planned_min*100
        ax.bar(x,y);ax.set(ylabel="Line OEE, %")
    elif project==83:
        ax.bar(["campaign","control"],[float(df.loc[df.treated==1,"observed_margin_brl"].mean()),
               float(df.loc[df.treated==0,"observed_margin_brl"].mean())])
        ax.set(ylabel="Simulated contribution per prospect (BRL)")
    elif project==84:
        ax.bar(list(m["abc_counts"]),list(m["abc_counts"].values()));ax.set(ylabel="Accounts by ABC")
    elif project==85:
        flags=m["flag_types"];ax.bar(list(flags),list(flags.values()));ax.tick_params(axis="x",labelrotation=20)
    elif project==86:
        im=ax.imshow(m["matrix_5x5"],cmap="viridis")
        fig.colorbar(im,ax=ax,label="synthetic event count")
        ax.set(xlabel="Impact (1–5)",ylabel="Likelihood (1–5)",
               xticks=range(5),xticklabels=range(1,6),yticks=range(5),yticklabels=range(1,6))
    elif project==87:
        rows=m["ranking"];ax.bar([r["project_id"] for r in rows],
                                 [r["npv_k_brl"] for r in rows]);ax.tick_params(axis="x",labelrotation=55)
        ax.set(ylabel="NPV (synthetic kBRL)")
    elif project==88:
        ax.plot(df.month,df.net_revenue_brl,label="Invoiced net revenue")
        ax.plot(df.month,df.posted_revenue_brl,label="Ledger")
        ax.legend();ax.tick_params(axis="x",labelrotation=80)
    elif project==89:
        rows=m["category_spend"];ax.bar([r["category"] for r in rows],[r["spend_brl"] for r in rows])
        ax.set(ylabel="Fictional purchasing BRL")
    elif project==90:
        rows=m["line_summary"];ax.bar([r["line"] for r in rows],
                                      [r["weighted_unit_cost_brl"] for r in rows])
        ax.set(ylabel="Weighted manufacturing cost per unit (BRL)")
    ax.set_title(f"#{project:03d} — synthetic evidence")
    fig.tight_layout()
    fig.savefig(filename,dpi=125)
    plt.close(fig)

def cli(project:int|None=None):
    parser=argparse.ArgumentParser(description="Verified SQL/BI industrial finance demonstration")
    if project is None:parser.add_argument("project",type=int,choices=sorted(CONFIG))
    parser.add_argument("--save",action="store_true")
    args=parser.parse_args()
    chosen=project if project is not None else args.project
    print(json.dumps(evaluate(chosen,save=args.save),ensure_ascii=False,indent=2))
if __name__=="__main__":cli()
