"""Regression tests for executable evidence and honest catalog claims."""
from pathlib import Path
import importlib.util
import math
import sys
import unittest
import json
import subprocess

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from case_studies import analytics as a

class TestCaseStudies(unittest.TestCase):
    def test_oee_formula_weighted(self):
        result=a.oee();self.assertEqual(result['records'],240)
        self.assertTrue(0<=result['oee_weighted_pct']<=100)
        self.assertAlmostEqual(result['oee_weighted_pct'],sum(x['oee_weighted']*x['planned_min'] for x in result['lines'])/sum(x['planned_min'] for x in result['lines'])*100,places=2)

    def test_supply_sql_and_otif(self):
        d=a.load('supply_orders.csv');result=a.supply()
        self.assertTrue(d.order_id.is_unique)
        self.assertEqual(sum(row['orders'] for row in result['by_carrier']),len(d))
        self.assertGreater(result['otif_pct'],0)
        self.assertLessEqual(result['otif_pct'],100)

    def test_trained_capex_model_and_holdout(self):
        r=a.capex();self.assertEqual(r['rows_train']+r['rows_test'],360)
        self.assertGreater(r['baseline_mae_brl'],r['mae_brl'])
        self.assertGreater(r['rmse_brl'],0)

    def test_trained_churn_model_probabilities(self):
        r=a.churn();self.assertEqual(r['rows_train']+r['rows_test'],480)
        for k in ('f1','precision','recall','roc_auc','average_precision','brier','baseline_brier'):
            self.assertTrue(0<=r[k]<=1,(k,r[k]))

    def test_temporal_forecast_no_future(self):
        r=a.forecast();self.assertEqual(r['rolling_test_days'],110)
        self.assertGreater(r['baseline_mae_units'],r['mae_units'])
        self.assertGreater(r['wape_pct'],0)

    def test_actual_xgboost_fit_not_stub(self):
        from case_studies.xgboost_capex import evaluate_xgboost_capex
        r=evaluate_xgboost_capex()
        self.assertEqual(r['estimator'],'XGBRegressor')
        self.assertTrue(r['xgboost_trained'])
        self.assertEqual(r['n_train']+r['n_test'],360)
        self.assertGreater(r['test_mae_brl'],0)
        self.assertEqual(len(r['feature_importance']),3)

    def test_invalid_case(self):
        with self.assertRaises(ValueError): a.run('unknown')

    def test_docs_pages_and_charts(self):
        for key in ('oee','supply','capex','churn','forecast'):
            f=ROOT/'site/cases'/key/'index.html';self.assertTrue(f.exists(),key)
            s=f.read_text();self.assertIn('SINTÉTICA',s);self.assertIn(f'{key}.svg',s)
            self.assertTrue((ROOT/'site/cases/assets'/f'{key}.svg').exists())

    def test_legacy_marked_demonstrations(self):
        import re
        for p in ROOT.glob('projetos/**/main.py'):
            n=int(p.parent.name[:3]);
            # Recommendation scripts #051-#060 now have domain acceptance tests.
            if n in (*range(1,31),31,61,86) or 51 <= n <= 60 or n>=101:continue
            txt=(p.parent/'README.md').read_text()
            self.assertIn('PROTÓTIPO SINTÉTICO',txt,str(p))
            self.assertIn('model_validation_status',p.read_text())

    def test_regression_022_bad_parameter_rejected(self):
        from regression_batch.engine import synthetic_data, partitions, validate_data
        for count in (0, 1, -5, 1.5, None, 100001):
            with self.subTest(n_samples=count), self.assertRaises(ValueError):
                synthetic_data(22, n=count)
        d=synthetic_data(22)
        validate_data(22,d)
        tr,cal,te=partitions(22,d)
        self.assertFalse(set(tr.sample_id) & set(te.sample_id))
        self.assertFalse(set(cal.sample_id) & set(te.sample_id))

    def test_f1_race_probability_sums_and_guards(self):
        p=ROOT/'f1-predictive-intelligence/ml/training/walk_forward_engine.py'
        spec=importlib.util.spec_from_file_location('f1_rules',p)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        cls=m.WalkForwardPredictionEngine
        target={'event_id':'DEMO','snapshot_timestamp_utc':'2026-03-01T00:00:00Z','entries':[{'driver_code':f'D{i}','constructor':f'C{i//2}','grid_pos':i} for i in range(1,21)]}
        result=cls.predict_event_walk_forward([],target,'2026-03-02T00:00:00Z')
        for k,expected in [('win_prob',1),('podium_prob',3),('points_prob',10)]:
            self.assertAlmostEqual(sum(r[k] for r in result['predictions']),expected,places=6)
        for r in result['predictions']:
            self.assertTrue(0<=r['win_prob']<=r['podium_prob']<=r['points_prob']<=1)
            self.assertIn('heuristic_attributions',r)
        with self.assertRaises(ValueError):cls.predict_event_walk_forward([],target,'2026-03-02T00:00:00')
        with self.assertRaises(ValueError):cls.predict_event_walk_forward([],target,'2026-03-02T00:00:00Z',horizon='BAD')
        target['entries'][1]['driver_code']=target['entries'][0]['driver_code']
        with self.assertRaises(ValueError):cls.predict_event_walk_forward([],target,'2026-03-02T00:00:00Z')

    def test_pit_stops_within_bounds(self):
        p=next(ROOT.glob('projetos/**/101-*/main.py'))
        spec=importlib.util.spec_from_file_location('pit',p)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        for laps in (3,6,15,58):
            rows=m.evaluate_pit_strategies(total_laps=laps)
            self.assertTrue(rows)
            for r in rows:
                self.assertTrue(all(1 < i < laps for i in r['pit_laps']))
                self.assertEqual(r['pit_laps'],sorted(set(r['pit_laps'])))
        for invalid in (0,2,-7,2.5):
            with self.assertRaises(ValueError):m.evaluate_pit_strategies(total_laps=invalid)
        with self.assertRaises(ValueError):m.evaluate_pit_strategies(15,-1)

    def test_111_projects_present(self):
        paths=list(ROOT.glob('projetos/**/main.py'));self.assertEqual(len(paths),111)
        self.assertEqual(sorted(int(p.parent.name[:3]) for p in paths),list(range(1,112)))

if __name__=='__main__':unittest.main()
