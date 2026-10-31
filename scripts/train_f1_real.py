"""Chronological benchmark using real results via FastF1's Jolpica client."""
import json,time,hashlib
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from fastf1.ergast import Ergast
import fastf1.ergast.interface as ergast_interface
ergast_interface.TIMEOUT=60
from sklearn.linear_model import Ridge,LinearRegression
from sklearn.ensemble import RandomForestRegressor,ExtraTreesRegressor,GradientBoostingRegressor,HistGradientBoostingRegressor
ROOT=Path(__file__).resolve().parents[1];CACHE=ROOT/'.cache/f1-public';CACHE.mkdir(parents=True,exist_ok=True)
def fetch(year):
 p=CACHE/f'full-results-{year}.json'
 if p.exists():return json.loads(p.read_text())
 races={};offset=0;total=1
 while offset<total:
  for attempt in range(4):
   try:r=Ergast(result_type='raw',auto_cast=False,limit=100).get_race_results(season=year,offset=offset);break
   except Exception:
    if attempt==3:raise
    time.sleep(2**attempt)
  total=r.total_results;print('Jolpica/FastF1',year,offset,total,flush=True)
  for race in r:
   key=race['round']
   if key not in races:races[key]={**race,'Results':[]}
   races[key]['Results'].extend(race['Results'])
  offset+=100;time.sleep(.5)
 rows=sorted(races.values(),key=lambda x:int(x['round']))
 assert sum(len(x['Results']) for x in rows)==total
 for race in rows: assert len({x['Driver']['driverId'] for x in race['Results']})==len(race['Results'])
 p.write_text(json.dumps(rows));return rows

def train():
 seasons={y:fetch(y) for y in [2022,2023,2024]};events=[];history={};teamhistory={}
 for year,races in seasons.items():
  for race in races:
   rows=[]
   for r in race['Results']:
    driver=r['Driver']['driverId'];team=r['Constructor']['constructorId'];grid=int(r['grid']) or len(race['Results'])
    avg=lambda a:sum(a[-5:])/len(a[-5:]) if a else 10.5
    x=[grid,avg(history.get(driver,[])),avg(teamhistory.get(team,[]))]
    rows.append({'driver_code':r['Driver'].get('code',driver.upper()),'driver_name':r['Driver']['givenName']+' '+r['Driver']['familyName'],'constructor':r['Constructor']['name'],'driver_id':driver,'team_id':team,'x':x,'position':int(r['position'])})
   events.append({'id':f'{year}-{int(race["round"]):02}', 'year':year,'name':race['raceName'],'date':race['date'],'rows':rows})
   for r in rows:
    history.setdefault(r['driver_id'],[]).append(r['position']);teamhistory.setdefault(r['team_id'],[]).append(r['position'])
 train=[e for e in events if e['year']==2022];valid=[e for e in events if e['year']==2023];target=next(e for e in events if e['id']=='2024-01')
 def arrays(es):return np.array([r['x'] for e in es for r in e['rows']]),np.array([r['position'] for e in es for r in e['rows']])
 X,y=arrays(train)
 factories={'Ridge_Regularized':lambda:Ridge(alpha=10),'LinearRegression':lambda:LinearRegression(),'RandomForest_Ensemble':lambda:RandomForestRegressor(n_estimators=150,max_depth=5,min_samples_leaf=8,random_state=111,n_jobs=1),'ExtraTrees':lambda:ExtraTreesRegressor(n_estimators=150,max_depth=5,min_samples_leaf=8,random_state=111,n_jobs=1),'GradientBoosting_Regressor':lambda:GradientBoostingRegressor(n_estimators=80,max_depth=2,min_samples_leaf=10,random_state=111),'HistGradientBoosting':lambda:HistGradientBoostingRegressor(max_iter=80,max_leaf_nodes=7,l2_regularization=10,random_state=111)}
 models={'Baseline_Grid':None,'Baseline_Form':None,**{k:f().fit(X,y) for k,f in factories.items()}}
 def scores(k,m,rows):
  a=np.array([r['x'] for r in rows]);return a[:,0] if k=='Baseline_Grid' else a[:,1] if k=='Baseline_Form' else m.predict(a)
 results={}
 for k,m in models.items():
  maes=[];losses=[]
  for e in valid:
   sc=scores(k,m,e['rows']);truth=np.array([r['position'] for r in e['rows']]);ranks=np.argsort(np.argsort(sc,kind='stable'),kind='stable')+1
   maes.append(float(np.mean(abs(ranks-truth))));w=np.exp(-(sc-sc.min())/5);p=w/w.sum();losses.append(float(-np.log(p[np.argmin(truth)])))
  results[k]={'status':'EVALUATED','kind':'baseline' if m is None else 'trained','holdout_event_rank_mae':float(np.mean(maes)),'validation_win_logloss_tuned':float(np.mean(losses)),'training_events':len(train),'validation_events':len(valid),'softmax_temperature':5,'temperature_policy':'fixed a priori, NOT tuned or calibrated'}
 selected=min(results,key=lambda k:results[k]['holdout_event_rank_mae']);xf,yf=arrays(train+valid)
 predictions_by_model={}
 for k in models:
  final=factories[k]().fit(xf,yf) if k in factories else None
  sc=scores(k,final,target['rows']);predictions_by_model[k]=[{**{a:r[a] for a in ['driver_code','driver_name','constructor']},'ranking_score':float(v)} for r,v in zip(target['rows'],sc)]
 report={'data_type':'real-historical','event_id':'2024-01 · Bahrain · retrospectiva pré-corrida','selected_model':selected,'predictions':predictions_by_model[selected],'predictions_by_model':predictions_by_model,'model_results':results,'created_at':datetime.now(timezone.utc).isoformat(),'sources':[{'provider':'FastF1 3.9.0 / Jolpica','season':year,'url':f'https://api.jolpi.ca/ergast/f1/{year}/results/','sha256':hashlib.sha256((CACHE/f'full-results-{year}.json').read_bytes()).hexdigest()} for year in seasons],'features':['grid position','mean last five prior driver results','mean last five prior constructor results'],'evaluation':{'train':'2022','validation':'2023','final_fit':'2022+2023','target':'2024 Bahrain, before race','temperature':5,'selection':'lowest validation rank MAE; validation not independent of model selection'},'limitations':['Retrospective pre-race scenario, not a live forecast.','Only grid and previously available race results are features.','Plackett-Luce probabilities are model estimates, not measurements or calibrated probabilities.','No explicit DNF model.','Validation is reused for model selection; no independent performance claim.']}
 (ROOT/'site/motorsport/data/models-real.json').write_text(json.dumps(report,ensure_ascii=False,separators=(',',':'),allow_nan=False))
 (ROOT/'site/motorsport/data/results-real.json').write_text(json.dumps({'provider':'FastF1/Jolpica','events':events},ensure_ascii=False,separators=(',',':')))
 print('TRAINED',selected,len(train),len(valid),len(target['rows']),flush=True)
if __name__=='__main__':train()
