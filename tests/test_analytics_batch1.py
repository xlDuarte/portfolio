"""Rigorous data and domain regression checks for nine distinct industrial studies."""
from pathlib import Path
import json
import subprocess
import sys
import unittest
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from analytics_batch1.engine import run,FUNCS,_read

class TestBatch1Studies(unittest.TestCase):
    def test_independent_specialized_methods_all_nine(self):
        self.assertEqual(len(FUNCS),9)
        self.assertEqual(len(set(FUNCS.values())),9)
        for idx in range(1,10):
            with self.subTest(id=idx):
                result=run(idx)
                self.assertEqual(result['project'],idx)
                self.assertIn('synthetic',result['dataset'])
                self.assertTrue(result['interpretation'])
                p=next((ROOT/'projetos/01-dados').glob(f'{idx:03d}-*/main.py'))
                self.assertNotIn('IndustrialProjectPipeline',p.read_text(encoding='utf8'))

    def test_operator_training_paired_bootstrap(self):
        r=run(1)
        self.assertGreater(r['paired_gain_pp'],0)
        self.assertLessEqual(r['bootstrap_95pct_ci_pp'][0],r['paired_gain_pp'])
        self.assertGreaterEqual(r['bootstrap_95pct_ci_pp'][1],r['paired_gain_pp'])
        self.assertEqual(sum(x['operators'] for x in r['per_shift']),r['operators'])

    def test_aftermarket_accounting_and_returns(self):
        d=_read(2);r=run(2)
        revenue=((d.units_sold-d.units_returned)*d.unit_price_brl).sum()
        self.assertAlmostEqual(revenue,r['net_revenue_brl'],places=2)
        self.assertEqual(r['returned_units'],int(d.units_returned.sum()))
        self.assertEqual(len(r['sku_abc']),d.sku.nunique())
        d.loc[0,'units_returned']=d.loc[0,'units_sold']+1
        with self.assertRaises(ValueError):FUNCS[2](d)

    def test_catalog_integrity(self):
        r=run(3);self.assertGreater(r['metadata_completeness_pct'],0)
        d=_read(3);d.loc[1,'document_id']=d.loc[0,'document_id']
        with self.assertRaisesRegex(ValueError,'Duplicate'):FUNCS[3](d)
        d=_read(3);d.loc[0,'completed_fields']=d.loc[0,'required_fields']+1
        with self.assertRaises(ValueError):FUNCS[3](d)

    def test_nvh_fft_peak_and_nyquist_guard(self):
        r=run(4);self.assertAlmostEqual(r['firing_hz'],100.0)
        self.assertAlmostEqual(r['dominant_peak_hz'],100.0,delta=1)
        self.assertAlmostEqual(r['harmonics'][1]['expected_hz'],200.0)
        d=_read(4);d['sample_rate_hz']=100
        with self.assertRaisesRegex(ValueError,'Nyquist'):FUNCS[4](d)
        d=_read(4);d.drop(index=10,inplace=True)
        with self.assertRaises(ValueError):FUNCS[4](d)

    def test_knowledgebase_sessions(self):
        r=run(5);d=_read(5)
        self.assertEqual(sum(t['sessions'] for t in r['by_topic']),len(d))
        d.loc[0,'ticket_opened']=1;d.loc[0,'resolved_without_ticket']=1
        with self.assertRaises(ValueError):FUNCS[5](d)

    def test_procurement_cycle_time(self):
        r=run(6);d=_read(6)
        self.assertAlmostEqual(r['average_cycle_days'],(pd.to_datetime(d.receipt_date)-pd.to_datetime(d.request_date)).dt.days.mean(),places=2)
        d.loc[0,'receipt_date']='2025-01-01'
        with self.assertRaises(ValueError):FUNCS[6](d)

    def test_oem_supplier_hhi(self):
        r=run(7)
        self.assertGreater(r['supplier_hhi'],0)
        self.assertLessEqual(r['supplier_hhi'],1)
        self.assertAlmostEqual(sum(r['by_tier'].values()),r['total_spend_brl'],places=1)

    def test_shift_energy_weighted_intensity(self):
        r=run(8);d=_read(8)
        self.assertAlmostEqual(r['weighted_kwh_per_unit'],d.kwh.sum()/d.produced_units.sum(),places=4)
        self.assertAlmostEqual(sum(g['kwh'] for g in r['by_shift']),r['total_kwh'],places=1)
        d.loc[0,'run_hours']=11
        with self.assertRaises(ValueError):FUNCS[8](d)

    def test_asset_value_finance_limits(self):
        r=run(9);d=_read(9)
        self.assertGreater(r['depreciated_book_value_brl'],0)
        self.assertLessEqual(r['depreciated_book_value_brl'],r['gross_book_cost_brl'])
        d.loc[0,'salvage_fraction']=1.5
        with self.assertRaises(ValueError):FUNCS[9](d)

    def test_input_schema_and_null_guards_all(self):
        for idx in range(1,10):
            d=_read(idx)
            with self.subTest(project=idx,missing='column'),self.assertRaises(ValueError):FUNCS[idx](d.drop(columns=d.columns[0]))
            d.loc[0,d.columns[-1]]=np.nan
            with self.subTest(project=idx,missing='value'),self.assertRaises(ValueError):FUNCS[idx](d)

    def test_pages_graphs_docs_source_and_notebooks(self):
        for idx in range(1,10):
            with self.subTest(project=idx):
                page=ROOT/f'site/cases/{idx:03d}/index.html'
                text=page.read_text(encoding='utf8')
                self.assertIn('SINTÉTICOS',text)
                self.assertIn('GitHub',text)
                self.assertTrue((page.parent/'chart.svg').is_file())
                nb=json.loads((ROOT/f'analytics_batch1/notebooks/{idx:03d}.ipynb').read_text())
                self.assertEqual(nb['nbformat'],4)
                self.assertTrue(any(f'run({idx})' in ''.join(c['source']) for c in nb['cells']))
                assert (ROOT/f'analytics_batch1/data/{idx:03d}.csv').is_file()

    def test_default_project_commands(self):
        # Run all nine project command-line entrypoints, not just function imports.
        for idx in range(1,10):
            entry=next((ROOT/'projetos/01-dados').glob(f'{idx:03d}-*/main.py'))
            with self.subTest(project=idx):
                completed=subprocess.run([sys.executable,str(entry)],cwd=ROOT,capture_output=True,text=True,timeout=12)
                self.assertEqual(completed.returncode,0,completed.stderr)
                actual=json.loads(completed.stdout)
                self.assertEqual(actual['project'],idx)

if __name__=='__main__':unittest.main()
