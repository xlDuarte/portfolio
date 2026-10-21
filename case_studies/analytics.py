"""Validated metrics for reproducible synthetic demonstration case studies.

Never convert synthetic results to claims about a real client's performance.
Split chronologically whenever the business question implies forecasting.
"""
from __future__ import annotations
import csv
import json
import math
import sqlite3
from collections import defaultdict
from pathlib import Path
from statistics import mean
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import average_precision_score, brier_score_loss, f1_score, mean_absolute_error, mean_squared_error, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
BASE=Path(__file__).resolve().parent
DATA=BASE/'data'
REPORTS=BASE/'reports'

def load(name):
    return pd.read_csv(DATA/name)

def oee():
    d=load('oee_shifts.csv')
    assert d[['planned_min','downtime_min','ideal_cycle_min','total_units','good_units']].notna().all().all()
    assert (d.planned_min > 0).all() and (d.downtime_min>=0).all() and (d.planned_min>d.downtime_min).all()
    assert ((d.good_units>=0)&(d.good_units<=d.total_units)).all()
    d['runtime_min']=d.planned_min-d.downtime_min
    d['availability']=d.runtime_min/d.planned_min
    d['performance']=d.ideal_cycle_min*d.total_units/d.runtime_min
    d['quality']=d.good_units/d.total_units
    assert (d.performance<=1).all(), 'Impossible count: performance > 100%'
    d['oee']=d.availability*d.performance*d.quality
    agg=d.groupby('line',sort=True).apply(lambda g:pd.Series({
        'planned_min':float(g.planned_min.sum()),
        'oee_weighted':float((g.ideal_cycle_min*g.good_units).sum()/g.planned_min.sum()),
        'mean_unweighted_oee':float(g.oee.mean()),
        'scrap_units':int((g.total_units-g.good_units).sum())
    }),include_groups=False)
    return {'case':'OEE production reliability','dataset':'synthetic','records':len(d),'total_planned_hours':round(d.planned_min.sum()/60,2),'oee_weighted_pct':round(100*(d.ideal_cycle_min*d.good_units).sum()/d.planned_min.sum(),2),'lines':agg.round(5).reset_index().to_dict('records'),'decision':'Investigate excess downtime and defects by line before setting improvement targets.'}

def supply():
    d=load('supply_orders.csv');assert d.order_id.is_unique
    assert (d.delivered_qty>=0).all() and (d.delivered_qty<=d.ordered_qty).all()
    d['on_time']=(pd.to_datetime(d.delivered_date)<=pd.to_datetime(d.promised_date))
    d['in_full']=d.delivered_qty>=d.ordered_qty
    d['otif']=d.on_time & d.in_full
    d['late_days']=(pd.to_datetime(d.delivered_date)-pd.to_datetime(d.promised_date)).dt.days.clip(lower=0)
    d['exposure_brl']=(d.ordered_qty-d.delivered_qty)*d.unit_value_brl
    con=sqlite3.connect(':memory:')
    try:
        d.to_sql('orders',con,index=False,if_exists='replace')
        q="""SELECT carrier,COUNT(*) AS orders,ROUND(100.0*AVG(CASE WHEN otif THEN 1.0 ELSE 0 END),2) AS otif_pct,ROUND(SUM(exposure_brl),2) AS shortage_brl FROM orders GROUP BY carrier ORDER BY otif_pct ASC"""
        by_carrier=pd.read_sql_query(q,con).to_dict('records')
    finally:con.close()
    return {'case':'Supply chain OTIF','dataset':'synthetic','records':len(d),'otif_pct':round(100*d.otif.mean(),2),'on_time_pct':round(100*d.on_time.mean(),2),'shortage_exposure_brl':round(float(d.exposure_brl.sum()),2),'late_mean_days':round(float(d.late_days.mean()),2),'by_carrier':by_carrier,'decision':'Segment late and partial deliveries by carrier and material to prioritize supplier reviews.'}

def capex():
    d=load('capex_projects.csv').sort_values('project_id')
    assert d.project_id.is_unique and d.isna().sum().sum()==0
    feats=['area_m2','robots','utilities_complexity']; n=int(.8*len(d))
    x_train,x_test=d.iloc[:n][feats],d.iloc[n:][feats]
    y_train,y_test=d.iloc[:n].actual_capex_brl,d.iloc[n:].actual_capex_brl
    model=make_pipeline(StandardScaler(),Ridge(alpha=1.0));model.fit(x_train,y_train)
    baseline=DummyRegressor(strategy='mean');baseline.fit(x_train,y_train)
    pred=model.predict(x_test);base=baseline.predict(x_test)
    mae=float(mean_absolute_error(y_test,pred));baseline_mae=float(mean_absolute_error(y_test,base))
    return {'case':'CAPEX regression','dataset':'synthetic','rows_train':len(x_train),'rows_test':len(x_test),'features':feats,'split':'80/20 by project_id (synthetic index; not chronological)','mae_brl':round(mae,2),'rmse_brl':round(float(np.sqrt(mean_squared_error(y_test,pred))),2),'baseline_mae_brl':round(baseline_mae,2),'better_than_baseline':bool(mae<baseline_mae),'decision':'Compare predicted cost range against quotes; validate on real projects before procurement use.'}

def churn():
    d=load('b2b_churn.csv').sort_values('account_id')
    feats=['tenure_months','support_tickets_90d','otd_rate','monthly_spend_brl'];n=int(.8*len(d))
    x_train,x_test=d.iloc[:n][feats],d.iloc[n:][feats]
    y_train,y_test=d.iloc[:n].churned_90d,d.iloc[n:].churned_90d
    assert set(y_train.unique())=={0,1}
    model=make_pipeline(StandardScaler(),LogisticRegression(max_iter=500,random_state=21));model.fit(x_train,y_train)
    prior=float(y_train.mean());baseline=DummyClassifier(strategy='prior');baseline.fit(x_train,y_train)
    probs=model.predict_proba(x_test)[:,1];base_probs=baseline.predict_proba(x_test)[:,1]
    pred=(probs>=.5).astype(int)
    return {'case':'B2B churn classification','dataset':'synthetic','rows_train':len(x_train),'rows_test':len(x_test),'positive_rate_train':round(prior,3),'f1':round(float(f1_score(y_test,pred,zero_division=0)),3),'precision':round(float(precision_score(y_test,pred,zero_division=0)),3),'recall':round(float(recall_score(y_test,pred,zero_division=0)),3),'roc_auc':round(float(roc_auc_score(y_test,probs)),3),'average_precision':round(float(average_precision_score(y_test,probs)),3),'brier':round(float(brier_score_loss(y_test,probs)),4),'baseline_brier':round(float(brier_score_loss(y_test,base_probs)),4),'decision':'Use calibrated churn risk for human-reviewed retention interventions, never automatic denial.'}

def forecast():
    d=load('demand_daily.csv').sort_values('date')
    assert d.date.is_unique and d.demand_units.notna().all()
    vals=d.demand_units.to_numpy(); origin=150
    rows=[]
    for t in range(origin,len(vals)):
        history=vals[:t] # strictly historical; rolling-origin backtest
        y=float(vals[t]);pred=float(history[-7]);base=float(history[-1])
        rows.append((y,pred,base))
    actual=np.array([r[0] for r in rows]);yp=np.array([r[1] for r in rows]);yb=np.array([r[2] for r in rows])
    mae=float(np.abs(actual-yp).mean());base_mae=float(np.abs(actual-yb).mean())
    return {'case':'Daily demand forecasting','dataset':'synthetic','rolling_test_days':len(rows),'training_min_days':origin,'method':'7-day seasonal naive, strictly past only','baseline':'last-observation persistence','mae_units':round(mae,2),'baseline_mae_units':round(base_mae,2),'wape_pct':round(float(100*np.abs(actual-yp).sum()/actual.sum()),2),'better_than_baseline':bool(mae<base_mae),'decision':'Apply rolling-origin assessment and compare inventory decisions against safety stock before deployment.'}

def run(case):
    funcs={'oee':oee,'supply':supply,'capex':capex,'churn':churn,'forecast':forecast}
    if case not in funcs:raise ValueError(f'Unsupported case: {case}')
    return funcs[case]()

def run_all():
    REPORTS.mkdir(exist_ok=True)
    results={key:run(key) for key in ('oee','supply','capex','churn','forecast')}
    (REPORTS/'metrics.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    return results
if __name__=='__main__':print(json.dumps(run_all(),ensure_ascii=False,indent=2))
