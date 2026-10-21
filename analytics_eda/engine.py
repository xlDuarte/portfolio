"""10 distinct EDA case studies on FIXED-SEED SYNTHETIC data only.

Technologies executed: Pandas, NumPy, SQLite SQL, Seaborn, Matplotlib and Plotly.
This is NOT evidence of observed industrial impact, actual F1 lap timing, job postings or market quotes.
"""
from __future__ import annotations
import json
import math
import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent / 'data'
NAMES = {
 11:'Global fleet electrification by region',12:'Workplace safety and ergonomic risk',
 13:'Warehouse capacity and dock utilisation',14:'Motorsport lap and sector benchmarks',
 15:'Supplier and batch quality',16:'SMED setup-time improvement',
 17:'Industrial and technology skills market',18:'Synthetic automotive and steel equities',
 19:'Parts dispatch and promised delivery',20:'Critical freight delay decomposition',
}
REQUIRED = {
 11:['region','year','fleet_units','ev_units','population','urbanization_pct'],
 12:['record_id','site','department','employee_hours','ergonomic_risk_score','safety_training_hours','reportable_incidents','near_misses'],
 13:['snapshot_id','hub','date','capacity_pallets','occupied_pallets','inbound_pallets','outbound_pallets','dock_hours_used','dock_hours_available'],
 14:['lap_id','car','session','compound','lap_number','track_temp_c','sector_1_s','sector_2_s','sector_3_s'],
 15:['batch_id','supplier','part_family','inspected_units','defect_units','rating_1to5','audit_date'],
 16:['changeover_id','asset','operation','phase','internal_setup_min','external_setup_min','production_run_hours','operator_count'],
 17:['job_id','region','role','seniority','salary_monthly_brl','skills','posted_date'],
 18:['ticker','date','close_brl','volume_shares'],
 19:['order_id','origin','route','mode','order_created_utc','dispatched_utc','delivered_utc','promised_utc','quantity'],
 20:['shipment_id','carrier','route','freight_mode','cause','delay_minutes','expedited_cost_brl','criticality'],
}
KEYS={11:['region','year'],12:['record_id'],13:['snapshot_id'],14:['lap_id'],15:['batch_id'],16:['changeover_id'],17:['job_id'],18:['ticker','date'],19:['order_id'],20:['shipment_id']}
MEASURES={11:['fleet_units','ev_units','population','urbanization_pct'],12:['employee_hours','ergonomic_risk_score','safety_training_hours','reportable_incidents','near_misses'],13:['capacity_pallets','occupied_pallets','inbound_pallets','outbound_pallets','dock_hours_used','dock_hours_available'],14:['lap_number','track_temp_c','sector_1_s','sector_2_s','sector_3_s'],15:['inspected_units','defect_units','rating_1to5'],16:['internal_setup_min','external_setup_min','production_run_hours','operator_count'],17:['salary_monthly_brl'],18:['close_brl','volume_shares'],19:['quantity'],20:['delay_minutes','expedited_cost_brl']}

def read_case(project:int,source:str|Path|None=None)->pd.DataFrame:
    if project not in NAMES: raise ValueError('Unsupported project: expected 011–020')
    path=Path(source) if source else DATA/f'{project:03d}.csv'
    d=pd.read_csv(path)
    missing=set(REQUIRED[project])-set(d.columns)
    if missing: raise ValueError(f'Missing columns: {sorted(missing)}')
    if d.empty: raise ValueError('Empty dataset')
    if d[REQUIRED[project]].isna().any().any(): raise ValueError('Nulls in required fields')
    if d.duplicated(KEYS[project]).any(): raise ValueError(f'Duplicate business key: {KEYS[project]}')
    for col in MEASURES[project]:
        d[col]=pd.to_numeric(d[col],errors='coerce')
    if d[MEASURES[project]].isna().any().any():raise ValueError('Non-numeric measurement')
    if not np.isfinite(d[MEASURES[project]].to_numpy(dtype=float)).all(): raise ValueError('Infinite measurement')
    if (d[MEASURES[project]]<0).any().any():raise ValueError('Negative measurement')
    return d

def _ratio(a,b): return float(a/b) if b else 0.0

def _sql_group(d:pd.DataFrame,query:str) -> list[dict]:
    conn=sqlite3.connect(':memory:')
    try:
        d.to_sql('records',conn,index=False,if_exists='replace')
        return pd.read_sql_query(query,conn).to_dict('records')
    finally:
        conn.close()

def analyze(project:int,source:str|Path|None=None)->tuple[dict,pd.DataFrame]:
    d=read_case(project,source).copy()
    if project==11:
        if (d.ev_units>d.fleet_units).any() or (d.urbanization_pct>100).any() or (d.fleet_units>d.population*2).any():raise ValueError('Invalid fleet, EV share or demographic bounds')
        d['ev_share_pct']=100*d.ev_units/d.fleet_units
        q=_sql_group(d,'SELECT region, COUNT(*) AS years, MAX(year) AS last_year, SUM(ev_units) AS reported_ev_observations FROM records GROUP BY region ORDER BY region')
        latest=d[d.year==d.year.max()];prev=d[d.year==d.year.max()-1]
        result=dict(years=sorted(int(x) for x in d.year.unique()),regions=int(d.region.nunique()),latest_year=int(d.year.max()),latest_ev_share_pct=round(100*_ratio(latest.ev_units.sum(),latest.fleet_units.sum()),3),prior_ev_share_pct=round(100*_ratio(prev.ev_units.sum(),prev.fleet_units.sum()),3),per_region=q)
    elif project==12:
        if (d.ergonomic_risk_score>100).any() or (d.employee_hours<=0).any():raise ValueError('Invalid exposure or ergonomics')
        group=_sql_group(d,'SELECT site, SUM(reportable_incidents) AS incidents, SUM(employee_hours) AS exposure_hours, SUM(near_misses) AS near_misses FROM records GROUP BY site ORDER BY site')
        for x in group:x['incident_rate_per_200k_hours']=round(200000*_ratio(x['incidents'],x['exposure_hours']),2)
        result=dict(incidents=int(d.reportable_incidents.sum()),total_exposure_hours=int(d.employee_hours.sum()),incident_rate_per_200k_hours=round(200000*_ratio(d.reportable_incidents.sum(),d.employee_hours.sum()),2),ergonomic_risk_median=round(float(d.ergonomic_risk_score.median()),2),by_site=group)
    elif project==13:
        if (d.capacity_pallets<=0).any() or (d.occupied_pallets>d.capacity_pallets).any() or (d.dock_hours_available<=0).any() or (d.dock_hours_used>d.dock_hours_available).any():raise ValueError('Impossible storage or dock capacity')
        d['occupancy_pct']=100*d.occupied_pallets/d.capacity_pallets;d['dock_use_pct']=100*d.dock_hours_used/d.dock_hours_available
        group=_sql_group(d,'SELECT hub, COUNT(*) AS snapshots, AVG(100.0*occupied_pallets/capacity_pallets) AS avg_occupancy_pct FROM records GROUP BY hub ORDER BY avg_occupancy_pct DESC')
        result=dict(snapshots=len(d),mean_occupancy_pct=round(float(d.occupancy_pct.mean()),2),near_capacity_count=int((d.occupancy_pct>=90).sum()),mean_dock_utilisation_pct=round(float(d.dock_use_pct.mean()),2),by_hub=group)
    elif project==14:
        if (d[['sector_1_s','sector_2_s','sector_3_s']]<=0).any().any() or (d.track_temp_c>80).any() or (d.lap_number<1).any():raise ValueError('Invalid telemetry sectors or temperature')
        d['lap_time_s']=d.sector_1_s+d.sector_2_s+d.sector_3_s
        group=_sql_group(d,'SELECT car, COUNT(*) AS laps, MIN(sector_1_s+sector_2_s+sector_3_s) AS best_lap_s, AVG(sector_1_s+sector_2_s+sector_3_s) AS avg_lap_s FROM records GROUP BY car ORDER BY best_lap_s')
        result=dict(laps=len(d),best_lap_s=round(float(d.lap_time_s.min()),3),median_lap_s=round(float(d.lap_time_s.median()),3),per_car=group,interpretation='Descriptive comparison only; unbalanced tyres/session/track conditions, no causal ranking.')
    elif project==15:
        if (d.inspected_units<=0).any() or (d.defect_units>d.inspected_units).any() or (d.rating_1to5>5).any() or (d.rating_1to5<1).any():raise ValueError('Invalid defect counts or ratings')
        d['defect_rate_pct']=100*d.defect_units/d.inspected_units
        group=_sql_group(d,'SELECT supplier, SUM(defect_units) AS defects, SUM(inspected_units) AS inspected FROM records GROUP BY supplier ORDER BY defects DESC')
        for x in group:x['defect_rate_pct']=round(100*_ratio(x['defects'],x['inspected']),2)
        result=dict(batches=len(d),defects=int(d.defect_units.sum()),inspected=int(d.inspected_units.sum()),weighted_defect_rate_pct=round(100*_ratio(d.defect_units.sum(),d.inspected_units.sum()),3),by_supplier=group)
    elif project==16:
        if not set(d.phase).issubset({'Before','After'}) or set(d.phase)!={'Before','After'}:raise ValueError('Both Before/After phases required')
        if (d.production_run_hours<=0).any() or (d.operator_count<=0).any():raise ValueError('Invalid setup sampling exposure')
        d['setup_min']=d.internal_setup_min+d.external_setup_min
        group=_sql_group(d,'SELECT operation, phase, COUNT(*) AS events, AVG(internal_setup_min+external_setup_min) AS mean_setup_min FROM records GROUP BY operation, phase')
        med=d.groupby('phase').setup_min.median()
        result=dict(changeovers=len(d),median_before_min=round(float(med['Before']),3),median_after_min=round(float(med['After']),3),median_reduction_pct=round(100*_ratio(med['Before']-med['After'],med['Before']),2),by_operation_phase=group,interpretation='Observational before/after synthetic sample; changes in job mix can confound estimates.')
    elif project==17:
        if (d.salary_monthly_brl<=0).any():raise ValueError('Invalid compensation')
        skills=d.skills.str.split('|').explode().str.strip();skills=skills[skills!='']
        if skills.empty:raise ValueError('No skills recorded')
        group=_sql_group(d,'SELECT region, COUNT(*) AS postings, AVG(salary_monthly_brl) AS mean_advertised_salary_brl FROM records GROUP BY region ORDER BY postings DESC')
        result=dict(postings=len(d),skills_frequency=skills.value_counts().head(12).to_dict(),salary_median_brl=round(float(d.salary_monthly_brl.median()),2),by_region=group,interpretation='SYNTHETIC job advertisements; not evidence of actual vacancies or labor-market salaries.')
    elif project==18:
        if (d.close_brl<=0).any() or (d.volume_shares<=0).any():raise ValueError('Invalid market quote')
        d['date']=pd.to_datetime(d.date,errors='coerce');
        if d.date.isna().any():raise ValueError('Invalid date')
        d=d.sort_values(['ticker','date']); d['log_return']=d.groupby('ticker').close_brl.transform(lambda x:np.log(x/x.shift(1)))
        d['rolling_20d_vol_pct']=d.groupby('ticker').log_return.transform(lambda x:100*np.sqrt(252)*x.rolling(20).std())
        d['drawdown_pct']=100*(d.close_brl/d.groupby('ticker').close_brl.cummax()-1)
        by=[]
        for ticker,v in d.groupby('ticker'):
            ret=v.log_return.dropna();by.append(dict(ticker=ticker,annualized_logreturn_vol_pct=round(float(ret.std(ddof=1)*np.sqrt(252)*100),2),max_drawdown_pct=round(float(v.drawdown_pct.min()),2)))
        group=_sql_group(d.assign(date=d.date.dt.strftime('%Y-%m-%d')),'SELECT ticker, COUNT(*) AS observations, MIN(date) AS first_day, MAX(date) AS last_day FROM records GROUP BY ticker')
        result=dict(quotes=len(d),instruments=len(by),volatility_by_symbol=by,coverage=group,interpretation='Artificial random walk; NOT observed prices or forward-looking investment guidance.')
    elif project==19:
        for c in ('order_created_utc','dispatched_utc','delivered_utc','promised_utc'):
            d[c]=pd.to_datetime(d[c],utc=True,errors='coerce')
        if d[['order_created_utc','dispatched_utc','delivered_utc','promised_utc']].isna().any().any():raise ValueError('Invalid shipping date')
        if (d.dispatched_utc<d.order_created_utc).any() or (d.delivered_utc<d.dispatched_utc).any() or (d.promised_utc<d.order_created_utc).any():raise ValueError('Impossible dispatch chronology')
        d['dispatch_hours']=(d.dispatched_utc-d.order_created_utc).dt.total_seconds()/3600
        d['total_lead_hours']=(d.delivered_utc-d.order_created_utc).dt.total_seconds()/3600
        d['on_time']=d.delivered_utc<=d.promised_utc
        group=_sql_group(d.assign(order_created_utc=d.order_created_utc.astype(str),dispatched_utc=d.dispatched_utc.astype(str),delivered_utc=d.delivered_utc.astype(str),promised_utc=d.promised_utc.astype(str)),'SELECT route, COUNT(*) AS orders FROM records GROUP BY route ORDER BY orders DESC')
        result=dict(orders=len(d),median_dispatch_hours=round(float(d.dispatch_hours.median()),2),p90_total_lead_hours=round(float(d.total_lead_hours.quantile(.90)),2),on_time_pct=round(100*float(d.on_time.mean()),2),by_route=group)
    elif project==20:
        if (d.expedited_cost_brl<0).any():raise ValueError('Invalid freight cost')
        group=_sql_group(d,'SELECT cause, COUNT(*) AS legs, SUM(delay_minutes) AS delay_minutes, SUM(expedited_cost_brl) AS expedite_cost_brl FROM records GROUP BY cause ORDER BY delay_minutes DESC')
        total=int(d.delay_minutes.sum());share=0
        for x in group:share+=_ratio(x['delay_minutes'],total);x['cumulative_delay_share_pct']=round(100*share,2)
        result=dict(shipments=len(d),delayed_shipments=int((d.delay_minutes>0).sum()),total_delay_hours=round(total/60,2),expedite_cost_brl=round(float(d.expedited_cost_brl.sum()),2),cause_pareto=group,interpretation='Cause labels are synthetic assumptions; descriptive Pareto does not prove root causality.')
    else:raise ValueError('Unknown project')
    return {'project':project,'name':NAMES[project],'data_provenance':'FIXED-SEED SYNTHETIC — NOT REAL BUSINESS DATA','records':len(d),**result},d

def run(project:int,source:str|Path|None=None)->dict:return analyze(project,source)[0]

def save_report(project:int,destination: str|Path)->dict:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import seaborn as sns
    import plotly.express as px
    out=Path(destination);out.mkdir(parents=True,exist_ok=True)
    result,d=analyze(project)
    (out/'metrics.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,default=str),encoding='utf8')
    d.to_csv(out/'validated_data.csv',index=False)
    fig,ax=plt.subplots(figsize=(8.5,4.0))
    if project==11: sns.lineplot(data=d,x='year',y='ev_share_pct',hue='region',marker='o',ax=ax);x='year';y='ev_share_pct';color='region'
    elif project==12: sns.scatterplot(data=d,x='ergonomic_risk_score',y='near_misses',hue='site',alpha=.72,ax=ax);x='ergonomic_risk_score';y='near_misses';color='site'
    elif project==13: sns.boxplot(data=d,x='hub',y='occupancy_pct',ax=ax);x='hub';y='occupancy_pct';color=None
    elif project==14: sns.boxplot(data=d,x='compound',y='lap_time_s',ax=ax);x='compound';y='lap_time_s';color=None
    elif project==15: sns.barplot(data=d,x='supplier',y='defect_rate_pct',estimator='mean',color='#478ba2',ax=ax);x='supplier';y='defect_rate_pct';color=None
    elif project==16: sns.boxplot(data=d,x='phase',y='setup_min',ax=ax);x='phase';y='setup_min';color=None
    elif project==17:
        f=d.skills.str.split('|').explode().value_counts().head(9).rename_axis('skill').reset_index(name='postings');sns.barplot(data=f,x='postings',y='skill',color='#478ba2',ax=ax);x='postings';y='skill';color=None
    elif project==18: sns.lineplot(data=d,x='date',y='close_brl',hue='ticker',ax=ax);x='date';y='close_brl';color='ticker'
    elif project==19: sns.boxplot(data=d,x='mode',y='total_lead_hours',ax=ax);x='mode';y='total_lead_hours';color=None
    else: c=pd.DataFrame(result['cause_pareto']);sns.barplot(data=c,x='delay_minutes',y='cause',color='#478ba2',ax=ax);x='delay_minutes';y='cause';color=None
    ax.set_title(f'#{project:03d} — SYNTHETIC EDA');fig.tight_layout();fig.savefig(out/'chart.svg');plt.close(fig)
    try:
        if project==17:pfig=px.bar(f,x=x,y=y,title=f'#{project:03d} — SYNTHETIC')
        elif project==20:pfig=px.bar(c,x=x,y=y,title=f'#{project:03d} — SYNTHETIC')
        elif project in (11,12,18):pfig=px.scatter(d,x=x,y=y,color=color,title=f'#{project:03d} — SYNTHETIC') if project==12 else px.line(d,x=x,y=y,color=color,title=f'#{project:03d} — SYNTHETIC')
        else:pfig=px.box(d,x=x,y=y,title=f'#{project:03d} — SYNTHETIC')
        pfig.write_html(out/'interactive.html',include_plotlyjs='cdn',full_html=True)
    except Exception as e:
        raise RuntimeError(f'Plotly chart generation for case {project} failed') from e
    return result

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('project',type=int);p.add_argument('--source');p.add_argument('--report-dir');a=p.parse_args()
 print(json.dumps(save_report(a.project,a.report_dir) if a.report_dir else run(a.project,a.source),ensure_ascii=False,indent=2,default=str))
