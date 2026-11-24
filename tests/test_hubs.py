"""Hub scenes (Phase 2): every hub page mounts its scene, data comes from the case studies."""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
HUBS = {"industrial/": "industrial", "automotivo/": "automotivo", "automotivo/f1/": "f1",
        "automotivo/porsche/": "porsche", "laboratorio/": "lab", "sobre/": "sobre"}


class TestHubs(unittest.TestCase):
    def test_each_hub_mounts_its_bundle(self):
        for rel, entry in HUBS.items():
            page = (SITE / rel / "index.html").read_text(encoding="utf-8")
            self.assertIn(f'data-hub="{entry}"', page, rel)
            self.assertIn(f'import("/assets/js/hub-{entry}.js")', page, rel)
            self.assertTrue((SITE / "assets" / "js" / f"hub-{entry}.js").is_file(), entry)

    def test_hub_data_is_regenerated_identically_from_the_metrics(self):
        out = SITE / "assets" / "hubs" / "hub-data.json"
        before = out.read_bytes()
        subprocess.run([sys.executable, str(ROOT / "scripts" / "build_hub_data.py")], check=True, capture_output=True)
        self.assertEqual(before, out.read_bytes())
        data = json.loads(before)
        metrics = json.loads((ROOT / "case_studies" / "reports" / "metrics.json").read_text(encoding="utf-8"))
        self.assertEqual(data["supply"]["on_time_pct"], metrics["supply"]["on_time_pct"])
        self.assertEqual(data["churn"]["positive_rate_train"], metrics["churn"]["positive_rate_train"])
        self.assertEqual(len(data["forecast"]["demand_last_days"]), 140)

    def test_porsche_sliders_respect_the_model_limits(self):
        model = (SITE / "motorsport" / "porsche" / "model.mjs").read_text(encoding="utf-8")
        limits = re.search(r"LIMITS=\{(.*?)\};", model).group(1)
        page = (SITE / "automotivo" / "porsche" / "index.html").read_text(encoding="utf-8")
        for key, html_id in (("speed", "pc-speed"), ("ay", "pc-ay"), ("ax", "pc-ax")):
            lo, hi = re.search(rf"{key}:\[([-\d.]+),([-\d.]+)\]", limits).groups()
            tag = re.search(rf'<input type="range" id="{html_id}"[^>]*>', page).group(0)
            self.assertIn(f'min="{float(lo):g}"', tag.replace(".0\"", "\""))
            self.assertIn(f'max="{float(hi):g}"', tag.replace(".0\"", "\""))

    def test_timeline_runs_oldest_to_newest(self):
        page = (SITE / "sobre" / "index.html").read_text(encoding="utf-8")
        starts = [int(m) for m in re.findall(r'<span class="when">(\d{4})', page)]
        self.assertGreaterEqual(len(starts), 3)
        self.assertEqual(starts, sorted(starts))

    def test_lab_links_point_to_shared_projects(self):
        page = (SITE / "laboratorio" / "index.html").read_text(encoding="utf-8")
        for pid in ("103", "104", "105"):
            self.assertIn(f'href="/cases/motorsport/{pid}/"', page)


if __name__ == "__main__":
    unittest.main()
