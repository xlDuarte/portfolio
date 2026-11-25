"""Regression and domain validity checks for the 10 verified synthetic EDA projects."""
import csv
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from analytics_eda.engine import NAMES, read_case, run, save_report, analyze
from analytics_eda.generate import build

class TestEDA(unittest.TestCase):
    def test_inventory_and_unique_titles(self):
        self.assertEqual(set(NAMES),set(range(11,21)))
        self.assertEqual(len(set(NAMES.values())),10)
        for i in range(11,21):
            self.assertEqual(len(read_case(i)),len(build(i)))
            self.assertTrue((ROOT/f'analytics_eda/notebooks/{i:03d}.ipynb').exists())
            self.assertTrue((ROOT/f'site/cases/{i:03d}/index.html').exists())
            for name in ('metrics.json','chart.svg','interactive.html'):
                self.assertTrue((ROOT/f'site/cases/{i:03d}/{name}').exists())

    def test_distinct_domain_metrics(self):
        keys=[]
        for i in range(11,21):
            r=run(i)
            self.assertEqual(r['project'],i)
            self.assertEqual(r['data_provenance'],'FIXED-SEED SYNTHETIC — NOT REAL BUSINESS DATA')
            self.assertGreater(r['records'],0)
            keys.append(set(r)-{'project','data_provenance','records','name','interpretation'})
        for j in range(len(keys)):
            for k in range(j+1,len(keys)):
                self.assertNotEqual(keys[j],keys[k],f'Identical analytics KPIs for projects {j+11} and {k+11}')

    def test_domain_invariants(self):
        a={i:run(i) for i in range(11,21)}
        self.assertTrue(0<=a[11]['latest_ev_share_pct']<=100)
        self.assertGreaterEqual(a[12]['incident_rate_per_200k_hours'],0)
        self.assertLessEqual(a[13]['mean_occupancy_pct'],100)
        self.assertLess(a[14]['best_lap_s'],a[14]['median_lap_s'])
        self.assertLessEqual(a[15]['weighted_defect_rate_pct'],100)
        self.assertLess(a[16]['median_after_min'],a[16]['median_before_min'])
        self.assertGreater(a[17]['salary_median_brl'],0)
        self.assertEqual(a[18]['instruments'],3)
        self.assertTrue(0<=a[19]['on_time_pct']<=100)
        self.assertAlmostEqual(a[20]['cause_pareto'][-1]['cumulative_delay_share_pct'],100,places=1)

    def test_calculated_weighted_ratios(self):
        f=read_case(11); latest=f[f.year==f.year.max()]
        self.assertAlmostEqual(run(11)['latest_ev_share_pct'],100*latest.ev_units.sum()/latest.fleet_units.sum(),places=3)
        q=read_case(15)
        self.assertAlmostEqual(run(15)['weighted_defect_rate_pct'],100*q.defect_units.sum()/q.inspected_units.sum(),places=3)
        o=read_case(12)
        self.assertAlmostEqual(run(12)['incident_rate_per_200k_hours'],200000*o.reportable_incidents.sum()/o.employee_hours.sum(),places=2)

    def test_missing_null_duplicate_and_negative_rejected(self):
        for i in range(11,21):
            with self.subTest(project=i):
                d=read_case(i); cols=list(d.columns)
                with tempfile.TemporaryDirectory() as td:
                    p=Path(td)/'invalid.csv'
                    d.drop(columns=cols[0]).to_csv(p,index=False)
                    with self.assertRaisesRegex(ValueError,'Missing columns'):read_case(i,p)
                    d.iloc[:0].to_csv(p,index=False)
                    with self.assertRaisesRegex(ValueError,'Empty dataset'):read_case(i,p)
                    pd.concat([d,d.iloc[[0]]]).to_csv(p,index=False)
                    with self.assertRaisesRegex(ValueError,'Duplicate business key'):read_case(i,p)
                    d1=d.copy();d1.iloc[0,d1.columns.get_loc(cols[-1])]=None
                    d1.to_csv(p,index=False)
                    with self.assertRaisesRegex(ValueError,'Nulls'):read_case(i,p)

    def test_business_rules_reject_impossible_inputs(self):
        edits={
         11:('ev_units',10**15),12:('ergonomic_risk_score',105),13:('occupied_pallets',999999),
         14:('sector_1_s',0),15:('defect_units',999999),16:('phase','Impossible'),
         17:('salary_monthly_brl',0),18:('close_brl',0),19:('dispatched_utc','2020-01-01'),20:('delay_minutes',-2)
        }
        for i,(col,value) in edits.items():
            with self.subTest(project=i):
                d=read_case(i);d.at[0,col]=value
                with tempfile.TemporaryDirectory() as td:
                    p=Path(td)/'bad.csv';d.to_csv(p,index=False)
                    with self.assertRaises(ValueError):run(i,p)

    def test_reports_execute_and_write_nonempty_plots(self):
        for i in range(11,21):
            with self.subTest(project=i):
                with tempfile.TemporaryDirectory() as td:
                    m=save_report(i,td)
                    self.assertEqual(m['project'],i)
                    for f in ('metrics.json','validated_data.csv','chart.svg','interactive.html'):
                        self.assertGreater((Path(td)/f).stat().st_size,300)
                    self.assertIn('plotly', (Path(td)/'interactive.html').read_text().lower())

    def test_script_cli(self):
        for i in range(11,21):
            p=next((ROOT/'projetos/02-eda').glob(f'{i:03d}-*/main.py'))
            with self.subTest(project=i):
                r=subprocess.run([sys.executable,str(p)],cwd=ROOT,capture_output=True,text=True,timeout=15)
                self.assertEqual(r.returncode,0,r.stderr[-500:])
                self.assertEqual(json.loads(r.stdout)['project'],i)

    def test_pages_avoid_fake_production_claims(self):
        catalog=(ROOT/'site/cases/eda/index.html').read_text()
        for i in range(11,21):
            t=(ROOT/f'site/cases/{i:03d}/index.html').read_text()
            if i==14:   # phase 3: real OpenF1 benchmark on top, synthetic EDA kept below and labelled as such
                self.assertIn('Dados reais e sintéticos, separados',t)
                self.assertIn('dados sintéticos de semente fixa',t)
            else:
                self.assertIn('Dados integralmente sintéticos',t)
            self.assertIn('interactive.html',t)
            self.assertIn('chart.svg',t)
            self.assertIn(f'/cases/{i:03d}/',catalog)

if __name__=='__main__': unittest.main()
