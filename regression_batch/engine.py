"""Reproducible domain-specific regressions on EXPLICITLY SYNTHETIC datasets.

This project shows genuine scikit-learn + XGBoost training, temporal leakage controls,
validation-set conformal intervals, baselines and held-out diagnostic plots.
No generated data are observations of an actual employer or market.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor

ROOT=Path(__file__).resolve().parent
CONFIG={int(i):v for i,v in json.loads((ROOT/'config.json').read_text(encoding='utf8')).items()}

def synthetic_data(project: int, n: int=420, seed: int=2026) -> pd.DataFrame:
    """Generate one independently specified, domain-plausible scenario per project."""
    if project not in CONFIG: raise ValueError('Unknown regression project')
    if type(n) is not int or not 120 <= n <= 100000:
        raise ValueError('n must be an integer between 120 and 100000')
    r=np.random.default_rng(seed+project)
    a=lambda lo,hi:r.uniform(lo,hi,n)
    integers=lambda lo,hi:r.integers(lo,hi+1,n)
    cat=lambda opts:r.choice(opts,size=n)
    d={}
    if project==22:
        d.update(age_years=a(.2,12),odometer_km=a(3000,280000),service_score=a(30,100),incident_count=integers(0,4),battery_health_pct=a(58,100),original_price_brl=a(70000,340000),powertrain=cat(['gasoline','diesel','electric','hybrid']))
        y=np.asarray(d['original_price_brl'])*np.exp(-.105*d['age_years']-1.0e-6*d['odometer_km']) + 170*d['service_score']-6800*d['incident_count']+ (np.asarray(d['powertrain'])=='electric')*160*d['battery_health_pct'] +r.normal(0,8700,n)
    elif project==23:
        d.update(experience_years=a(0,22),certifications=integers(0,8),responsibility_level=integers(1,5),local_cost_index=a(.75,1.5),leadership_years=a(0,11),overtime_hours=a(0,45),specialty=cat(['automation','data','mechanical','electrical']))
        specialty=pd.Series(d['specialty']).map({'automation':1200,'data':1800,'mechanical':800,'electrical':1100}).to_numpy()
        y=(4000+450*d['experience_years']+380*d['certifications']+2500*d['responsibility_level']+280*d['leadership_years']+105*d['overtime_hours']+specialty)*d['local_cost_index']+r.normal(0,1550,n)
    elif project==24:
        d.update(training_hours=a(8,160),practice_score=a(15,95),prior_score=a(15,90),study_weeks=a(1,26),attendance_pct=a(45,100),difficulty_index=a(1,5),certification_track=cat(['java','industrial_safety','data','automation']))
        y=9+.13*d['training_hours']+.31*d['practice_score']+.23*d['prior_score']+.38*d['attendance_pct']-5.2*d['difficulty_index']+r.normal(0,7,n)
    elif project==25:
        d.update(exposed_workers=integers(15,750),hazard_index=a(.2,2.5),historic_near_misses=integers(0,70),training_coverage_pct=a(30,100),machine_age_years=a(0,35),shift_hours=a(6,12),process=cat(['machining','forging','assembly','logistics']))
        y=9000+270*d['exposed_workers']*d['hazard_index']+950*d['historic_near_misses']+690*d['machine_age_years']+2100*(100-d['training_coverage_pct'])+r.normal(0,13500,n)
    elif project==26:
        d.update(replacement_value_brl=a(180000,7000000),equipment_age_years=a(0,22),annual_use_hours=a(100,7600),maintenance_score=a(15,100),deductible_pct=a(1,15),security_score=a(20,100),equipment_type=cat(['forklift','press','cnc','fleet']))
        y=(.013+.001*d['equipment_age_years']+.000002*d['annual_use_hours']+.0007*(100-d['maintenance_score'])-.0007*d['deductible_pct'])*d['replacement_value_brl']+r.normal(0,17500,n)
    elif project==27:
        # Features are constructed strictly from past generated sales (shifted at least one day).
        dates=pd.date_range('2024-01-01',periods=n+7,freq='D')
        past=[120.,127.,119.,135.,140.,131.,124.]
        for i in range(n):
            m=(dates[i+7].month-1)*2*np.pi/12
            planned_price=1+.07*np.sin(i/42)
            capacity=220+20*np.sin(i/17)
            val=.62*past[-1]+.20*past[-7]+.14*capacity+22*np.sin(m)-25*(planned_price-1)+r.normal(0,12)
            past.append(float(max(2,val)))
        t=np.arange(n)
        ds=dates[7:]
        d.update(lag1_sales=np.array(past[6:-1]),lag7_sales=np.array(past[:-7]),past7_mean=np.array([np.mean(past[i:i+7]) for i in range(n)]),announced_price_index=1+.07*np.sin(t/42),capacity_units=220+20*np.sin(t/17),month_sin=np.sin(2*np.pi*(ds.month-1)/12),month_cos=np.cos(2*np.pi*(ds.month-1)/12))
        y=np.array(past[7:]);d['observation_date']=ds.strftime('%Y-%m-%d').to_numpy()
    elif project==28:
        d.update(cpu_cores=cat([4,8,12,16,24,32]),ram_gb=cat([8,16,32,64,128]),ssd_tb=cat([.5,1,2,4]),gpu_tflops=a(0,45),ruggedness_rating=integers(1,5),warranty_years=integers(1,6),device_quantity=integers(1,25),deployment_class=cat(['office','factory','outdoor']))
        item=1200+260*d['cpu_cores']+53*d['ram_gb']+900*d['ssd_tb']+115*d['gpu_tflops']+1500*d['ruggedness_rating']+430*d['warranty_years']
        y=np.array(item)*d['device_quantity']*(1-.003*np.minimum(d['device_quantity'],20))+r.normal(0,3400,n)
    elif project==29:
        d.update(planned_furnace_hours=a(0,20),planned_machine_hours=a(0,22),planned_tonnage=a(0,80),ambient_temp_c=a(10,38),furnace_load_pct=a(30,100),tariff_period_index=a(.85,1.3),process=cat(['heavy_forging','light_forging','machining']))
        y=650+580*d['planned_furnace_hours']*(d['furnace_load_pct']/100)+95*d['planned_machine_hours']+25*d['planned_tonnage']+3.8*d['ambient_temp_c']+r.normal(0,410,n)
    elif project==30:
        d.update(route_distance_km=a(20,1600),forecast_traffic_index=a(.7,2.4),stops_planned=integers(0,12),cargo_weight_tons=a(1,35),forecast_rain_mm=a(0,55),dispatch_hour=integers(0,23),border_crossings=integers(0,2),transport_mode=cat(['truck','rail','van']))
        speeds=pd.Series(d['transport_mode']).map({'truck':65,'rail':74,'van':76}).to_numpy()
        y=d['route_distance_km']/speeds*d['forecast_traffic_index']+.6*d['stops_planned']+.012*d['cargo_weight_tons']+.02*d['forecast_rain_mm']+2.8*d['border_crossings']+r.normal(0,1.1,n)+1.5
    else: raise AssertionError('Unreachable project')
    y=np.maximum(y,1.)
    if project==24: y=np.clip(y,0,100)
    out=pd.DataFrame(d);out.insert(0,'sample_id',[f'P{project:03d}-{j:05d}' for j in range(n)])
    if CONFIG[project]['temporal'] and 'observation_date' not in out:
        out.insert(1,'observation_date',pd.date_range('2024-01-01',periods=n).strftime('%Y-%m-%d'))
    out[ 'target_value']=np.asarray(y).round(3)
    return out

def validate_data(project:int, frame:pd.DataFrame) -> None:
    conf=CONFIG[project];required=['sample_id','target_value']+conf['numerics']+conf['categories']
    if conf['temporal']:required+=['observation_date']
    missing=set(required)-set(frame.columns)
    if missing:raise ValueError('Missing required columns: '+', '.join(sorted(missing)))
    if len(frame)<120:raise ValueError('Insufficient records')
    if frame.sample_id.isna().any() or frame.sample_id.duplicated().any():raise ValueError('Duplicate/missing IDs')
    if frame[required].isna().any().any():raise ValueError('Missing values')
    for f in conf['numerics']+['target_value']:
        if not np.isfinite(pd.to_numeric(frame[f],errors='coerce')).all():raise ValueError('Non-finite numeric field: '+f)
    if (frame.target_value<0).any():raise ValueError('Negative target')
    if conf['temporal']:
        if pd.to_datetime(frame.observation_date,errors='coerce').isna().any():raise ValueError('Invalid date')
        if frame.observation_date.duplicated().any():raise ValueError('Duplicate observation date')

def partitions(project:int,frame:pd.DataFrame,seed:int=2026):
    conf=CONFIG[project]
    if conf['temporal']:
        data=frame.sort_values('observation_date').reset_index(drop=True)
    else:
        # Random split of unique synthetic records. No repeated entities in these fixtures.
        data=frame.sample(frac=1,random_state=seed).reset_index(drop=True)
    n=len(data);a=int(.60*n);b=int(.80*n)
    train,cal,test=data.iloc[:a].copy(),data.iloc[a:b].copy(),data.iloc[b:].copy()
    if conf['temporal']:
        assert max(train.observation_date)<min(cal.observation_date)
        assert max(cal.observation_date)<min(test.observation_date)
    assert not (set(train.sample_id)&set(test.sample_id))
    assert not (set(train.sample_id)&set(cal.sample_id))
    return train,cal,test

def evaluate(project:int,frame:pd.DataFrame|None=None,save:bool=False) -> dict:
    from matplotlib import pyplot as plt
    if project not in CONFIG:raise ValueError('Unknown project')
    conf=CONFIG[project]
    if frame is None:
        f=ROOT/'data'/f'{project:03d}.csv'
        frame=pd.read_csv(f) if f.exists() else synthetic_data(project)
    validate_data(project,frame)
    train,cal,test=partitions(project,frame)
    fs=conf['numerics']+conf['categories'];Xtr=train[fs];ytr=train.target_value
    Xcal=cal[fs]; ycal=cal.target_value; Xte=test[fs]; yte=test.target_value
    def processor():
        return ColumnTransformer([('number',StandardScaler(),conf['numerics']),('category',OneHotEncoder(handle_unknown='ignore'),conf['categories'])] if conf['categories'] else [('number',StandardScaler(),conf['numerics'])],remainder='drop')
    baseline=DummyRegressor(strategy='median').fit(Xtr,ytr)
    ridge=Pipeline([('features',processor()),('model',Ridge(alpha=7.0))]).fit(Xtr,ytr)
    xgb=Pipeline([('features',processor()),('model',XGBRegressor(n_estimators=110,max_depth=3,learning_rate=.06,subsample=.9,colsample_bytree=.9,objective='reg:squarederror',random_state=2026,n_jobs=1))]).fit(Xtr,ytr)
    pred=np.asarray(xgb.predict(Xte),dtype=float)
    cal_pred=np.asarray(xgb.predict(Xcal),dtype=float)
    if not np.isfinite(pred).all():raise AssertionError('Non-finite predictions')
    # Finite-sample split-conformal absolute-residual interval; assess on untouched test set.
    residual=np.abs(ycal.to_numpy()-cal_pred)
    q=min(1.0,np.ceil((len(residual)+1)*.90)/len(residual))
    interval=float(np.quantile(residual,q,method='higher'))
    lower=pred-interval; upper=pred+interval
    mae=lambda y,p:float(mean_absolute_error(y,p))
    metrics={
      'project_id':project,'project':conf['title'],
      'status':'real estimators on generated SYNTHETIC fixture, NOT industrial performance',
      'source':'regression_batch/data/%03d.csv (deterministically generated, synthetic)'%project,
      'features':fs,'models':['DummyRegressor','Ridge','XGBRegressor'],
      'split':'forward chronological 60/20/20' if conf['temporal'] else 'unique-record seeded random 60/20/20',
      'train_rows':len(train),'calibration_rows':len(cal),'test_rows':len(test),
      'baseline_mae':round(mae(yte,baseline.predict(Xte)),4),
      'ridge_mae':round(mae(yte,ridge.predict(Xte)),4),
      'xgboost_mae':round(mae(yte,pred),4),
      'xgboost_rmse':round(float(np.sqrt(mean_squared_error(yte,pred))),4),
      'xgboost_r2':round(float(r2_score(yte,pred)),4),
      'xgboost_wape_pct':round(float(100*np.abs(yte.to_numpy()-pred).sum()/max(1.,np.abs(yte.to_numpy()).sum())),3),
      'interval_nominal_coverage':0.9,
      'interval_empirical_coverage':round(float(np.mean((yte.to_numpy()>=lower)&(yte.to_numpy()<=upper))),4),
      'interval_width':round(2*interval,3),
      'unit':conf['unit'],
      'temporal_holdout_start':str(test.observation_date.iloc[0]) if conf['temporal'] else None,
      'no_real_client_data':True,'no_claim_of_business_impact':True,
      'top_model_features':sorted(zip(xgb.named_steps['features'].get_feature_names_out(),xgb.named_steps['model'].feature_importances_.tolist()),key=lambda x:-x[1])[:5]
    }
    metrics['top_model_features']=[{'feature':str(x),'importance':round(float(v),5)} for x,v in metrics['top_model_features']]
    if save:
        for d in ('reports','figures'): (ROOT/d).mkdir(exist_ok=True)
        (ROOT/'reports'/f'{project:03d}.json').write_text(json.dumps(metrics,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        pd.DataFrame({'sample_id':test.sample_id.to_numpy(),'actual':yte.to_numpy(),'prediction':pred,'interval_lower':lower,'interval_upper':upper}).round(4).to_csv(ROOT/'reports'/f'{project:03d}_predictions.csv',index=False)
        fig,axes=plt.subplots(1,2,figsize=(10.2,4.2))
        axes[0].scatter(yte,pred,s=12,alpha=.6)
        lo=min(yte.min(),pred.min());hi=max(yte.max(),pred.max());axes[0].plot([lo,hi],[lo,hi],ls='--',lw=1)
        axes[0].set(xlabel='Observed synthetic target ('+conf['unit']+')',ylabel='XGBoost predicted',title='Holdout: observed vs predicted')
        axes[1].scatter(pred,yte.to_numpy()-pred,s=12,alpha=.6)
        axes[1].axhline(0,color='black',lw=1);axes[1].set(xlabel='Predicted',ylabel='Residual',title='Holdout residuals')
        fig.suptitle('#%03d — Synthetic regression benchmark'%project)
        fig.tight_layout();fig.savefig(ROOT/'figures'/f'{project:03d}.svg',format='svg',bbox_inches='tight');plt.close(fig)
    return metrics

def run(project:int):
    return evaluate(project,save=False)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('id',type=int);p.add_argument('--save',action='store_true')
    arg=p.parse_args()
    print(json.dumps(evaluate(arg.id,save=arg.save),indent=2,ensure_ascii=False))
