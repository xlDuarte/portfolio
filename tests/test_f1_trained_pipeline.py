"""Synthetic F1 model training and data leakage regression suite."""
import importlib.util
import json
import math
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE = ROOT/'f1-predictive-intelligence'/'ml'/'training'/'trained_pipeline.py'
spec = importlib.util.spec_from_file_location('trained_f1',MODULE)
f1=importlib.util.module_from_spec(spec)
spec.loader.exec_module(f1)

class TestF1Trained(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.events = f1.make_synthetic_events()
  cls.target={**cls.events[-1], 'event_id':'TEST_NEXT', 'event_timestamp_utc':'2025-01-01T12:00:00+00:00', 'snapshot_timestamp_utc':'2024-12-31T18:00:00+00:00'}
  cls.cutoff='2024-12-31T20:00:00+00:00'

 def test_all_eight_model_definitions_train(self):
  report=f1.fit_and_evaluate(self.events,self.target,self.cutoff)
  self.assertEqual(set(report['model_results']),set(f1.MODEL_NAMES))
  self.assertTrue(all(z['status']=='EVALUATED' for z in report['model_results'].values()))
  for key,value in report['model_results'].items():
   self.assertGreater(value['training_events'],1)
   self.assertGreater(value['validation_events'],1)
   self.assertTrue(math.isfinite(value['holdout_event_rank_mae']))
  self.assertEqual(len(report['predictions']),12)
  for k,expected in (('win_prob',1),('podium_prob',3),('points_prob',10)):
   self.assertAlmostEqual(sum(z[k] for z in report['predictions']),expected,places=8)
  for row in report['predictions']:
   self.assertLessEqual(row['win_prob'],row['podium_prob'])
   self.assertLessEqual(row['podium_prob'],row['points_prob'])

 def test_future_training_event_rejected(self):
  ev=self.events+[dict(self.events[0],event_id='FUTURE',event_timestamp_utc='2025-02-01T00:00:00+00:00')]
  with self.assertRaisesRegex(ValueError,'look-ahead'):
   f1.fit_and_evaluate(ev,self.target,self.cutoff,models=['Ridge_Regularized'])

 def test_future_target_snapshot_rejected(self):
  with self.assertRaisesRegex(ValueError,'look-ahead'):
   f1.fit_and_evaluate(self.events,{**self.target,'snapshot_timestamp_utc':'2025-01-04T00:00:00Z'},self.cutoff,models=['Ridge_Regularized'])

 def test_invalid_timestamps(self):
  with self.assertRaises(ValueError):f1.timestamp('2024-12-01T00:00:00')

 def test_duplicate_driver_and_missing_results(self):
  dup=self.target['entries'][:]
  dup[1]={**dup[1], 'driver_code':dup[0]['driver_code']}
  with self.assertRaisesRegex(ValueError,'duplicate'):
   f1.fit_and_evaluate(self.events,{**self.target,'entries':dup},self.cutoff,models=['Ridge_Regularized'])
  with self.assertRaisesRegex(ValueError,'results/entries'):
   f1.build_temporal_rows([{**self.events[0],'results':self.events[0]['results'][:-1]}])

 def test_no_current_race_label_leakage(self):
  X=f1.features_for(self.target['entries'],self.events)
  Y=f1.features_for(self.target['entries'],self.events)
  self.assertEqual(X,Y)
  self.assertEqual(len(f1.build_temporal_rows(self.events)),len(self.events)-1)

if __name__=='__main__':unittest.main()
