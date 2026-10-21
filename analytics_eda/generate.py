"""Fixed-seed SYNTHETIC data generators. These do not pull real corporate/market data."""
from pathlib import Path
import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent / 'data'
DATA.mkdir(parents=True, exist_ok=True)

def build(project: int) -> pd.DataFrame:
    rng = np.random.default_rng(52000 + project)
    if project == 11:
        rows = []
        for region, total in [('LATAM', 11_000_000), ('Europe', 27_000_000), ('Asia', 59_000_000), ('North America', 33_000_000)]:
            for year in range(2018, 2026):
                fleet = round(total * (1.016 ** (year - 2018)) * rng.uniform(.995, 1.005))
                share = min(.68, rng.uniform(.008,.022) * (1.36 ** (year - 2018)))
                rows.append(dict(region=region, year=year, fleet_units=fleet, ev_units=int(fleet * share), population=int(fleet*rng.uniform(2.0,3.8)), urbanization_pct=round(rng.uniform(58,91),2)))
        return pd.DataFrame(rows)
    if project == 12:
        n=240; sites=rng.choice(['Forge','Machining','Assembly','Warehouse'],n)
        risk=np.clip(rng.normal(44,16,n),0,100); hours=rng.integers(1300,2100,n)
        incidents=rng.poisson(.09+risk/380); near=rng.poisson(.2+risk/90)
        return pd.DataFrame(dict(record_id=[f'SAF{i:04d}' for i in range(n)], site=sites, department=rng.choice(['Production','Logistics','Quality'],n), employee_hours=hours, ergonomic_risk_score=risk.round(2), safety_training_hours=rng.integers(0,35,n), reportable_incidents=incidents, near_misses=near))
    if project == 13:
        n=144; cap=rng.choice([1600,2500,4200],n); occ=(cap*rng.uniform(.42,1.0,n)).astype(int)
        return pd.DataFrame(dict(snapshot_id=[f'WH{i:04d}' for i in range(n)], hub=rng.choice(['Hub-SP','Hub-RJ','Hub-MG'],n), date=pd.date_range('2026-03-01',periods=n,freq='D').astype(str), capacity_pallets=cap, occupied_pallets=occ, inbound_pallets=rng.integers(20,150,n), outbound_pallets=rng.integers(20,150,n), dock_hours_used=rng.uniform(2,23,n).round(2), dock_hours_available=np.full(n,24)))
    if project == 14:
        n=180; car=rng.choice(['P01','P02','P03','P04','P05','P06'],n); tire=rng.choice(['Soft','Medium','Hard'],n)
        s1=rng.normal(28.1,0.55,n);s2=rng.normal(34.7,0.8,n);s3=rng.normal(22.3,0.6,n)
        s1 += (tire=='Hard')*.25;s2+=(tire=='Soft')*(-.2)
        return pd.DataFrame(dict(lap_id=[f'LAP{i:04d}' for i in range(n)], car=car, session=rng.choice(['FP1','FP2','Qualifying'],n), compound=tire, lap_number=rng.integers(1,60,n), track_temp_c=rng.uniform(22,48,n).round(2), sector_1_s=s1.round(3),sector_2_s=s2.round(3),sector_3_s=s3.round(3)))
    if project == 15:
        n=180; units=rng.integers(60,280,n); rate=rng.uniform(.005,.07,n); defects=rng.binomial(units,rate)
        return pd.DataFrame(dict(batch_id=[f'LOT{i:04d}' for i in range(n)], supplier=rng.choice(['Supplier-A','Supplier-B','Supplier-C','Supplier-D'],n), part_family=rng.choice(['Steel','Electronics','Machined'],n), inspected_units=units, defect_units=defects, rating_1to5=np.clip(rng.normal(4.1,.55,n),1,5).round(2), audit_date=rng.choice(pd.date_range('2026-01-01',periods=90).astype(str),n)))
    if project == 16:
        n=120; kind=rng.choice(['Die','Tool','Wheel'],n); phase=np.tile(['Before','After'],n//2)
        event=rng.uniform(17,55,n)*(np.where(phase=='After',rng.uniform(.65,.88,n),1))
        return pd.DataFrame(dict(changeover_id=[f'SMED{i:04d}' for i in range(n)], asset=rng.choice(['Line-A','Line-B','Line-C'],n), operation=kind, phase=phase, internal_setup_min=(event*.68).round(2), external_setup_min=(event*.32).round(2), production_run_hours=rng.uniform(3,10,n).round(2), operator_count=rng.integers(2,7,n)))
    if project == 17:
        skills=['Python','SQL','Power BI','SAP','AWS','Excel','Spark','Docker','Lean','Pandas','Statistics','PLC']
        n=170; rows=[]
        for i in range(n):
            s=sorted(rng.choice(skills,size=int(rng.integers(2,6)),replace=False).tolist())
            rows.append(dict(job_id=f'JOB{i:04d}', region=rng.choice(['Vale do Paraiba','Sao Paulo','Campinas']), role=rng.choice(['Data Analyst','Engineer','BI Analyst','Data Engineer','Operations Analyst']), seniority=rng.choice(['Junior','Mid','Senior']), salary_monthly_brl=int(rng.integers(3500,18000)), skills='|'.join(s), posted_date=str(pd.Timestamp('2026-01-01')+pd.Timedelta(days=int(rng.integers(0,90))))[:10]))
        return pd.DataFrame(rows)
    if project == 18:
        rows=[]
        for symbol in ['AUTO_SYN','STEEL_SYN','SUPPLY_SYN']:
            dates=pd.bdate_range('2025-01-01',periods=252); prices=85*np.exp(np.cumsum(rng.normal(.0001,.018,len(dates))))
            for i,(date,price) in enumerate(zip(dates,prices)):
                rows.append(dict(ticker=symbol,date=str(date.date()),close_brl=round(float(price),4),volume_shares=int(rng.integers(100_000,4_000_000))))
        return pd.DataFrame(rows)
    if project == 19:
        n=190; created=pd.Timestamp('2026-02-01')+pd.to_timedelta(rng.integers(0,40*24,n),unit='h');dispatch=created+pd.to_timedelta(rng.integers(1,16,n),unit='h');delivered=dispatch+pd.to_timedelta(rng.integers(8,90,n),unit='h');promised=created+pd.to_timedelta(rng.integers(42,100,n),unit='h')
        return pd.DataFrame(dict(order_id=[f'PO{i:04d}' for i in range(n)], origin=rng.choice(['Plant-A','Plant-B'],n), route=rng.choice(['SP-RJ','SP-MG','SP-PR'],n), mode=rng.choice(['Road','Air'],n), order_created_utc=created.astype(str), dispatched_utc=dispatch.astype(str), delivered_utc=delivered.astype(str), promised_utc=promised.astype(str), quantity=rng.integers(1,80,n)))
    if project == 20:
        n=200; causes=rng.choice(['Weather','Customs','Carrier','Capacity','Documentation'],n,p=[.16,.21,.35,.2,.08]); delay=np.where(causes=='Carrier',rng.integers(20,240,n),rng.integers(5,180,n));late=rng.choice([0,1],n,p=[.24,.76]); delay=delay*late
        return pd.DataFrame(dict(shipment_id=[f'FR{i:04d}' for i in range(n)], carrier=rng.choice(['Carrier-A','Carrier-B','Carrier-C'],n), route=rng.choice(['SP-MIA','SP-FRA','SP-SCL'],n), freight_mode=rng.choice(['Air','Road'],n), cause=causes, delay_minutes=delay, expedited_cost_brl=np.where(late,rng.uniform(500,23000,n),0).round(2), criticality=rng.choice(['High','Medium','Low'],n)))
    raise ValueError('Unsupported EDA project 011–020')

def generate_all() -> None:
    for project in range(11,21):
        p=DATA/f'{project:03d}.csv'
        build(project).to_csv(p,index=False)
        print(project, len(pd.read_csv(p)), p)

if __name__=='__main__': generate_all()
