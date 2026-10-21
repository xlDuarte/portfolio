"""Deterministic fictitious datasets for the nine distinct operational analyses."""
from pathlib import Path
import numpy as np
import pandas as pd

DIR=Path(__file__).resolve().parent/'data'

def generate():
    DIR.mkdir(parents=True,exist_ok=True)
    r=np.random.default_rng(20261021)
    datasets={}
    # Operator-level paired pre/post; training exposure correlated with gain, no causal claim.
    n=180;pre=r.integers(35,85,n);hours=r.integers(2,30,n)
    post=np.clip(pre + (.35*hours+r.normal(2,8,n)).round(),0,100)
    qb=np.clip(r.normal(89,4,n),0,100)
    qa=np.clip(qb + r.normal(1.2,2.5,n),0,100)
    datasets[1]=pd.DataFrame({'operator_id':[f'OP-{i:04}' for i in range(n)],'shift':r.choice(['A','B','C'],n),'training_hours':hours,'pre_score':pre,'post_score':post,'quality_before_pct':qb.round(2),'quality_after_pct':qa.round(2)})
    # Aftermarket: independent sales movements with bounded returns and stock accounting.
    n=320;sku=r.choice([f'PART-{i:02}' for i in range(1,13)],n);sold=r.integers(1,40,n);ret=r.binomial(sold,.04);price=r.uniform(40,600,n);cost=price*r.uniform(.5,.85,n)
    datasets[2]=pd.DataFrame({'transaction_id':[f'S-{i:04}' for i in range(n)],'date':pd.date_range('2026-01-01',periods=n).strftime('%Y-%m-%d'),'sku':sku,'channel':r.choice(['dealer','online','retailer'],n),'units_sold':sold,'units_returned':ret,'unit_price_brl':price.round(2),'unit_cost_brl':cost.round(2),'beginning_stock':sold+r.integers(3,80,n),'received_units':r.integers(0,50,n)})
    n=160;types=r.choice(['work_instruction','maintenance_manual','engineering_spec','telemetry_map'],n);req=r.integers(6,18,n);done=np.array([r.integers(max(1,int(v*.6)),v+1) for v in req]);tag=[f'SENSOR-{i:05}' for i in range(n)]
    datasets[3]=pd.DataFrame({'document_id':[f'D-{i:05}' for i in range(n)],'asset_id':[f'A-{i:05}' for i in range(n)],'doc_type':types,'revision':r.integers(1,5,n),'effective_date':'2024-03-01','owner':r.choice(['Reliability','Engineering','Operations'],n),'required_fields':req,'completed_fields':done,'sensor_tag':tag,'sensor_units':r.choice(['C','mm/s','bar','kW'],n),'last_reviewed':(pd.Timestamp('2026-10-01')-pd.to_timedelta(r.integers(0,850,n),unit='D')).strftime('%Y-%m-%d'),'is_active':r.choice([0,1],n,p=[.12,.88])})
    # Vibronic fixture: 100 Hz firing fundamental (3000RPM, 4 cyl), 2f and 3f.
    n=2048;fs=2048;t=np.arange(n)/fs
    v=.32*np.sin(2*np.pi*100*t)+.16*np.sin(2*np.pi*200*t)+.08*np.sin(2*np.pi*300*t)+r.normal(0,.025,n)
    datasets[4]=pd.DataFrame({'sample_index':np.arange(n),'sample_rate_hz':fs,'accel_g':np.round(v,7),'rpm':3000,'cylinders':4})
    n=300;ticket=r.binomial(1,.33,n);selfservice=np.where(ticket==1,0,r.binomial(1,.7,n))
    datasets[5]=pd.DataFrame({'event_id':[f'K-{i:04}' for i in range(n)],'date':(pd.Timestamp('2026-01-01')+pd.to_timedelta(np.arange(n)%150,unit='D')).strftime('%Y-%m-%d'),'topic':r.choice(['Safety','PLC','Quality','Data','Maintenance'],n),'operator_id':r.choice([f'OP-{i:03}' for i in range(95)],n),'articles_viewed':r.integers(1,9,n),'feedback_score':r.integers(1,6,n),'ticket_opened':ticket,'resolved_without_ticket':selfservice,'minutes_spent':np.round(r.uniform(1,27,n),2)})
    n=220;start=pd.Timestamp('2026-01-01')+pd.to_timedelta(r.integers(0,190,n),unit='D');approval=start+pd.to_timedelta(r.integers(1,6,n),unit='D');po=approval+pd.to_timedelta(r.integers(1,8,n),unit='D');receipt=po+pd.to_timedelta(r.integers(2,32,n),unit='D');req=r.uniform(600,40000,n);q=req*r.uniform(.8,.99,n);rec=q*r.uniform(.99,1.02,n)
    datasets[6]=pd.DataFrame({'request_id':[f'PR-{i:04}' for i in range(n)],'request_date':start.strftime('%Y-%m-%d'),'approved_date':approval.strftime('%Y-%m-%d'),'po_date':po.strftime('%Y-%m-%d'),'receipt_date':receipt.strftime('%Y-%m-%d'),'department':r.choice(['MRO','Assembly','Machining','Facility'],n),'supplier':r.choice(['SUP-A','SUP-B','SUP-C'],n),'request_value_brl':req.round(2),'quoted_value_brl':q.round(2),'received_value_brl':rec.round(2),'status':'received'})
    n=340;qty=r.integers(1,180,n);price=r.uniform(50,1400,n)
    datasets[7]=pd.DataFrame({'po_id':[f'PO-{i:05}' for i in range(n)],'date':(pd.Timestamp('2026-01-01')+pd.to_timedelta(r.integers(0,180,n),unit='D')).strftime('%Y-%m-%d'),'customer':r.choice([f'OEM-{i:02}' for i in range(12)],n),'tier':r.choice(['OEM','Tier-1','Tier-2'],n),'supplier':r.choice(['SUP-A','SUP-B','SUP-C','SUP-D'],n),'part_family':r.choice(['Casting','Fasteners','Tools','Sensors'],n),'quantity':qty,'unit_price_brl':price.round(2),'unit_cost_brl':(price*r.uniform(.65,.95,n)).round(2)})
    n=270;units=r.integers(100,450,n);kwh=units*r.uniform(1.5,3.8,n);shift=r.choice(['A','B','C'],n)
    datasets[8]=pd.DataFrame({'reading_id':[f'MTR-{i:05}' for i in range(n)],'day':(pd.Timestamp('2026-02-01')+pd.to_timedelta(np.arange(n)//3,unit='D')).strftime('%Y-%m-%d'),'shift':shift,'line':r.choice(['CNC','Forging','Assembly'],n),'kwh':kwh.round(2),'produced_units':units,'planned_hours':8,'run_hours':r.uniform(5.2,7.9,n).round(2),'tariff_brl_kwh':np.where(shift=='C',.95,.75)})
    n=65;capex=r.uniform(8e4,2.5e6,n);age=r.integers(1,10,n);life=r.integers(8,20,n);sal=r.uniform(.05,.2,n);annual=capex*r.uniform(.04,.18,n)
    datasets[9]=pd.DataFrame({'asset_id':[f'AST-{i:04}' for i in range(n)],'acquisition_cost_brl':capex.round(2),'age_years':age,'useful_life_years':life,'salvage_fraction':sal.round(4),'annual_net_cashflow_brl':annual.round(2),'discount_rate':r.uniform(.07,.15,n).round(4),'remaining_horizon_years':np.maximum(life-age,1)})
    for k,d in datasets.items(): d.to_csv(DIR/f'{k:03}.csv',index=False)
    return {k:len(d) for k,d in datasets.items()}

if __name__=='__main__':print(generate())
