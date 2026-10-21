"""Reproducible, explicitly synthetic demonstration datasets. Never production observations."""
from __future__ import annotations
import csv
import math
import random
from datetime import date, timedelta
from pathlib import Path
DATA=Path(__file__).parent/'data'

def save(name, rows):
    DATA.mkdir(parents=True,exist_ok=True)
    with (DATA/name).open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def generate():
    rng=random.Random(20261021)
    oee=[]
    for i in range(240):
        planned=480
        dow=i%7; line='LINE-A' if i%2==0 else 'LINE-B'
        downtime=round(max(5, rng.gauss(47 if dow<5 else 62,15)),1)
        runtime=planned-downtime
        ideal_cycle=0.7
        count=int(runtime/ideal_cycle*rng.uniform(.83,.97))
        good=max(0,count-int(count*rng.uniform(.014,.065)))
        oee.append({'date':(date(2025,1,1)+timedelta(days=i)).isoformat(),'line':line,'planned_min':planned,'downtime_min':downtime,'ideal_cycle_min':ideal_cycle,'total_units':count,'good_units':good})
    save('oee_shifts.csv',oee)
    orders=[]
    for i in range(420):
        promised=date(2025,1,1)+timedelta(days=i//2)
        carrier=['A','B','C'][i%3]; material=['STEEL','ALUMINUM','COMPONENT'][(i//3)%3]
        eta=7 + {'A':-1,'B':1,'C':0}[carrier]+(2 if material=='STEEL' else 0)+rng.gauss(0,2)
        delivered=promised+timedelta(days=round(eta-7))
        qty=rng.randint(20,500); full=qty if rng.random()<.83 else max(0,qty-rng.randint(1,20))
        orders.append({'order_id':f'ORD-{i:05d}','promised_date':promised.isoformat(),'delivered_date':delivered.isoformat(),'carrier':carrier,'material':material,'ordered_qty':qty,'delivered_qty':full,'unit_value_brl':rng.randint(150,1500)})
    save('supply_orders.csv',orders)
    capex=[]
    for i in range(360):
        area=rng.randint(80,1600); robots=rng.randint(1,22); utilities=rng.randint(0,9)
        cost=115000+980*area+18000*robots+40000*utilities+rng.gauss(0,85000)
        capex.append({'project_id':f'CAP-{i:04d}','area_m2':area,'robots':robots,'utilities_complexity':utilities,'actual_capex_brl':round(max(cost,100000),2)})
    save('capex_projects.csv',capex)
    churn=[]
    for i in range(480):
        duration=rng.randint(1,60); tickets=rng.randint(0,14); delivery=rng.uniform(.55,1); spend=rng.randint(10000,90000)
        z=-.8-.055*duration+.21*tickets-4*(delivery-.8)+.000006*(25000-spend)
        prob=1/(1+math.exp(-z)); y=int(rng.random()<prob)
        churn.append({'account_id':f'ACC-{i:04d}','tenure_months':duration,'support_tickets_90d':tickets,'otd_rate':round(delivery,4),'monthly_spend_brl':spend,'churned_90d':y})
    save('b2b_churn.csv',churn)
    ts=[]
    for i in range(260):
        demand=round(max(3,120+0.11*i+18*math.sin(2*math.pi*i/7)+8*math.cos(2*math.pi*i/30)+rng.gauss(0,7)),2)
        ts.append({'date':(date(2025,1,1)+timedelta(days=i)).isoformat(),'material':'ALLOY-001','demand_units':demand})
    save('demand_daily.csv',ts)
    return ['oee_shifts.csv','supply_orders.csv','capex_projects.csv','b2b_churn.csv','demand_daily.csv']
if __name__=='__main__':print('\n'.join(generate()))
