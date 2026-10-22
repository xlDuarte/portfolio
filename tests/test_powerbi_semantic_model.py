"""Offline PBIP structure and independent synthetic KPI fixture checks.
Does not execute DAX Tabular Engine and must not be labeled Desktop certification.
"""
from pathlib import Path
import json, math, unittest
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'powerbi-industrial'

class TestPowerBIArtifacts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.model=json.loads((P/'IndustrialOperations.SemanticModel'/'model.bim').read_text())['model']
  cls.metrics=json.loads((P/'expected_kpis.json').read_text())
 def test_project_paths(self):
  pbip=json.loads((P/'IndustrialOperations.pbip').read_text())
  report=json.loads((P/'IndustrialOperations.Report'/'definition.pbir').read_text())
  self.assertEqual(pbip['artifacts'][0]['report']['path'],'IndustrialOperations.Report')
  self.assertEqual(report['datasetReference']['byPath']['path'],'../IndustrialOperations.SemanticModel')
  self.assertTrue((P/'IndustrialOperations.Report'/'definition'/'pages'/'pages.json').exists())
 def test_star_schema(self):
  tables={t['name']:t for t in self.model['tables']}
  self.assertEqual(len(tables),5)
  self.assertEqual(len(self.model['relationships']),6)
  for rel in self.model['relationships']:
   self.assertIn(rel['fromTable'],tables)
   self.assertIn(rel['toTable'],tables)
   self.assertEqual(rel['crossFilteringBehavior'],'oneDirection')
  self.assertEqual(sum(len(t.get('measures',[])) for t in tables.values()),16)
 def test_reference_kpis_are_well_formed(self):
  self.assertAlmostEqual(self.metrics['oee'],self.metrics['availability']*self.metrics['performance']*self.metrics['quality'])
  self.assertEqual(self.metrics['revenue_brl'],318000)
  self.assertAlmostEqual(self.metrics['otif'],0.75)
  self.assertTrue(all(math.isfinite(v) for v in self.metrics.values()))
 def test_expected_dax_measures(self):
  all_measures={m['name']:m['expression'] for t in self.model['tables'] for m in t.get('measures',[])}
  for name in ('Availability','Performance','Quality','OEE','OTIF Rate','Revenue BRL','Defects PPM'):
   self.assertIn(name,all_measures)
  self.assertIn('SUMX',all_measures['Performance'])
  self.assertIn('FILTER',all_measures['OTIF Orders'])
  self.assertTrue((P/'IndustrialOperations.Report'/'definition'/'pages').exists())
if __name__=='__main__':unittest.main()
