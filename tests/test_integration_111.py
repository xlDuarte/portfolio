"""Structural integration acceptance gates, NOT proof of real-world model performance."""
from pathlib import Path
import re
import unittest
from classification_batch.engine import CONFIG, evaluate_formula
ROOT=Path(__file__).resolve().parents[1]
GROUPS={"classification":(31,40),"nlp":(41,50),"recommendation":(51,60),
        "timeseries":(61,70),"vision":(71,80),"business":(81,90),
        "advanced":(91,100),"motorsport":(101,110)}
class IntegrationInventory(unittest.TestCase):
    def test_all_111_canonical_programs(self):
        paths=list((ROOT/"projetos").glob("**/main.py"))
        numbers=sorted(int(p.parent.name[:3]) for p in paths)
        self.assertEqual(numbers,list(range(1,112)))
        self.assertEqual(len(paths),111)
        for path in paths:
            with self.subTest(case=path.parent.name):
                self.assertTrue((path.parent/"README.md").is_file())
                self.assertGreater((path).stat().st_size,50)
    def test_canonical_classification_entrypoints_really_train(self):
        self.assertEqual(set(CONFIG),set(range(31,41)))
        for id,c in CONFIG.items():
            entry=ROOT/"projetos"/"04-classification"/f"{id:03d}-{c['slug']}"/"main.py"
            source=entry.read_text()
            self.assertIn("from classification_batch.engine import evaluate",source)
            self.assertIn(f"evaluate({id})",source)
            self.assertTrue((ROOT/"site"/"cases"/"classification"/f"{id:03d}"/"index.html").exists())
    def test_no_eval_execution_from_config(self):
        import numpy as np
        # The config parser only accepts features present in RANGES.
        from classification_batch.engine import RANGES
        key="monthly_orders"
        self.assertEqual(float(evaluate_formula(f"2*{key}-3",{key:4.})),5.)
        for expr in ('__import__("os").system("exit 1")','monthly_orders.__class__','1**2','abc'):
            with self.subTest(expr=expr),self.assertRaises(ValueError):
                evaluate_formula(expr,{key:4.})
    def test_8_domain_workflows_and_public_catalogs(self):
        for key,(start,end) in GROUPS.items():
            self.assertTrue((ROOT/"site"/"cases"/key/"index.html").is_file(),key)
            hub=ROOT/"site"/("automotivo" if key=="motorsport" else "industrial")/"index.html"
            self.assertIn(f"/cases/{key}/",hub.read_text(),key)
            self.assertTrue((ROOT/"site"/"cases"/key/f"{start:03d}"/"index.html").is_file(),key)
        for required in ("classification-batch.yml","nlp-batch.yml","recommendation-batch.yml",
                         "timeseries-batch.yml","vision-batch.yml","business-batch.yml",
                         "advanced-batch.yml","motorsport-batch.yml","ci-and-pages.yml"):
            self.assertTrue((ROOT/".github"/"workflows"/required).is_file(),required)
    def test_original_010_and_111_kept_and_not_mislabeled(self):
        a=next((ROOT/"projetos").glob("**/010-*/main.py")).read_text()
        b=next((ROOT/"projetos").glob("**/111-*/main.py")).read_text()
        self.assertIn("supply",a)
        self.assertIn("PLANNED_MODEL_CATALOG_NOT_IMPLEMENTED",b)
    def test_technical_scope_disclosed_in_report(self):
        s=(ROOT/"INTEGRATION_AUDIT.md").read_text()
        for token in ("synthetic","Power BI","SAP","MLflow","XGBoost","111","não é 100/100"):
            self.assertIn(token.lower(),s.lower())
if __name__=="__main__":unittest.main()
