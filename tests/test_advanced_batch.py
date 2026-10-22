"""Integration tests of ten actual synthetic stream/ML/SQL projects."""
from __future__ import annotations
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from advanced_batch import engine as e
from advanced_batch.api import create_app
from advanced_batch.export_bi import export_bi

ROOT=Path(__file__).resolve().parents[1]

class TestAdvancedBatch(unittest.TestCase):
    def test_ten_domains_unique_and_sources(self):
        self.assertEqual(set(e.SPECS),set(range(91,101)))
        self.assertEqual(len({cfg["kind"] for cfg in e.SPECS.values()}),10)
        for project in e.SPECS:
            with self.subTest(project=project):
                events=e.generate(project)
                self.assertEqual(events,e.generate(project))
                self.assertEqual(len(events),96)
                self.assertEqual(len({r["event_id"] for r in events}),96)
                self.assertTrue(all(r["project_id"]==project and r["origin"]=="SYNTHETIC" for r in events))
                self.assertTrue(all(e.validate_event(r) is r for r in events))

    def test_all_ten_workflows_run_real_models_or_rules(self):
        for project in e.SPECS:
            with self.subTest(project=project):
                outcome=e.analyze(project)
                self.assertEqual(outcome["project_id"],project)
                self.assertEqual(outcome["sample_count"],96)
                self.assertFalse(outcome["sap_connected"])
                self.assertFalse(outcome["production_ready"])
                self.assertIn("SYNTHETIC",outcome["status"])
                self.assertTrue(outcome["metrics"])

    def test_domain_specific_invariants(self):
        vendor=e.analyze(91)["metrics"]
        self.assertFalse(vendor["decisions_executed"])
        self.assertTrue(0<=vendor["mean_risk_score"]<=100)
        anomaly=e.analyze(92)["metrics"]
        self.assertEqual(anomaly["historical_train_rows"]+anomaly["unseen_stream_rows"],96)
        self.assertIn("IsolationForest",anomaly["model"])
        skills=e.analyze(93)["metrics"]
        self.assertFalse(skills["staffing_or_hiring_decision_executed"])
        self.assertTrue(all(0<=r["skills_coverage"]<=1 for r in skills["sample_recommendations"]))
        forecast=e.analyze(94)["metrics"]
        self.assertEqual(forecast["untouched_test_weeks"],12)
        self.assertEqual(len(forecast["future_six_week_forecast_units"]),6)
        self.assertFalse(forecast["purchase_order_created"])
        churn=e.analyze(95)["metrics"]
        self.assertEqual(churn["train_contracts"]+churn["untouched_test_contracts"],96)
        self.assertTrue(0<=churn["test_roc_auc"]<=1)
        mes=e.analyze(96)["metrics"]
        self.assertTrue(mes["all_within_bounds"])
        self.assertFalse(mes["actual_mes_commands_sent"])
        rul=e.analyze(97)["metrics"]
        self.assertIn("RandomForestRegressor",rul["model"])
        self.assertGreaterEqual(rul["rul_test_mae_hours"],0)
        documents=e.analyze(98)["metrics"]
        self.assertEqual(documents["train_documents"]+documents["unseen_documents"],96)
        self.assertIn("TF-IDF",documents["model"])
        safety=e.analyze(99)["metrics"]
        self.assertFalse(safety["equipment_shutdown_executed"])
        self.assertGreater(safety["alert_count"],0)
        bi=e.analyze(100)["metrics"]
        self.assertEqual(len(bi["lines"]),3)
        self.assertTrue(0<=bi["weighted_oee_pct"]<=100)
        self.assertFalse(bi["dax_executed"])

    def test_event_schema_checks_and_idempotency(self):
        rows=e.generate(91,24)
        with e.connect() as conn:
            first=e.ingest(conn,rows)
            second=e.ingest(conn,rows)
            self.assertEqual(first["inserted"],24)
            self.assertEqual(second["inserted"],0)
            self.assertEqual(second["deduplicated"],24)
            self.assertEqual(e.read_events(conn,91,100),rows)
            modified=dict(rows[0]);modified["payload"]=dict(rows[0]["payload"])
            modified["payload"]["otif"]=0.01
            with self.assertRaisesRegex(ValueError,"Conflicting"):
                e.ingest(conn,[modified])
            self.assertEqual(len(e.read_events(conn,91)),24)
            invalid=dict(rows[1]);invalid["occurred_at"]="2025-01-01T00:00:00"
            with self.assertRaises(ValueError):e.ingest(conn,[invalid])

    def test_fastapi_real_database_roundtrip_and_validation(self):
        with tempfile.TemporaryDirectory() as folder:
            path=str(Path(folder)/"demo.sqlite3")
            with TestClient(create_app(path)) as client:
                self.assertEqual(client.get("/health").status_code,200)
                self.assertEqual(len(client.get("/v1/projects").json()),10)
                self.assertEqual(client.get("/v1/projects/92/analytics").status_code,409)
                r=client.post("/v1/projects/92/simulate",params={"count":48})
                self.assertEqual(r.status_code,200,r.text)
                self.assertEqual(r.json()["inserted"],48)
                again=client.post("/v1/projects/92/simulate",params={"count":48})
                self.assertEqual(again.json()["deduplicated"],48)
                self.assertEqual(client.get("/v1/projects/92/events").json()["count"],48)
                computed=client.get("/v1/projects/92/analytics")
                self.assertEqual(computed.status_code,200,computed.text)
                self.assertEqual(computed.json()["sample_count"],48)
                self.assertIn("IsolationForest",computed.json()["metrics"]["model"])
                self.assertEqual(client.post("/v1/projects/101/simulate").status_code,404)
                self.assertEqual(client.post("/v1/projects/91/simulate",params={"count":0}).status_code,422)
                bad=e.generate(91,24)[0];bad["origin"]="REAL_SENSOR"
                res=client.post("/v1/projects/91/ingest",json={"events":[bad]})
                self.assertEqual(res.status_code,409)

    def test_sql_bi_and_powerbi_export(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"bi.csv"
            exported=export_bi(path,count=36)
            self.assertEqual(exported["rows"],36)
            self.assertIn("good_ideal_min",path.read_text())
            self.assertEqual(len(path.read_text().splitlines()),37)
            self.assertIn("DIVIDE",(ROOT/"advanced_batch"/"powerbi"/"Measures.dax").read_text())

    def test_cli_scripts_site_and_documentation(self):
        for project,cfg in e.SPECS.items():
            folder=ROOT/"projetos"/"10-advanced"/cfg["slug"]
            with self.subTest(project=project):
                self.assertTrue((folder/"main.py").is_file())
                self.assertIn("advanced_batch.engine",(folder/"main.py").read_text())
                self.assertTrue((folder/"README.md").is_file())
                page=ROOT/"site"/"cases"/"advanced"/f"{project:03d}"/"index.html"
                self.assertTrue(page.is_file())
        self.assertTrue((ROOT/"site"/"cases"/"advanced"/"index.html").is_file())
        self.assertIn("/cases/advanced/",(ROOT/"site"/"docs"/"index.html").read_text())
        p=ROOT/"projetos"/"10-advanced"/e.SPECS[100]["slug"]/"main.py"
        completed=subprocess.run([sys.executable,str(p)],capture_output=True,text=True,
                                 check=True,timeout=30)
        self.assertEqual(json.loads(completed.stdout)["project_id"],100)

if __name__=="__main__":unittest.main()
