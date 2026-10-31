"""Exploratory pace regression on observed laps; coefficients are estimates."""
import json,numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];p=ROOT/'site/motorsport/data';d=json.loads((p/'bahrain-2024-race.json').read_text());drivers=sorted(x['driver_number'] for x in d['drivers']);rows=[]
for lap in d['laps']:
 n=lap['lap_number'];who=lap['driver_number'];duration=lap.get('lap_duration')
 stint=next((s for s in d['stints'] if s['driver_number']==who and s['lap_start']<=n<=s['lap_end']),None)
 if not stint or stint['compound'] not in ['SOFT','HARD'] or not duration or lap['is_pit_out_lap'] or n==1 or n in [stint['lap_start'],stint['lap_end']] or not 88<duration<104:continue
 age=n-stint['lap_start']+stint.get('tyre_age_at_start',0);hard=int(stint['compound']=='HARD')
 rows.append(([1,hard,age,age*hard,n]+[int(who==v) for v in drivers[1:]],duration,lap))
X=np.array([r[0] for r in rows]);y=np.array([r[1] for r in rows]);b=np.linalg.lstsq(X,y,rcond=None)[0];pred=X@b
out={'origin':'estimated-from-observed','provider':'OpenF1','session_key':9472,'race_laps':57,'observed_laps_used':len(rows),'coefficients':{'intercept':float(b[0]),'hard_offset':float(b[1]),'soft_age':float(b[2]),'hard_age':float(b[2]+b[3]),'lap_trend':float(b[4])},'fit_mae_seconds':float(abs(pred-y).mean()),'filter':'SOFT/HARD, 88 < lap seconds < 104, exclude lap 1, pit-out, stint first and last laps','limitations':['Exploratory fit on this race, not prospective validation.','Age and race-lap effects are associations; lap trend is not a measured fuel effect.','Pit loss is a user-defined counterfactual parameter, not pit-lane duration.','Only S-H and S-H-S plans, no traffic, DNF or safety-car model.','Predicted stint ages can exceed observed support.'],'source':'bahrain-2024-race.json'}
(p/'strategy-real.json').write_text(json.dumps(out,separators=(',',':')));print(out)
