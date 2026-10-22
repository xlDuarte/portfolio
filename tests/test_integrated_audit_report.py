"""Truth-in-labeling gates for the consolidated, already-merged 111-project tree.

Does not replace runtime, real-data or external validation.
"""
import csv
import unittest
from pathlib import Path
from scripts.audit_integrated_portfolio import build_audit,KNOWN_LIMITS

ROOT=Path(__file__).resolve().parents[1]

class TestIntegratedAuditTruth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=build_audit(ROOT)
        with (ROOT/"TECHNOLOGY_GAP_MATRIX_INTEGRATED.csv").open(newline="",encoding="utf-8") as source:
            cls.matrix={int(row["id"]):row for row in csv.DictReader(source)}

    def test_exactly_111_source_programs_and_gap_rows(self):
        self.assertEqual(self.report["canonical_projects"],111)
        self.assertEqual(self.report["technology_gap_matrix_rows"],111)
        self.assertEqual(len(self.report["projects"]),111)
        self.assertTrue(self.report["all_readmes_present"])
        self.assertEqual(self.report["python_entrypoints_syntax_valid"],111)

    def test_each_domain_has_ten_real_pages_and_workflows(self):
        self.assertEqual(len(self.report["domains"]),8)
        self.assertEqual(self.report["domain_code_packages_present"],8)
        for item in self.report["domains"]:
            with self.subTest(domain=item["domain"]):
                self.assertTrue(item["case_index_present"])
                self.assertEqual(item["individual_site_pages_present"],10)
                self.assertEqual(len(item["project_ids"]),10)

    def test_no_cross_project_technology_attribution(self):
        # Earlier audit rows 101-110 assigned XGBoost, LSTM, Grad-CAM,
        # MLflow, LangChain and SHAP to *every* project: false claim.
        expected={
            101:"XGBRegressor",102:"EKF",103:"Lucas-Kanade",
            104:"LSTM",105:"Grad-CAM",106:"MLflow",
            107:"LangChain",108:"SHAP",109:"Plotly",110:"QSS"}
        for id,token in expected.items():
            with self.subTest(project=id):
                self.assertIn(token.lower(),self.matrix[id]["evidencia_no_codigo"].lower())
        self.assertNotIn("MLflow",self.matrix[102]["evidencia_no_codigo"])
        self.assertNotIn("LSTM",self.matrix[103]["evidencia_no_codigo"])
        self.assertNotIn("Grad-CAM",self.matrix[109]["evidencia_no_codigo"])
        self.assertNotIn("SHAP",self.matrix[110]["evidencia_no_codigo"])

    def test_bi_sklean_claims_are_specific(self):
        # Scikit-learn is really used to fit predictive models #081/#088,
        # not all ten BI projects.
        self.assertIn("RandomForest",self.matrix[81]["evidencia_no_codigo"])
        self.assertIn("Ridge",self.matrix[88]["evidencia_no_codigo"])
        self.assertNotIn("Scikit-learn",self.matrix[87]["evidencia_no_codigo"])
        self.assertIn("não executado",self.matrix[100]["lacunas_nao_comprovadas"])

    def test_project_111_and_production_gaps_are_explicit(self):
        self.assertEqual(self.matrix[111]["status"],"escopo anunciado incompleto")
        self.assertIn("Catálogo ML não treinado",self.matrix[111]["lacunas_nao_comprovadas"])
        self.assertIsNone(self.report["production_maturity_score"])
        self.assertIsNone(self.report["externally_validated_projects"])
        types={r["technology"]:r["status"] for r in KNOWN_LIMITS}
        self.assertEqual(types["Power BI DAX / PBIX/PBIP"],"UNVERIFIED_RUNTIME")
        self.assertEqual(types["F1-PIP model catalogue #111"],"INCOMPLETE")

if __name__=="__main__":
    unittest.main()
