"""Business/finance integration tests on deterministic artificial ERP-like tables."""
from __future__ import annotations
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd

from business_batch import engine as b
ROOT=Path(__file__).resolve().parents[1]

class TestBusinessFinanceBatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables=b.fixtures()
    def test_configuration_and_sql_for_every_project(self):
        self.assertEqual(set(b.CONFIG),set(range(81,91)))
        self.assertEqual(len({x["slug"] for x in b.CONFIG.values()}),10)
        with b.open_sqlite(self.tables) as conn:
            for p in b.CONFIG:
                with self.subTest(project=p):
                    self.assertTrue((ROOT/"business_batch"/"sql"/f"{p:03d}.sql").exists())
                    sql=b.sql_frame(p,conn)
                    self.assertFalse(sql.empty)
                    self.assertGreater(len(sql.columns),1)

    def test_deterministic_tables_fk_and_integrity(self):
        other=b.fixtures()
        self.assertEqual(set(other),set(self.tables))
        for key in self.tables:
            with self.subTest(table=key):
                pd.testing.assert_frame_equal(self.tables[key],other[key])
        b.validate_tables(self.tables)
        corrupt={key:v.copy() for key,v in self.tables.items()}
        corrupt["fact_invoices"].loc[0,"customer_id"]="MISSING"
        with self.assertRaisesRegex(ValueError,"Orphan"):
            b.validate_tables(corrupt)
        bad={key:v.copy() for key,v in self.tables.items()}
        bad["fact_shifts"].loc[0,"good_units"]=99999
        with self.assertRaisesRegex(ValueError,"Impossible"):
            b.validate_tables(bad)

    def test_all_ten_domain_outcomes(self):
        for p in b.CONFIG:
            with self.subTest(project=p):
                report=b.evaluate(p,self.tables)
                self.assertEqual(report["project_id"],p)
                self.assertTrue(report["sql_result_rows"]>0)
                self.assertIn("SQLite3",report["sql_engine"])
                self.assertFalse(report["production_ready"])
                self.assertFalse(report["sap_ariba_connected"])
                self.assertFalse(report["power_bi_dax_executed"])
                self.assertIn("SYNTHETIC",report["data_origin"])
                self.assertEqual(report,b.evaluate(p,self.tables))
                self.assertTrue(report["metrics"])

    def test_081_ltv_fits_and_retains_unseen_accounts(self):
        m=b.evaluate(81,self.tables)["metrics"]
        self.assertIn("RandomForestRegressor",m["model"])
        self.assertEqual(m["train_accounts"]+m["test_accounts"],180)
        self.assertEqual(m["test_accounts"],45)
        self.assertGreater(m["baseline_test_mae_brl"],m["test_mae_brl"])
        self.assertEqual(len(m["predictions"]),12)
        self.assertEqual(len({x["customer_id"] for x in m["predictions"]}),12)
        self.assertGreaterEqual(m["test_mae_brl"],0)

    def test_082_weighted_oee_and_quotas(self):
        m=b.evaluate(82,self.tables)["metrics"]
        d=self.tables["fact_shifts"]
        expected=100*float((d.good_units*d.ideal_cycle_min).sum()/d.planned_min.sum())
        self.assertAlmostEqual(m["weighted_oee_pct"],expected,places=3)
        self.assertAlmostEqual(m["weighted_oee_pct"],
                               m["availability_pct"]*m["performance_pct"]*m["quality_pct"]/10000,places=1)
        self.assertTrue(0<=m["weighted_oee_pct"]<=100)
        self.assertEqual(len(m["lines"]),3)

    def test_083_randomized_synthetic_campaign(self):
        m=b.evaluate(83,self.tables)["metrics"]
        self.assertEqual(m["treated_n"]+m["control_n"],600)
        self.assertGreater(m["observed_margin_lift_brl"],30)
        self.assertTrue(m["randomized_in_fixture"])
        self.assertGreater(m["campaign_spend_brl"],0)
        self.assertGreater(m["estimated_incremental_margin_brl"],0)

    def test_084_abc_and_rfm_balances(self):
        m=b.evaluate(84,self.tables)["metrics"]
        self.assertEqual(sum(m["abc_counts"].values()),m["accounts"])
        self.assertAlmostEqual(m["revenue_total_brl"],
                               float(self.tables["fact_invoices"].amount_brl.sum()),places=1)
        for account in m["top_accounts"]:
            self.assertEqual(len(account["rfm"]),3)
            self.assertTrue(all(char in "12345" for char in account["rfm"]))
            self.assertIn(account["abc"],("A","B","C"))

    def test_085_payment_audit_flags_are_review_not_fraud(self):
        m=b.evaluate(85,self.tables)["metrics"]
        self.assertEqual(m["payments_checked"],320)
        self.assertGreaterEqual(m["flag_types"]["duplicate_ref"],2)
        self.assertGreater(m["flag_types"]["possible_split"],0)
        self.assertGreater(m["flagged_payments"],0)
        self.assertIn("not fraud",m["disclaimer"].lower())

    def test_086_risk_heatmap_complete(self):
        m=b.evaluate(86,self.tables)["metrics"]
        self.assertEqual(len(m["matrix_5x5"]),5)
        self.assertEqual(sum(map(sum,m["matrix_5x5"])),130)
        self.assertEqual(m["events"],130)
        self.assertTrue(0<=m["critical_share_pct"]<=100)
        self.assertTrue(m["not_observed_incidents"])

    def test_087_capex_knapsack_feasibility_and_objective(self):
        m=b.evaluate(87,self.tables)["metrics"]
        self.assertLessEqual(m["selected_capex_k_brl"],m["budget_k_brl"])
        self.assertAlmostEqual(m["remaining_budget_k_brl"],
                               m["budget_k_brl"]-m["selected_capex_k_brl"],places=1)
        self.assertGreaterEqual(m["selected_npv_k_brl"],0)
        self.assertEqual(len(set(m["selected_project_ids"])),len(m["selected_project_ids"]))
        with self.assertRaises(ValueError):
            b._capex(self.tables["fact_capex"],budget_k_brl=-100)

    def test_088_billing_reconciliation_temporal_forecast(self):
        m=b.evaluate(88,self.tables)["metrics"]
        self.assertEqual(m["months"],36)
        self.assertEqual(m["reconciliation_mismatches"],2)
        self.assertEqual((m["temporal_train_months"],m["untouched_test_months"]),(30,6))
        self.assertGreater(m["absolute_unreconciled_brl"],0)
        self.assertEqual(len(m["future_months"]),3)
        self.assertEqual(len(m["future_net_revenue_forecast_brl"]),3)
        self.assertFalse(m["future_actuals_available"])

    def test_089_supplier_spend_and_delivery(self):
        m=b.evaluate(89,self.tables)["metrics"]
        self.assertEqual(m["purchase_orders"],480)
        self.assertAlmostEqual(m["total_spend_brl"],float(self.tables["fact_procurement"].spend_brl.sum()),places=1)
        self.assertTrue(0<m["supplier_hhi"]<1)
        self.assertTrue(0<=m["on_time_delivery_pct"]<=100)
        self.assertAlmostEqual(sum(x["spend_brl"] for x in m["category_spend"]),m["total_spend_brl"],places=1)

    def test_090_cost_drivers_and_tariffs(self):
        m=b.evaluate(90,self.tables)["metrics"]
        self.assertEqual(m["batches"],300)
        self.assertAlmostEqual(m["weighted_unit_cost_brl"],
                               m["total_manufacturing_cost_brl"]/m["manufactured_units"],places=2)
        self.assertGreater(m["energy_cost_brl"],0)
        self.assertGreater(m["overtime_cost_brl"],0)
        self.assertEqual(len(m["line_summary"]),3)

    def test_export_every_domain_json_csv_png_and_powerbi_tables(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(b,"ROOT",Path(tmp)):
                (Path(tmp)/"sql").mkdir()
                for id in b.CONFIG:
                    original=(ROOT/"business_batch"/"sql"/f"{id:03d}.sql").read_text()
                    (Path(tmp)/"sql"/f"{id:03d}.sql").write_text(original)
                for p in b.CONFIG:
                    output=b.evaluate(p,self.tables,save=True)
                    self.assertTrue((Path(tmp)/"reports"/f"{p:03d}.json").is_file())
                    self.assertTrue((Path(tmp)/"exports"/f"{p:03d}_query.csv").is_file())
                    self.assertTrue((Path(tmp)/"figures"/f"{p:03d}.png").is_file())
                    self.assertEqual(json.loads((Path(tmp)/"reports"/f"{p:03d}.json").read_text()),output)
                self.assertEqual(len(list((Path(tmp)/"exports"/"raw").glob("*.csv"))),11)
                self.assertGreater((Path(tmp)/"figures"/"086.png").stat().st_size,1000)

    def test_powerbi_artifacts_and_ten_site_cards(self):
        powerbi=ROOT/"business_batch"/"powerbi"
        self.assertIn("SUMX(Fact_Shifts",(powerbi/"Measures.dax").read_text())
        self.assertIn("File.Contents",(powerbi/"CsvTable.pq").read_text())
        self.assertIn("Power BI Desktop",(powerbi/"README.md").read_text())
        self.assertEqual(len(list(powerbi.glob("Fact_*.pq"))),10)
        self.assertTrue((powerbi/"Dim_Customers.pq").is_file())
        for id,cfg in b.CONFIG.items():
            folder=ROOT/"projetos"/"09-business"/cfg["slug"]
            self.assertTrue((folder/"main.py").is_file())
            self.assertTrue((folder/"README.md").is_file())
            self.assertIn("business_batch.engine",(folder/"main.py").read_text())
            self.assertTrue((ROOT/"site"/"cases"/"business"/f"{id:03d}"/"index.html").is_file())
        self.assertTrue((ROOT/"site"/"cases"/"business"/"index.html").is_file())
        self.assertIn("/cases/business/",(ROOT/"site"/"industrial"/"index.html").read_text())

    def test_entrypoint_and_interactive_dashboard(self):
        p=ROOT/"projetos"/"09-business"/b.CONFIG[82]["slug"]/"main.py"
        process=subprocess.run([sys.executable,str(p)],capture_output=True,text=True,check=True,timeout=30)
        self.assertEqual(json.loads(process.stdout)["project_id"],82)
        self.assertIn("run_app",(ROOT/"business_batch"/"app.py").read_text())

if __name__=="__main__":unittest.main()
