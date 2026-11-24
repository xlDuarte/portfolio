"""Home hero prototype: the payload must stay faithful to the repository data."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERO = ROOT / "site" / "assets" / "hero"


class TestHeroData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before = (HERO / "hero-data.json").read_bytes()
        subprocess.run([sys.executable, str(ROOT / "scripts" / "build_hero_data.py")], check=True, capture_output=True)
        cls.data = json.loads((HERO / "hero-data.json").read_text(encoding="utf-8"))

    def test_regeneration_is_deterministic(self):
        self.assertEqual(self.before, (HERO / "hero-data.json").read_bytes())

    def test_oee_matches_case_study(self):
        metrics = json.loads((ROOT / "case_studies" / "reports" / "metrics.json").read_text(encoding="utf-8"))
        self.assertAlmostEqual(self.data["industrial"]["oee_weighted"] * 100, metrics["oee"]["oee_weighted_pct"], places=1)
        self.assertEqual(self.data["industrial"]["origin"], "synthetic")

    def test_f1_replay_is_observed_and_complete(self):
        f1 = self.data["f1"]
        self.assertEqual(f1["origin"], "observed")
        self.assertEqual([c["code"] for c in f1["cars"]], ["VER", "PER", "SAI"])
        for car in f1["cars"]:
            self.assertEqual(len(car["samples"]), 240 * f1["sample_hz"])
        self.assertEqual(len(f1["track"]["points"]), 360)

    def test_assets_and_prototype_page(self):
        for name in ("hero.js", "hero.css", "hero-fallback.svg"):
            self.assertTrue((HERO / name).is_file(), name)
        page = (ROOT / "site" / "prototipos" / "heroi" / "index.html").read_text(encoding="utf-8")
        self.assertIn('name="robots" content="noindex"', page)
        self.assertIn('import("/assets/hero/hero.js")', page)
        self.assertNotIn("/prototipos/", (ROOT / "site" / "sitemap.xml").read_text(encoding="utf-8"))

    def test_caption_states_the_display_exaggeration_used_in_code(self):
        import re
        code = (ROOT / "frontend" / "hero" / "main.js").read_text(encoding="utf-8")
        factor = re.search(r"elevation:\s*(\d+),", code).group(1)
        page = (ROOT / "site" / "prototipos" / "heroi" / "index.html").read_text(encoding="utf-8")
        self.assertIn(f"exagerado <span data-elevation>{factor}</span> vezes", page)


if __name__ == "__main__":
    unittest.main()
