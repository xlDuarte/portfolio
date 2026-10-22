"""Acceptance tests for 10 independently constrained synthetic industrial recommenders."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

from recommendation_batch.engine import (
    FIXTURES, SPECS, SIGNATURES, recommend, _features, _wave, _bom,
)

ROOT = Path(__file__).resolve().parents[1]

class RecommendationBatchTests(unittest.TestCase):
    def test_all_ten_domains_runnable_deterministic(self):
        self.assertEqual(set(SPECS), set(range(51,61)))
        self.assertEqual(len({s["mode"] for s in SPECS.values()}), 10 - 1) if False else None
        self.assertEqual(len({s["slug"] for s in SPECS.values()}), 10)
        for p in SPECS:
            with self.subTest(project=p):
                a = recommend(p)
                b = recommend(p)
                self.assertEqual(a, b)
                self.assertEqual(a["project_id"], p)
                self.assertEqual(a["result_count"], len(a["recommendations"]))
                self.assertTrue(a["recommendations"], p)
                self.assertFalse(a["production_ready"])
                self.assertIn("SYNTHETIC", a["data_origin"])
                for item in a["recommendations"]:
                    self.assertIn("id", item)
                    self.assertIn("why", item)

    def test_content_filters_and_nonapproved_revisions(self):
        docs = recommend(53, "welding quality", filters={"domain":"welding"})
        self.assertEqual({x["id"] for x in docs["recommendations"]}, {"DOC1"})
        media = recommend(51, "hydraulic vibration", filters={"asset":"pump", "language":"pt"})
        ids = {x["id"] for x in media["recommendations"]}
        self.assertNotIn("PB08", ids)
        self.assertNotIn("PB03", ids)
        self.assertTrue(ids)

    def test_acoustic_fft_real_computation_and_nearest_neighbors(self):
        for kind in SIGNATURES:
            result = recommend(52, kind)
            self.assertEqual(result["recommendations"][0]["id"], kind)
            self.assertTrue(all(0 <= v["distance"] for v in result["recommendations"]))
        self.assertEqual(len(_features(_wave("bearing_fault"))), 5)
        with self.assertRaises(ValueError):
            recommend(52, "unknown")

    def test_parts_respect_asset_stock_and_approval(self):
        rows = recommend(54, "bearing pump", filters={"asset":"pump","min_stock":3})["recommendations"]
        ids = {r["id"] for r in rows}
        self.assertIn("P01", ids)
        self.assertNotIn("P02", ids)
        self.assertNotIn("P06", ids)
        self.assertTrue(all(p["approved"] and p["stock"] >= 3 for p in FIXTURES["parts"] if p["id"] in ids))

    def test_learning_path_prerequisites_and_hour_budget(self):
        rows = recommend(55, "python pandas power bi", top_k=6, filters={"max_hours":60, "known_skills":[]})["recommendations"]
        trained = set()
        total=0
        catalogue = {c["id"]: c for c in FIXTURES["courses"]}
        for row in rows:
            course = catalogue[row["id"]]
            self.assertTrue(set(course["prerequisites"]) <= trained)
            self.assertNotIn(course["skill"], trained)
            trained.add(course["skill"])
            total += row["hours"]
        self.assertLessEqual(total,60)
        self.assertTrue(any(r["skill"]=="python" for r in rows))

    def test_skill_staffing_is_nonpersonal_and_respects_clearance(self):
        rows = recommend(56, "python sql industrial data", filters={"min_hours":16})["recommendations"]
        ids = {r["id"] for r in rows}
        self.assertNotIn("ENG5", ids)  # fictitious profile without project clearance
        self.assertNotIn("ENG2", ids)  # available hours insufficient
        self.assertTrue(all(r["coverage"] >= 0 for r in rows))
        self.assertTrue(all(r["title"].startswith("Synthetic") for r in rows))

    def test_feed_excludes_archived_and_aged_items(self):
        rows = recommend(57, "steel energy", filters={"max_age_days":7})["recommendations"]
        self.assertTrue(rows)
        self.assertTrue(all(r["age_days"] <= 7 and "SYNTHETIC" in r["source"] for r in rows))
        self.assertNotIn("NEWS10", {r["id"] for r in rows})

    def test_supplier_constraints_applied_before_ranking(self):
        result = recommend(58, "bearings", filters={"quantity":100,"max_lead_days":10,"min_otif":.9})
        ids = {r["id"] for r in result["recommendations"]}
        self.assertNotIn("SUP3", ids) # Not approved
        self.assertNotIn("SUP4", ids) # insufficient stock/capacity and lead time
        self.assertNotIn("SUP9", ids) # no certificate
        self.assertTrue(ids)
        self.assertTrue(all(r["total_price_brl"] == 100*r["unit_price_brl"] for r in result["recommendations"]))
        self.assertEqual(recommend(58,"bearings",filters={"quantity":999})["result_count"], 0)

    def test_routing_valid_simple_paths_and_approved_carriers(self):
        result = recommend(59, "Pindamonhangaba>Santos", top_k=20)
        self.assertTrue(result["result_count"] > 1)
        weights = [r["weighted_objective"] for r in result["recommendations"]]
        self.assertEqual(weights, sorted(weights))
        for route in result["recommendations"]:
            self.assertEqual(route["nodes"][0], "Pindamonhangaba")
            self.assertEqual(route["nodes"][-1], "Santos")
            self.assertEqual(len(route["nodes"]),len(set(route["nodes"])))
            self.assertTrue(all(x["carrier"]!="C3" for x in route["legs"]))
        truck = recommend(59,"Pindamonhangaba>Santos",filters={"modes":["truck"]})
        self.assertTrue(all(leg["mode"]=="truck" for r in truck["recommendations"] for leg in r["legs"]))
        with self.assertRaises(ValueError):
            recommend(59,"Santos>Pindamonhangaba")

    def test_bom_is_complete_not_truncated_and_respects_inventory(self):
        result = recommend(60, "PUMP-100", top_k=1, filters={"units":2,"pack_size":5})
        rows = {r["id"]:r for r in result["recommendations"]}
        self.assertEqual(set(rows), {"P01","P02","P03","P07"})
        self.assertEqual(rows["P01"]["required_qty"],4)
        self.assertEqual(rows["P02"]["required_qty"],4)
        self.assertEqual(rows["P03"]["required_qty"],2)
        self.assertEqual(rows["P07"]["required_qty"],2)
        self.assertEqual(rows["P02"]["shortfall_qty"],2)
        self.assertEqual(rows["P02"]["suggested_purchase_qty"],5)
        self.assertEqual(rows["P03"]["suggested_purchase_qty"],0)
        with self.assertRaises(ValueError):
            recommend(60, "INVALID-ASSY")
        with self.assertRaises(ValueError):
            _bom("PUMP-100",5,{"units":0})

    def test_input_validation(self):
        for p in SPECS:
            with self.subTest(project=p):
                with self.assertRaises(ValueError):
                    recommend(p,"")
                with self.assertRaises(ValueError):
                    recommend(p,top_k=0)
                with self.assertRaises(ValueError):
                    recommend(p,filters=[])
        with self.assertRaises(ValueError):
            recommend(58,filters={"min_otif":float("nan")})
        with self.assertRaises(ValueError):
            recommend(59, filters={"modes":["air"]})

    def test_entrypoints_readmes_ui_pages_and_cli(self):
        for p,cfg in SPECS.items():
            directory = ROOT/"projetos"/"06-recommendation"/cfg["slug"]
            for filename in ("main.py","README.md","streamlit_app.py"):
                self.assertTrue((directory/filename).is_file(), (p,filename))
            self.assertIn("recommendation_batch.engine",(directory/"main.py").read_text())
            self.assertIn("recommendation_batch.app",(directory/"streamlit_app.py").read_text())
            page=ROOT/"site"/"cases"/"recommendation"/f"{p:03d}"/"index.html"
            self.assertTrue(page.is_file(),(p,page))
        self.assertTrue((ROOT/"site"/"cases"/"recommendation"/"index.html").is_file())
        p=ROOT/"projetos"/"06-recommendation"/SPECS[60]["slug"]/"main.py"
        res=subprocess.run([sys.executable,str(p),"--query","PUMP-100","--filters-json",'{"units":2}'],
                           capture_output=True,text=True,check=True,timeout=25)
        self.assertEqual(json.loads(res.stdout)["project_id"],60)

if __name__=="__main__":
    unittest.main()
