"""Collect public observed F1 data. No synthetic fallback. Run from repo root."""
import json, time, hashlib, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'site/motorsport/data'
CACHE=ROOT/'.cache/f1-public'
CACHE.mkdir(parents=True,exist_ok=True)
OUT.mkdir(parents=True,exist_ok=True)
provenance=[]
def get(endpoint, **params):
    url='https://api.openf1.org/v1/'+endpoint+'?'+urllib.parse.urlencode(params)
    key=hashlib.sha256(url.encode()).hexdigest(); path=CACHE/(key+'.json')
    if path.exists(): raw=path.read_bytes()
    else:
        for attempt in range(4):
            try:
                with urllib.request.urlopen(url,timeout=60) as r: raw=r.read()
                json.loads(raw);path.write_bytes(raw);break
            except Exception:
                if attempt==3: raise
                time.sleep(2**attempt)
        time.sleep(.4)
    provenance.append({'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
    return json.loads(raw)
def write(name,data):
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'),allow_nan=False))
def collect():
    sessions=get('sessions',year=2024,country_name='Bahrain',session_name='Race')
    assert len(sessions)==1
    s=sessions[0];key=s['session_key'];print('Session',key,flush=True)
    data={'schema_version':1,'origin':'observed','provider':'OpenF1','session':s}
    for e in ['drivers','laps','stints','weather','position','pit','race_control']:
        data[e]=get(e,session_key=key);print(e,len(data[e]),flush=True)
    # Bounded replay excerpt, all channels use the same absolute UTC time window.
    start='2024-03-02T15:05:30+00:00';end='2024-03-02T15:09:30+00:00'
    data['replay_window']={'start':start,'end':end,'drivers':[1,11,55]}
    data['telemetry']={};data['location']={}
    for driver in data['replay_window']['drivers']:
        for endpoint,target in [('car_data','telemetry'),('location','location')]:
            rows=get(endpoint,session_key=key,driver_number=driver,**{'date>':start,'date<':end})
            assert len(rows)>100,(endpoint,driver,len(rows))
            data[target][str(driver)]=rows;print(endpoint,driver,len(rows),flush=True)
    assert len(data['drivers'])==20 and len(data['laps'])>1000
    data['collected_at']=datetime.now(timezone.utc).isoformat()
    data['sources']=provenance
    data['limitations']=['Replay is a 4-minute excerpt of 3 drivers, not the entire field.',
      'Location is approximate; interpolation is a display operation, not new measured samples.',
      'No tyre temperature, wheel loads, suspension travel, sideslip ground truth or vibration sensors are available.',
      'Observed race data must not be used as pre-race prediction features for the same race.']
    write('bahrain-2024-race.json',data)
    print('Saved',OUT/'bahrain-2024-race.json',flush=True)
if __name__=='__main__':collect()
